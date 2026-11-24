"""Caso de uso: migrar as experiências legadas do perfil para os quatro blocos, em rascunho.

O resultado nunca é gravado: o usuário revisa e só então salva pelo caso de uso SalvarPerfilEstruturado.
"""
from __future__ import annotations

from dataclasses import replace

from jobsync.perfil_estruturado.domain.estruturar_experiencia_service import EstruturarExperienciaService
from jobsync.perfil_estruturado.domain.exceptions import PerfilEstruturadoNaoEncontrado
from jobsync.perfil_estruturado.domain.perfil_estruturado import PerfilEstruturado
from jobsync.perfil_estruturado.domain.perfil_estruturado_repository import PerfilEstruturadoRepository
from jobsync.perfil_estruturado.service_layer.migrar_experiencias_do_perfil.dtos import (
    MigrarExperienciasDoPerfilInputDto,
)
from jobsync.perfil_estruturado.service_layer.migrar_experiencias_do_perfil.validator import (
    MigrarExperienciasDoPerfilInputValidator,
)


class MigrarExperienciasDoPerfil:
    """Devolve o perfil com as experiências legadas estruturadas; as demais não mudam."""

    def __init__(self, repositorio: PerfilEstruturadoRepository, estruturador: EstruturarExperienciaService) -> None:
        self._repositorio = repositorio
        self._estruturador = estruturador

    def executar(self, input_dto: MigrarExperienciasDoPerfilInputDto) -> PerfilEstruturado:
        MigrarExperienciasDoPerfilInputValidator.validar(input_dto)
        perfil = self._repositorio.buscar_por_perfil(input_dto.perfil_identificador)
        if perfil is None:
            raise PerfilEstruturadoNaoEncontrado()

        posicoes = [indice for indice, experiencia in enumerate(perfil.experiencias) if experiencia.eh_legada]
        migradas = self._estruturador.executar_varias([perfil.experiencias[indice] for indice in posicoes])
        experiencias = list(perfil.experiencias)
        for indice, migrada in zip(posicoes, migradas):
            experiencias[indice] = migrada
        return replace(perfil, experiencias=tuple(experiencias))
