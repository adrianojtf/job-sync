"""Caso de uso: sugerir, via IA, uma nova descrição para uma experiência profissional.

Usado na tela Meu perfil, onde não há vaga-alvo: a IA apenas melhora a escrita do texto
livre. Cargo, empresa e período são sempre os recebidos. Nada é persistido.
"""
from __future__ import annotations

from dataclasses import replace
from time import perf_counter

from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.melhorador_texto_curriculo_port import MelhoradorTextoCurriculoPort
from jobsync.curriculo.domain.refino import PedidoRefino, SugestaoRefinada
from jobsync.curriculo.service_layer.sugerir_ajuste_experiencia.validator import (
    SugerirAjusteExperienciaInputValidator,
)
from jobsync.curriculo.service_layer.sugestao_ia_indisponivel import SugestaoIAIndisponivel
from jobsync.curriculo.service_layer.validacoes_sugestao import registrar_sugestao


class SugerirAjusteExperiencia:
    def __init__(self, melhorador: MelhoradorTextoCurriculoPort) -> None:
        self._melhorador = melhorador

    def executar(
        self, experiencia: ExperienciaParaAvaliacao, refino: PedidoRefino = PedidoRefino()
    ) -> SugestaoRefinada[ExperienciaParaAvaliacao]:
        SugerirAjusteExperienciaInputValidator.validar(experiencia, refino)
        foco = refino.foco(com_vaga=False)
        inicio = perf_counter()
        try:
            sugerida = self._melhorador.melhorar_experiencia(experiencia, refino)
        except (RuntimeError, ValueError) as erro:
            raise SugestaoIAIndisponivel() from erro
        registrar_sugestao(
            "perfil",
            "EXPERIENCIA",
            len(experiencia.descricao),
            len(sugerida.descricao),
            inicio,
            refino,
            foco,
        )
        return SugestaoRefinada(replace(experiencia, descricao=sugerida.descricao), foco)
