"""Caso de uso: login legado por identificador, sem senha.

Existe só para desenvolvimento e testes (flag `AUTH_LOGIN_SIMPLES_HABILITADO`). O perfil é o
próprio identificador, o que mantém acessíveis os perfis criados antes da autenticação real.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import UsuarioDuplicado
from jobsync.autenticacao.domain.usuario import Usuario
from jobsync.autenticacao.domain.usuario_repository import UsuarioRepository
from jobsync.autenticacao.service_layer.emitir_sessao.service import EmitirSessao
from jobsync.autenticacao.service_layer.sessao_iniciada import SessaoIniciada
from jobsync.shared_kernel.domain.relogio import agora_utc

_DOMINIO_FICTICIO = "simples.local"


@dataclass
class EntrarComIdentificadorSimples:
    _usuarios: UsuarioRepository
    _emitir_sessao: EmitirSessao
    _relogio: Callable[[], datetime] = agora_utc

    def executar(self, identificador: str) -> SessaoIniciada:
        perfil = identificador.strip()
        if not perfil:
            raise ValueError("O identificador não pode ser vazio.")
        usuario = self._usuarios.buscar_por_perfil(perfil) or self._criar(perfil)
        return SessaoIniciada(token=self._emitir_sessao.executar(usuario.id), usuario=usuario)

    def _criar(self, perfil: str) -> Usuario:
        resumo = hashlib.sha256(perfil.encode("utf-8")).hexdigest()[:20]
        novo = Usuario.novo(Email(f"dev-{resumo}@{_DOMINIO_FICTICIO}"), perfil, self._relogio()).verificar_email()
        try:
            self._usuarios.salvar_novo(novo)
        except UsuarioDuplicado:
            concorrente = self._usuarios.buscar_por_perfil(perfil)
            if concorrente is None:
                raise
            return concorrente
        return novo
