"""Adapter Jev para avaliar experiências profissionais por rubricas estruturadas."""
from __future__ import annotations

from jobsync.curriculo.domain.avaliacao_experiencia import (
    AvaliacaoExperiencia,
    ExperienciaParaAvaliacao,
)
from jobsync.curriculo.domain.avaliador_experiencia_port import (
    AvaliadorExperienciaPort,
)
from jobsync.shared_kernel.adapters.cliente_jev_client import ClienteJev, PerguntaScore

_PERGUNTAS = {
    "clareza_escrita": PerguntaScore(
        instrucoes=(
            "Avalie a clareza e a qualidade da escrita da experiência, considerando "
            "organização, objetividade e legibilidade."
        ),
        criterios=(
            "Muito pouco clara: difícil de compreender e sem organização.",
            "Pouco clara: escrita confusa ou pouco objetiva em vários trechos.",
            "Parcialmente clara: ideia geral compreensível, mas com problemas de organização ou objetividade.",
            "Clara: texto bem organizado e fácil de entender.",
            "Muito clara: texto conciso, fluido, bem organizado e fácil de entender.",
        ),
    ),
    "qualidade_detalhe": PerguntaScore(
        instrucoes=(
            "Avalie o nível de detalhe da experiência, incluindo responsabilidades, ações "
            "e resultados que estejam presentes no texto."
        ),
        criterios=(
            "Muito superficial: não explica responsabilidades nem ações realizadas.",
            "Superficial: menciona atividades sem detalhar contribuição ou contexto.",
            "Parcialmente detalhada: apresenta algumas responsabilidades, mas poucos detalhes de execução ou resultado.",
            "Detalhada: explica responsabilidades e contribuições com exemplos pertinentes.",
            "Muito detalhada: descreve ações, responsabilidades e resultados concretos presentes no texto.",
        ),
    ),
    "aderencia_vaga": PerguntaScore(
        instrucoes=(
            "Avalie a relevância da experiência para as responsabilidades e requisitos da vaga "
            "fornecida como contexto."
        ),
        criterios=(
            "Sem aderência: não há relação identificável com a vaga-alvo.",
            "Baixa aderência: poucas responsabilidades da experiência se relacionam à vaga.",
            "Aderência parcial: há alguns elementos relevantes, mas também lacunas importantes.",
            "Boa aderência: responsabilidades e competências são majoritariamente relevantes à vaga.",
            "Alta aderência: a experiência demonstra diretamente responsabilidades e competências centrais da vaga.",
        ),
    ),
    "consistencia_textual": PerguntaScore(
        instrucoes=(
            "Avalie somente se as afirmações da experiência são internamente coerentes e "
            "sustentadas pelo texto fornecido. Não verifique fatos externamente nem presuma "
            "que uma afirmação é verdadeira ou falsa."
        ),
        criterios=(
            "Muito inconsistente: há contradições claras ou afirmações sem qualquer sustentação textual.",
            "Inconsistente: existem afirmações conflitantes ou exageradas sem suporte no texto fornecido.",
            "Parcialmente consistente: o texto é em geral coerente, mas contém afirmações pouco sustentadas.",
            "Consistente: as afirmações são coerentes e têm suporte no próprio texto.",
            "Muito consistente: as afirmações são claras, coerentes e proporcionais às evidências apresentadas no texto.",
        ),
    ),
}


class AvaliadorExperienciaJevClient(AvaliadorExperienciaPort):
    """Traduz respostas tipadas do Jev para o modelo de domínio de currículo."""

    def __init__(self, cliente_jev: ClienteJev | None = None) -> None:
        self._cliente_jev = cliente_jev or ClienteJev()

    def avaliar(
        self,
        experiencia: ExperienciaParaAvaliacao,
        descricao_vaga: str,
    ) -> AvaliacaoExperiencia:
        estado = {
            "experiencia_profissional": {
                "cargo": experiencia.cargo,
                "empresa": experiencia.empresa,
                "periodo": experiencia.periodo,
                "descricao": experiencia.texto_completo,
            },
            "descricao_vaga": descricao_vaga,
        }
        respostas = self._cliente_jev.avaliar_scores(
            estado=estado,
            perguntas=_PERGUNTAS,
        )
        return AvaliacaoExperiencia(
            clareza_escrita=respostas["clareza_escrita"].normalizar(),
            qualidade_detalhe=respostas["qualidade_detalhe"].normalizar(),
            aderencia_vaga=respostas["aderencia_vaga"].normalizar(),
            consistencia_textual=respostas["consistencia_textual"].normalizar(),
        )
