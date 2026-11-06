"""Caso de uso: sugerir, via IA, uma nova descrição para uma experiência profissional.

Com contexto de vaga (revisão do currículo adaptado), adapta a descrição à vaga; sem
contexto (tela Meu perfil), apenas melhora a escrita. Cargo, empresa e período são
sempre os recebidos. Nada é persistido.
"""
from __future__ import annotations

from dataclasses import replace
from time import perf_counter

from jobsync.curriculo.domain.ajustador_experiencia_port import AjustadorExperienciaPort
from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.contexto_vaga import ContextoVaga
from jobsync.curriculo.domain.melhorador_texto_curriculo_port import MelhoradorTextoCurriculoPort
from jobsync.curriculo.service_layer.sugerir_ajuste_experiencia.validator import (
    SugerirAjusteExperienciaInputValidator,
)
from jobsync.curriculo.service_layer.sugestao_ia_indisponivel import SugestaoIAIndisponivel
from jobsync.curriculo.service_layer.validacoes_sugestao import registrar_sugestao


class SugerirAjusteExperiencia:
    def __init__(
        self,
        ajustador_experiencia: AjustadorExperienciaPort,
        melhorador: MelhoradorTextoCurriculoPort,
    ) -> None:
        self._ajustador_experiencia = ajustador_experiencia
        self._melhorador = melhorador

    def executar(
        self, experiencia: ExperienciaParaAvaliacao, contexto: ContextoVaga | None
    ) -> ExperienciaParaAvaliacao:
        SugerirAjusteExperienciaInputValidator.validar(experiencia)
        inicio = perf_counter()
        try:
            sugerida = self._sugerir(experiencia, contexto)
        except (RuntimeError, ValueError) as erro:
            raise SugestaoIAIndisponivel() from erro
        registrar_sugestao(
            "vaga" if contexto else "perfil",
            "EXPERIENCIA",
            len(experiencia.descricao),
            len(sugerida.descricao),
            inicio,
        )
        return replace(experiencia, descricao=sugerida.descricao)

    def _sugerir(
        self, experiencia: ExperienciaParaAvaliacao, contexto: ContextoVaga | None
    ) -> ExperienciaParaAvaliacao:
        if contexto is None:
            return self._melhorador.melhorar_experiencia(experiencia)
        return self._ajustador_experiencia.ajustar(
            experiencia=experiencia,
            descricao_vaga=contexto.descricao_vaga,
            idioma_alvo=contexto.idioma_alvo,
            analise_vaga=contexto.analise_vaga,
        )
