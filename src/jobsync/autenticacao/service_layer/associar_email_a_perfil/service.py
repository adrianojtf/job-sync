"""Caso de uso do mantenedor: associa um e-mail a um perfil criado antes da autenticação real.

Cria o `Usuario` sem senha e sem e-mail verificado. O vínculo só se completa no primeiro login
em que o dono provar o e-mail (Google com e-mail verificado, ou link de confirmação). Assim, saber
o identificador de um perfil legado não basta para tomá-lo.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import (
    EmailEmUso,
    PerfilInexistente,
    PerfilJaAssociado,
    UsuarioDuplicado,
)
from jobsync.autenticacao.domain.usuario import Usuario
from jobsync.autenticacao.domain.usuario_repository import UsuarioRepository
from jobsync.perfil.domain.perfil_repository import PerfilRepository
from jobsync.shared_kernel.domain.relogio import agora_utc

logger = logging.getLogger(__name__)


class ResultadoAssociacao(Enum):
    ASSOCIADO = "associado"
    JA_ASSOCIADO = "ja_associado"


@dataclass
class AssociarEmailAPerfil:
    _usuarios: UsuarioRepository
    _perfis: PerfilRepository
    _relogio: Callable[[], datetime] = agora_utc

    def executar(self, perfil_identificador: str, email: str) -> ResultadoAssociacao:
        email_vo = Email(email)
        if self._perfis.buscar_por_identificador(perfil_identificador) is None:
            raise PerfilInexistente(f"O perfil '{perfil_identificador}' não existe.")

        do_perfil = self._usuarios.buscar_por_perfil(perfil_identificador)
        if do_perfil is not None:
            if do_perfil.email == email_vo:
                return ResultadoAssociacao.JA_ASSOCIADO
            raise PerfilJaAssociado(f"O perfil '{perfil_identificador}' já está associado a outro e-mail.")
        if self._usuarios.buscar_por_email(email_vo) is not None:
            raise EmailEmUso("Esse e-mail já pertence a outro usuário.")

        try:
            self._usuarios.salvar_novo(Usuario.novo(email_vo, perfil_identificador, self._relogio()))
        except UsuarioDuplicado as erro:
            raise EmailEmUso("Esse e-mail ou perfil já pertence a outro usuário.") from erro
        logger.info("email_associado_ao_perfil perfil=%s", perfil_identificador)
        return ResultadoAssociacao.ASSOCIADO
