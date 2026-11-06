"""Caso de uso: buscar vagas em fontes externas e calcular o match com um currículo salvo.

Busca as cinco fontes em paralelo, deduplica por título+empresa e calcula o
ATS Score (Domain Service reaproveitado) de cada vaga restante contra o
currículo informado, retornando a lista ordenada por score.
"""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

from jobsync.ats_score import CalcularAtsScore
from jobsync.curriculo import Curriculo, ExtratorCurriculoPort
from jobsync.vaga import AnaliseVaga
from jobsync.vaga.domain.job_description_analyzer_port import JobDescriptionAnalyzerPort
from jobsync.vaga_externa.domain.buscador_vagas_externo_port import BuscadorVagasExternoPort
from jobsync.vaga_externa.domain.vaga_externa import VagaComScore, VagaExterna

logger = logging.getLogger(__name__)

LIMITE_VAGAS_ANALISADAS = 20
"""Cada vaga analisada custa uma chamada à API OpenAI (JobDescriptionAnalyzerPort).

Fontes como RemoteOK e Arbeitnow podem devolver 100+ resultados por termo —
sem limite, uma única busca esgota a cota diária de tokens da conta OpenAI.
"""


class DescobrirVagasComMatch:
    """Orquestra a busca externa e o cálculo de match."""

    def __init__(
        self,
        buscadores: tuple[BuscadorVagasExternoPort, ...],
        analisador_vaga: JobDescriptionAnalyzerPort,
        extrator_curriculo: ExtratorCurriculoPort,
        calcular_score: CalcularAtsScore,
    ) -> None:
        self._buscadores = buscadores
        self._analisador_vaga = analisador_vaga
        self._extrator_curriculo = extrator_curriculo
        self._calcular_score = calcular_score

    def executar(
        self, termo: str, pdf_curriculo: bytes, dias_maximo: int | None = None
    ) -> tuple[VagaComScore, ...]:
        if not termo or not termo.strip():
            raise ValueError("O termo de busca é obrigatório.")
        if not pdf_curriculo:
            raise ValueError("O PDF do currículo é obrigatório.")

        curriculo = self._extrator_curriculo.extrair(pdf_curriculo)
        vagas_unicas = self._deduplicar(self._buscar_em_paralelo(termo, dias_maximo))
        vagas_no_periodo = self._filtrar_por_periodo(vagas_unicas, dias_maximo)
        vagas_a_analisar = vagas_no_periodo[:LIMITE_VAGAS_ANALISADAS]

        vagas_com_score = []
        for vaga in vagas_a_analisar:
            analise_vaga = self._analisador_vaga.analisar(vaga.descricao)
            resultado_score = self._calcular_score.executar(curriculo, analise_vaga)
            vagas_com_score.append(VagaComScore(vaga=vaga, resultado_score=resultado_score))

        return tuple(sorted(vagas_com_score, key=lambda v: v.resultado_score.nota, reverse=True))

    def _buscar_em_paralelo(self, termo: str, dias_maximo: int | None) -> tuple[VagaExterna, ...]:
        if not self._buscadores:
            return ()

        resultados: list[VagaExterna] = []
        with ThreadPoolExecutor(max_workers=len(self._buscadores)) as executor:
            futuros = {
                executor.submit(buscador.buscar, termo, dias_maximo): buscador
                for buscador in self._buscadores
            }
            for futuro in as_completed(futuros):
                buscador = futuros[futuro]
                try:
                    resultados.extend(futuro.result())
                except Exception as erro:  # noqa: BLE001 - falha isolada de uma fonte não derruba as demais
                    logger.warning("Falha na busca da fonte %s: %s", type(buscador).__name__, erro)
        return tuple(resultados)

    @staticmethod
    def _filtrar_por_periodo(
        vagas: tuple[VagaExterna, ...], dias_maximo: int | None
    ) -> tuple[VagaExterna, ...]:
        if dias_maximo is None:
            return vagas

        hoje = date.today()
        return tuple(
            vaga
            for vaga in vagas
            if vaga.data_publicacao is None or (hoje - vaga.data_publicacao).days <= dias_maximo
        )

    @staticmethod
    def _deduplicar(vagas: tuple[VagaExterna, ...]) -> tuple[VagaExterna, ...]:
        vistas: set[tuple[str, str]] = set()
        unicas: list[VagaExterna] = []
        for vaga in vagas:
            chave = (vaga.titulo.lower(), vaga.empresa.lower())
            if chave in vistas:
                continue
            vistas.add(chave)
            unicas.append(vaga)
        return tuple(unicas)
