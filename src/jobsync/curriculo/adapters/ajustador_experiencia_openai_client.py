"""Adapter OpenAI para adaptar uma experiência profissional por vez, em conquistas e contexto."""
from __future__ import annotations

from jobsync.curriculo.domain.ajustador_experiencia_port import AjustadorExperienciaPort
from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.experiencia_adaptada import ExperienciaAdaptada
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI
from jobsync.vaga.domain.analise_vaga import AnaliseVaga, TipoRequisitoTecnico

_NOME_IDIOMA = {
    "pt": "português do Brasil",
    "en": "inglês (formato americano de currículo)",
}

_ERRO_FORMATO = "O modelo devolveu conquistas e contexto fora do formato esperado."

_PROMPT_SISTEMA = """\
Você adapta experiências profissionais de um currículo para uma vaga específica, no padrão
de conquistas e contexto. Responda somente em JSON no formato:
{"conquistas": ["conquista 1", "conquista 2"], "contexto": "parágrafo de contexto"}

Regras:
- Conquistas: de 2 a 6 frases curtas, no idioma de saída, cada uma começando com verbo de ação
  e, quando houver dado, citando o resultado medido.
- Prefira sempre os números e fatos da descrição original. Quando ela não trouxer número,
  você pode propor métricas e volumes plausíveis e conservadores.
- Contexto: de 1 a 3 frases sobre a empresa, a área e o papel, sem repetir as conquistas.
- Destaque o que é mais relevante para a vaga, sem inventar tecnologias, empresas ou datas.
- Não altere cargo, empresa nem período e não os repita no texto de saída.
"""


class AjustadorExperienciaOpenAIClient(AjustadorExperienciaPort):
    """Escreve uma experiência em conquistas e contexto sem alterar seus metadados."""

    def __init__(self, cliente_openai: ClienteOpenAI | None = None) -> None:
        self._cliente_openai = cliente_openai or ClienteOpenAI()

    def ajustar(
        self,
        experiencia: ExperienciaParaAvaliacao,
        descricao_vaga: str,
        idioma_alvo: str,
        analise_vaga: AnaliseVaga,
    ) -> ExperienciaAdaptada:
        if not experiencia.descricao.strip():
            return self._sem_conteudo(experiencia)

        return self._solicitar(
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
            texto_da_experiencia=f"- Descrição original: {experiencia.descricao}",
            descricao_vaga=descricao_vaga,
            idioma_alvo=idioma_alvo,
            analise_vaga=analise_vaga,
        )

    def refinar(
        self,
        experiencia: ExperienciaAdaptada,
        descricao_vaga: str,
        idioma_alvo: str,
        analise_vaga: AnaliseVaga,
    ) -> ExperienciaAdaptada:
        conquistas_atuais = "\n".join(f"- {conquista}" for conquista in experiencia.conquistas)
        return self._solicitar(
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
            texto_da_experiencia=(
                "- Conquistas atuais (reescreva a partir delas):\n"
                f"{conquistas_atuais or '(nenhuma)'}\n"
                f"- Contexto atual: {experiencia.contexto.strip() or '(nenhum)'}"
            ),
            descricao_vaga=descricao_vaga,
            idioma_alvo=idioma_alvo,
            analise_vaga=analise_vaga,
        )

    @staticmethod
    def _sem_conteudo(experiencia: ExperienciaParaAvaliacao) -> ExperienciaAdaptada:
        """Sem texto de origem, não há o que adaptar sem inventar a experiência inteira."""
        return ExperienciaAdaptada(
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
            conquistas=(),
        )

    def _solicitar(
        self,
        cargo: str,
        empresa: str,
        periodo: str,
        texto_da_experiencia: str,
        descricao_vaga: str,
        idioma_alvo: str,
        analise_vaga: AnaliseVaga,
    ) -> ExperienciaAdaptada:
        resposta = self._cliente_openai.solicitar_json(
            prompt_sistema=_PROMPT_SISTEMA,
            prompt_usuario=(
                "Experiência profissional:\n"
                f"- Cargo: {cargo or 'não informado'}\n"
                f"- Empresa: {empresa or 'não informada'}\n"
                f"- Período: {periodo or 'não informado'}\n"
                f"{texto_da_experiencia}\n\n"
                f"Descrição da vaga-alvo:\n{descricao_vaga}\n\n"
                f"{self._requisitos(analise_vaga)}\n\n"
                f"Idioma de saída obrigatório: {_NOME_IDIOMA.get(idioma_alvo, idioma_alvo)}"
            ),
        )
        return ExperienciaAdaptada(
            cargo=cargo,
            empresa=empresa,
            periodo=periodo,
            conquistas=self._conquistas(resposta),
            contexto=self._contexto(resposta),
        )

    @staticmethod
    def _requisitos(analise_vaga: AnaliseVaga) -> str:
        def nomes(tipo: TipoRequisitoTecnico) -> str:
            return ", ".join(r.nome for r in analise_vaga.requisitos if r.tipo == tipo) or "nenhum"

        return (
            f"Requisitos explícitos da vaga: {nomes(TipoRequisitoTecnico.EXPLICITO)}\n"
            f"Requisitos implícitos da vaga: {nomes(TipoRequisitoTecnico.IMPLICITO)}"
        )

    @staticmethod
    def _conquistas(resposta: dict) -> tuple[str, ...]:
        conquistas = resposta.get("conquistas")
        if (
            not isinstance(conquistas, list)
            or not conquistas
            or not all(isinstance(c, str) and c.strip() for c in conquistas)
        ):
            raise ValueError(_ERRO_FORMATO)
        return tuple(c.strip() for c in conquistas)

    @staticmethod
    def _contexto(resposta: dict) -> str:
        contexto = resposta.get("contexto")
        if contexto is None:
            return ""
        if not isinstance(contexto, str):
            raise ValueError(_ERRO_FORMATO)
        return contexto.strip()
