"""Adapter Jev para avaliar descrições de vagas por rubricas estruturadas."""
from __future__ import annotations

from jobsync.shared_kernel.adapters.cliente_jev_client import ClienteJev, PerguntaScore
from jobsync.vaga.domain.avaliacao_descricao_vaga import AvaliacaoDescricaoVaga
from jobsync.vaga.domain.avaliador_descricao_vaga_port import AvaliadorDescricaoVagaPort

_PERGUNTAS = {
    "completude": PerguntaScore(
        instrucoes=(
            "Avalie a completude da descrição como anúncio de vaga, considerando cargo, "
            "responsabilidades, requisitos e informações essenciais."
        ),
        criterios=(
            "Muito insuficiente: não identifica o cargo nem descreve o trabalho.",
            "Insuficiente: omite a maioria das informações essenciais da vaga.",
            "Parcial: informa o cargo, mas deixa lacunas importantes em responsabilidades ou requisitos.",
            "Adequada: apresenta cargo, principais responsabilidades e requisitos necessários.",
            "Muito completa: apresenta cargo, responsabilidades, requisitos e contexto suficiente para candidatura.",
        ),
    ),
    "clareza": PerguntaScore(
        instrucoes=(
            "Avalie a clareza da descrição, considerando organização, linguagem objetiva, "
            "ambiguidades e contradições."
        ),
        criterios=(
            "Muito confusa: texto difícil de compreender, desorganizado ou contraditório.",
            "Confusa: várias ambiguidades dificultam entender o trabalho ou os requisitos.",
            "Parcialmente clara: sentido geral compreensível, mas com ambiguidades relevantes.",
            "Clara: informações organizadas e compreensíveis, com poucas ambiguidades.",
            "Muito clara: texto direto, bem organizado e sem ambiguidades relevantes.",
        ),
    ),
    "relevancia": PerguntaScore(
        instrucoes=(
            "Avalie se o conteúdo descreve uma vaga real e se as responsabilidades e requisitos "
            "são pertinentes ao cargo anunciado."
        ),
        criterios=(
            "Irrelevante: não descreve uma vaga ou não apresenta conteúdo relacionado ao cargo.",
            "Pouco relevante: a maior parte do conteúdo não corresponde ao cargo anunciado.",
            "Parcialmente relevante: mistura informações pertinentes e requisitos pouco relacionados.",
            "Relevante: responsabilidades e requisitos são majoritariamente pertinentes ao cargo.",
            "Muito relevante: todo o conteúdo é claramente pertinente ao trabalho e ao cargo anunciado.",
        ),
    ),
    "inclusao": PerguntaScore(
        instrucoes=(
            "Avalie se a linguagem é respeitosa e inclusiva e se evita exigências potencialmente "
            "discriminatórias ou excludentes sem relação necessária com o trabalho."
        ),
        criterios=(
            "Muito excludente: contém linguagem ou exigências claramente discriminatórias.",
            "Excludente: contém sinais fortes de preferência ou exclusão sem justificativa profissional.",
            "Mista: linguagem geralmente neutra, com alguns trechos potencialmente excludentes.",
            "Inclusiva: linguagem respeitosa e sem sinais relevantes de exclusão.",
            "Muito inclusiva: linguagem neutra, acessível e focada em requisitos relacionados ao trabalho.",
        ),
    ),
}


class AvaliadorDescricaoVagaJevClient(AvaliadorDescricaoVagaPort):
    """Traduz respostas tipadas do Jev para o modelo de domínio de vaga."""

    def __init__(self, cliente_jev: ClienteJev | None = None) -> None:
        self._cliente_jev = cliente_jev or ClienteJev()

    def avaliar(self, descricao_vaga: str) -> AvaliacaoDescricaoVaga:
        respostas = self._cliente_jev.avaliar_scores(
            estado=descricao_vaga,
            perguntas=_PERGUNTAS,
        )
        return AvaliacaoDescricaoVaga(
            completude=respostas["completude"].normalizar(),
            clareza=respostas["clareza"].normalizar(),
            relevancia=respostas["relevancia"].normalizar(),
            inclusao=respostas["inclusao"].normalizar(),
        )
