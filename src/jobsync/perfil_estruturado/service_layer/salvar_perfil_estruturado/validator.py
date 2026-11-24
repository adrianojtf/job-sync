"""Validator de input para o caso de uso SalvarPerfilEstruturado."""
from __future__ import annotations

import logging

from jobsync.perfil_estruturado.domain.perfil_estruturado import LIMITE_DE_ITENS_POR_LISTA
from jobsync.perfil_estruturado.service_layer.salvar_perfil_estruturado.dtos import SalvarPerfilEstruturadoInputDto
from jobsync.shared_kernel.domain.periodo import Periodo, PeriodoInvalido, validar_ano

logger = logging.getLogger(__name__)


def _recusar(lista: str, posicao: int | None, mensagem: str) -> None:
    """Registra só o nome da lista e a posição (nunca o texto do currículo) e levanta ValueError."""
    logger.warning("Perfil recusado (lista=%s, posicao=%s).", lista, posicao)
    raise ValueError(mensagem)


class SalvarPerfilEstruturadoInputValidator:
    """Valida os dados de entrada do caso de uso."""

    @staticmethod
    def validar(input_dto: SalvarPerfilEstruturadoInputDto) -> None:
        """Valida o DTO de entrada e levanta ValueError se inválido."""
        if not input_dto.perfil_identificador or not input_dto.perfil_identificador.strip():
            raise ValueError("O identificador do perfil é obrigatório.")
        if not input_dto.nome_completo or not input_dto.nome_completo.strip():
            raise ValueError("O nome completo é obrigatório.")
        if not input_dto.email or not input_dto.email.strip():
            raise ValueError("O email é obrigatório.")
        SalvarPerfilEstruturadoInputValidator._validar_limites(input_dto)
        SalvarPerfilEstruturadoInputValidator._validar_periodos(input_dto)

    @staticmethod
    def _validar_limites(input_dto: SalvarPerfilEstruturadoInputDto) -> None:
        listas = (
            ("experiências", input_dto.experiencias),
            ("formações", input_dto.formacoes),
            ("certificações", input_dto.certificacoes),
            ("idiomas", input_dto.idiomas),
        )
        for nome, itens in listas:
            if len(itens) > LIMITE_DE_ITENS_POR_LISTA:
                _recusar(nome, None, f"A lista de {nome} aceita no máximo {LIMITE_DE_ITENS_POR_LISTA} itens.")

    @staticmethod
    def _validar_periodos(input_dto: SalvarPerfilEstruturadoInputDto) -> None:
        for posicao, experiencia in enumerate(input_dto.experiencias, start=1):
            SalvarPerfilEstruturadoInputValidator._validar_periodo("Experiência", "experiências", posicao, experiencia.periodo)
        for posicao, formacao in enumerate(input_dto.formacoes, start=1):
            SalvarPerfilEstruturadoInputValidator._validar_periodo("Formação", "formações", posicao, formacao.periodo)
        for posicao, certificacao in enumerate(input_dto.certificacoes, start=1):
            texto = (certificacao.ano or "").strip()
            if not texto:
                continue
            try:
                validar_ano(texto)
            except PeriodoInvalido as erro:
                _recusar("certificações", posicao, f"Certificação {posicao}: ano inválido. {erro}")

    @staticmethod
    def _validar_periodo(rotulo: str, lista: str, posicao: int, periodo: str) -> None:
        if not (periodo or "").strip():
            return
        try:
            Periodo.ler(periodo)
        except PeriodoInvalido as erro:
            _recusar(lista, posicao, f"{rotulo} {posicao}: período inválido. {erro}")
