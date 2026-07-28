"""Domain Service: calcula o ATS Score de um currículo adaptado em relação a uma vaga.

Lógica pura de domínio (sem porta/infraestrutura): compara os requisitos
técnicos explícitos já extraídos pela análise de vaga com o conteúdo das
seções do currículo. Stateless, sem dependência de repositório ou serviço
externo — por isso vive em `domain`, não em `application.use_cases`.
"""
from __future__ import annotations

from domain.ats_score import ResultadoAtsScore
from domain.curriculo import Curriculo
from domain.vaga import AnaliseVaga, TipoRequisitoTecnico


class CalcularAtsScore:
    """Calcula a nota de aderência (0-100) e os requisitos explícitos não cobertos."""

    def executar(self, curriculo: Curriculo, analise_vaga: AnaliseVaga) -> ResultadoAtsScore:
        requisitos_explicitos = [
            requisito
            for requisito in analise_vaga.requisitos
            if requisito.tipo == TipoRequisitoTecnico.EXPLICITO
        ]

        if not requisitos_explicitos:
            return ResultadoAtsScore(nota=100, requisitos_faltantes=())

        conteudo_completo = " ".join(secao.conteudo for secao in curriculo.secoes).lower()

        requisitos_faltantes = tuple(
            requisito
            for requisito in requisitos_explicitos
            if requisito.nome.lower() not in conteudo_completo
        )

        cobertos = len(requisitos_explicitos) - len(requisitos_faltantes)
        nota = round(100 * cobertos / len(requisitos_explicitos))

        return ResultadoAtsScore(nota=nota, requisitos_faltantes=requisitos_faltantes)
