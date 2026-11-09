"""Trecho de prompt comum às sugestões de IA que refinam o texto atual (JOB-0037)."""
from __future__ import annotations

from jobsync.curriculo.domain.refino import FocoRefino, PedidoRefino

_FOCOS: dict[FocoRefino, str] = {
    FocoRefino.ADERENCIA_VAGA: "aderência à vaga: aproxime o texto dos requisitos e do cargo-alvo",
    FocoRefino.IMPACTO: "impacto e resultados: evidencie entregas e resultados, com números quando o texto os tiver",
    FocoRefino.PALAVRAS_CHAVE: (
        "palavras-chave da vaga: use os termos exatos da vaga onde forem verdadeiros, para a leitura por ATS"
    ),
    FocoRefino.CLAREZA_CONCISAO: "clareza e concisão: frases mais curtas e diretas, sem perder fatos",
    FocoRefino.ENFASE_TECNICA: "ênfase técnica: destaque tecnologias, arquitetura e decisões técnicas já citadas",
}


def bloco_refino(refino: PedidoRefino, com_vaga: bool) -> str:
    """Instrução de refino: parte do texto atual, foco da tentativa e versões a não repetir."""
    linhas = [
        "Parta do texto atual e melhore-o com uma abordagem diferente das versões anteriores.",
        f"Foco desta versão: {_FOCOS[refino.foco(com_vaga)]}.",
    ]
    if refino.sugestoes_anteriores:
        linhas.append("Não repita estas versões já sugeridas:")
        linhas.extend(f"---\n{sugestao}" for sugestao in refino.sugestoes_anteriores)
        linhas.append("---")
    return "\n".join(linhas)
