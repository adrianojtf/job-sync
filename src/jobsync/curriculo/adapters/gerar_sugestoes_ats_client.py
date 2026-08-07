"""Adapter (implementa GerarSugestoesAtsPort) que sugere melhorias de ATS Score via IA.

Diferente de AjustadorTextoGroq/GeradorCartaApresentacaoGroq, este adapter não
reescreve nada do candidato — apenas aponta, para cada requisito faltante já
identificado por CalcularAtsScore, o que mudar no currículo (e onde), sem
jamais sugerir afirmar experiência que o candidato não possui.
"""
from __future__ import annotations

from jobsync.ats_score import ResultadoAtsScore
from jobsync.curriculo import Curriculo
from jobsync.curriculo.domain.gerar_sugestoes_ats_port import GerarSugestoesAtsPort
from jobsync.vaga import AnaliseVaga, TipoRequisitoTecnico
from jobsync.shared_kernel.adapters.cliente_groq_client import ClienteGroq

_PROMPT_SISTEMA = """\
Você é um especialista em otimização de currículos para sistemas de triagem \
automática (ATS - Applicant Tracking Systems). Sua tarefa é sugerir mudanças \
concretas e acionáveis no currículo do candidato para aumentar a aderência a \
uma vaga específica, considerando APENAS os requisitos já identificados como \
faltantes.

Regras obrigatórias:
- NUNCA sugira que o candidato afirme ter uma tecnologia, ferramenta ou \
experiência que não aparece em nenhuma seção do currículo.
- Se o candidato já parece ter experiência relacionada (ex: "containers" mas \
não cita "Docker" explicitamente), sugira tornar isso explícito.
- Se não há nenhuma evidência de relação com o requisito faltante, diga \
claramente que essa é uma lacuna real de experiência, não uma questão de \
redação.
- Seja específico: aponte em qual seção do currículo cada mudança deveria \
ser feita.

Responda ESTRITAMENTE em JSON no formato:
{"sugestoes": ["um tópico por requisito faltante, cada um começando pelo nome do requisito"]}

Cada item da lista deve ser um tópico independente e autocontido (será exibido
como um item de lista para o candidato), não um parágrafo corrido cobrindo
todos os requisitos juntos.
"""


class GerarSugestoesAtsClient(GerarSugestoesAtsPort):
    """Gera sugestões de melhoria de ATS Score (uma por tópico) usando o modelo Groq."""

    def __init__(self, cliente_groq: ClienteGroq | None = None) -> None:
        self._cliente_groq = cliente_groq or ClienteGroq()

    def gerar(
        self,
        curriculo: Curriculo,
        analise_vaga: AnaliseVaga,
        resultado_ats: ResultadoAtsScore,
    ) -> tuple[str, ...]:
        if not resultado_ats.requisitos_faltantes:
            return (
                "Nenhuma mudança necessária: todos os requisitos explícitos da vaga já aparecem no currículo.",
            )

        conteudo_curriculo = "\n\n".join(
            f"{secao.titulo}:\n{secao.conteudo}" for secao in curriculo.secoes
        )
        requisitos_faltantes = ", ".join(r.nome for r in resultado_ats.requisitos_faltantes)

        prompt_usuario = (
            f"Nota atual de ATS Score: {resultado_ats.nota}/100\n\n"
            f"Requisitos da vaga não encontrados no currículo: {requisitos_faltantes}\n\n"
            f"Currículo do candidato:\n{conteudo_curriculo}\n\n"
            f"Descrição da vaga:\n{analise_vaga.texto_original}\n\n"
            "Para cada requisito faltante, diga: (1) se há evidência de experiência "
            "relacionada em alguma seção do currículo que poderia ser tornada mais "
            "explícita, e onde; ou (2) se é uma lacuna real de experiência, sem "
            "sugerir invenção de fatos."
        )

        resposta = self._cliente_groq.solicitar_json(
            prompt_sistema=_PROMPT_SISTEMA,
            prompt_usuario=prompt_usuario,
        )
        sugestoes = self._normalizar_sugestoes(resposta.get("sugestoes"))
        if not sugestoes:
            raise ValueError("O modelo não retornou sugestões de melhoria de ATS Score.")

        return sugestoes

    @staticmethod
    def _normalizar_sugestoes(sugestoes_bruta: object) -> tuple[str, ...]:
        """Normaliza a resposta do modelo para uma tupla de tópicos, tolerando formatos inesperados."""
        if isinstance(sugestoes_bruta, list):
            return tuple(str(item).strip() for item in sugestoes_bruta if str(item).strip())
        if isinstance(sugestoes_bruta, dict):
            return tuple(f"{chave}: {valor}".strip() for chave, valor in sugestoes_bruta.items())
        if sugestoes_bruta:
            texto = str(sugestoes_bruta).strip()
            return (texto,) if texto else ()
        return ()
