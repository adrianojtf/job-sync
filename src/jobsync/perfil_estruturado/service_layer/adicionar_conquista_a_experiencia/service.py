"""Caso de uso: guardar no banco da experiência a conquista aprovada a partir de uma pergunta (JOB-0043)."""
from __future__ import annotations

from jobsync.perfil_estruturado.domain.exceptions import PerfilEstruturadoNaoEncontrado
from jobsync.perfil_estruturado.domain.perfil_estruturado import Conquista, OrigemConquista, PerfilEstruturado
from jobsync.perfil_estruturado.domain.perfil_estruturado_repository import PerfilEstruturadoRepository
from jobsync.perfil_estruturado.service_layer.adicionar_conquista_a_experiencia.dtos import (
    AdicionarConquistaAExperienciaInputDto,
)
from jobsync.perfil_estruturado.service_layer.adicionar_conquista_a_experiencia.validator import (
    AdicionarConquistaAExperienciaInputValidator,
)


class AdicionarConquistaAExperiencia:
    """Acrescenta a conquista, com origem `RESPOSTA_PERGUNTA`, sem tocar no resto do perfil."""

    def __init__(self, repositorio: PerfilEstruturadoRepository) -> None:
        self._repositorio = repositorio

    def executar(self, input_dto: AdicionarConquistaAExperienciaInputDto) -> PerfilEstruturado:
        AdicionarConquistaAExperienciaInputValidator.validar(input_dto)
        perfil = self._repositorio.buscar_por_perfil(input_dto.perfil_identificador)
        if perfil is None:
            raise PerfilEstruturadoNaoEncontrado()
        atualizado = perfil.com_conquista_na_experiencia(
            input_dto.experiencia_indice,
            Conquista(texto=input_dto.texto, origem=OrigemConquista.RESPOSTA_PERGUNTA),
        )
        return self._repositorio.salvar(atualizado)
