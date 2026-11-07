"""Caso de uso: sugerir, via IA, conquistas e contexto novos para uma experiência adaptada.

Usado na revisão do currículo adaptado: a IA parte das conquistas e do contexto atuais do
usuário e os reescreve para a vaga. Cargo, empresa e período são sempre os recebidos.
Nada é persistido.
"""
from __future__ import annotations

from dataclasses import replace
from time import perf_counter

from jobsync.curriculo.domain.ajustador_experiencia_port import AjustadorExperienciaPort
from jobsync.curriculo.domain.contexto_vaga import ContextoVaga
from jobsync.curriculo.domain.experiencia_adaptada import ExperienciaAdaptada
from jobsync.curriculo.service_layer.sugerir_ajuste_experiencia_adaptada.validator import (
    SugerirAjusteExperienciaAdaptadaInputValidator,
)
from jobsync.curriculo.service_layer.sugestao_ia_indisponivel import SugestaoIAIndisponivel
from jobsync.curriculo.service_layer.validacoes_sugestao import registrar_sugestao


class SugerirAjusteExperienciaAdaptada:
    def __init__(self, ajustador_experiencia: AjustadorExperienciaPort) -> None:
        self._ajustador_experiencia = ajustador_experiencia

    def executar(
        self, experiencia: ExperienciaAdaptada, contexto: ContextoVaga
    ) -> ExperienciaAdaptada:
        SugerirAjusteExperienciaAdaptadaInputValidator.validar(experiencia)
        inicio = perf_counter()
        try:
            sugerida = self._ajustador_experiencia.refinar(
                experiencia=experiencia,
                descricao_vaga=contexto.descricao_vaga,
                idioma_alvo=contexto.idioma_alvo,
                analise_vaga=contexto.analise_vaga,
            )
        except (RuntimeError, ValueError) as erro:
            raise SugestaoIAIndisponivel() from erro
        registrar_sugestao(
            "vaga",
            "EXPERIENCIA_ADAPTADA",
            len(experiencia.como_descricao()),
            len(sugerida.como_descricao()),
            inicio,
        )
        return replace(experiencia, conquistas=sugerida.conquistas, contexto=sugerida.contexto)
