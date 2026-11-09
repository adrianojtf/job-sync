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
        texto = self._solicitar(
            "Descrição de uma experiência profissional "
            f"(cargo: {experiencia.cargo or 'não informado'}; "
            f"empresa: {experiencia.empresa or 'não informada'}). "
            "Reescreva somente a descrição, sem repetir cargo, empresa ou período:\n"
            f"{experiencia.descricao}",
            refino,
        )
        return replace(experiencia, descricao=texto)

    def _solicitar(self, prompt_usuario: str, refino: PedidoRefino) -> str:
        resposta = self._cliente_openai.solicitar_json(
            prompt_sistema=_PROMPT_SISTEMA,
            prompt_usuario=f"{prompt_usuario}\n\n{bloco_refino(refino, com_vaga=False)}",
        )
        texto = resposta.get("texto_sugerido")
        if not isinstance(texto, str) or not texto.strip():
            raise ValueError("O modelo não retornou um texto sugerido.")
        return texto.strip()
