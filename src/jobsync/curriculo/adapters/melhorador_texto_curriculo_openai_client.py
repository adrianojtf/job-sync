"""Adapter OpenAI que melhora a escrita de um trecho do currículo, sem vaga-alvo."""
from __future__ import annotations

from dataclasses import replace

from jobsync.curriculo.adapters.prompt_refino import bloco_refino
from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.curriculo import SecaoCurriculo
from jobsync.curriculo.domain.melhorador_texto_curriculo_port import MelhoradorTextoCurriculoPort
from jobsync.curriculo.domain.refino import PedidoRefino
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI

_PROMPT_SISTEMA = """\
Você melhora a escrita de trechos de currículo: clareza, objetividade e verbos de ação.
Mantenha o mesmo idioma do texto original. Preserve todos os fatos e não invente
responsabilidades, tecnologias, resultados, métricas, empresas ou datas.
Mantenha a estrutura em linhas e preserve os marcadores que começam com "-".
Responda somente em JSON no formato:
{"texto_sugerido": "texto reescrito"}
"""

_ERRO_BLOCOS = "O modelo devolveu os blocos da experiência fora do formato esperado."

_PROMPT_SISTEMA_BLOCOS = """\
Você melhora a escrita dos quatro blocos de uma experiência profissional de um currículo, sem vaga-alvo.
Responda somente em JSON no formato:
{"contexto": "parágrafo", "responsabilidades": ["..."], "conquistas": ["..."], "skills": ["..."]}

Regras:
- Mantenha o idioma e os fatos do texto; não invente empresas, datas nem tecnologias que não estejam nele.
- Contexto: de 1 a 3 frases. Responsabilidades e conquistas: de 3 a 5 frases curtas, cada uma com verbo de ação;
  nas conquistas, cite o resultado medido quando houver dado. Quando não houver número, você pode propor
  métricas plausíveis e conservadoras.
- Skills: as tecnologias e competências do texto, sem repetição.
- Não repita cargo, empresa nem período.
"""


class MelhoradorTextoCurriculoOpenAIClient(MelhoradorTextoCurriculoPort):
    """Reescreve um trecho do currículo sem adaptá-lo a uma vaga."""

    def __init__(self, cliente_openai: ClienteOpenAI | None = None) -> None:
        self._cliente_openai = cliente_openai or ClienteOpenAI()

    def melhorar_secao(self, secao: SecaoCurriculo, refino: PedidoRefino) -> SecaoCurriculo:
        texto = self._solicitar(f"Seção do currículo ({secao.titulo}):\n{secao.conteudo}", refino)
        return secao.com_novo_conteudo(texto)

    def melhorar_experiencia(
        self, experiencia: ExperienciaParaAvaliacao, refino: PedidoRefino
    ) -> ExperienciaParaAvaliacao:
        if experiencia.tem_blocos:
            return self._melhorar_blocos(experiencia, refino)
        texto = self._solicitar(
            "Descrição de uma experiência profissional "
            f"(cargo: {experiencia.cargo or 'não informado'}; "
            f"empresa: {experiencia.empresa or 'não informada'}). "
            "Reescreva somente a descrição, sem repetir cargo, empresa ou período:\n"
            f"{experiencia.descricao}",
            refino,
        )
        return replace(experiencia, descricao=texto)

    def _melhorar_blocos(
        self, experiencia: ExperienciaParaAvaliacao, refino: PedidoRefino
    ) -> ExperienciaParaAvaliacao:
        resposta = self._cliente_openai.solicitar_json(
            prompt_sistema=_PROMPT_SISTEMA_BLOCOS,
            prompt_usuario=(
                "Experiência profissional "
                f"(cargo: {experiencia.cargo or 'não informado'}; "
                f"empresa: {experiencia.empresa or 'não informada'}):\n"
                f"- Contexto: {experiencia.contexto.strip() or '(nenhum)'}\n"
                "- Responsabilidades:\n"
                f"{self._lista(experiencia.responsabilidades)}\n"
                "- Conquistas:\n"
                f"{self._lista(experiencia.conquistas)}\n"
                f"- Skills: {', '.join(experiencia.skills) or '(nenhuma)'}\n\n"
                f"{bloco_refino(refino, com_vaga=False)}"
            ),
        )
        return replace(
            experiencia,
            contexto=self._texto(resposta, "contexto"),
            responsabilidades=self._itens(resposta, "responsabilidades"),
            conquistas=self._itens(resposta, "conquistas"),
            skills=self._itens(resposta, "skills"),
        )

    @staticmethod
    def _lista(itens: tuple[str, ...]) -> str:
        return "\n".join(f"  - {item}" for item in itens) or "  (nenhuma)"

    @staticmethod
    def _texto(resposta: dict, chave: str) -> str:
        valor = resposta.get(chave, "")
        if not isinstance(valor, str):
            raise ValueError(_ERRO_BLOCOS)
        return valor.strip()

    @staticmethod
    def _itens(resposta: dict, chave: str) -> tuple[str, ...]:
        itens = resposta.get(chave, [])
        if not isinstance(itens, list) or not all(isinstance(item, str) and item.strip() for item in itens):
            raise ValueError(_ERRO_BLOCOS)
        return tuple(item.strip() for item in itens)

    def _solicitar(self, prompt_usuario: str, refino: PedidoRefino) -> str:
        resposta = self._cliente_openai.solicitar_json(
            prompt_sistema=_PROMPT_SISTEMA,
            prompt_usuario=f"{prompt_usuario}\n\n{bloco_refino(refino, com_vaga=False)}",
        )
        texto = resposta.get("texto_sugerido")
        if not isinstance(texto, str) or not texto.strip():
            raise ValueError("O modelo não retornou um texto sugerido.")
        return texto.strip()
