"""Dublê em memória de UsuarioRepository, para testes de serviço."""
from __future__ import annotations

from dataclasses import replace
from typing import Optional
from uuid import UUID

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import IdentidadeJaVinculada, UsuarioDuplicado
from jobsync.autenticacao.domain.identidade_externa import IdentidadeExterna
from jobsync.autenticacao.domain.usuario import Usuario
from jobsync.autenticacao.domain.usuario_repository import UsuarioRepository


class UsuarioRepositoryFake(UsuarioRepository):
    def __init__(self) -> None:
        self._usuarios: dict[UUID, Usuario] = {}
        self._identidades: dict[tuple[str, str], UUID] = {}
        self._senhas: dict[UUID, str] = {}

    def salvar_novo(self, usuario: Usuario) -> None:
        if self.buscar_por_email(usuario.email) or self.buscar_por_perfil(usuario.perfil_identificador):
            raise UsuarioDuplicado("E-mail ou perfil já associado a outro usuário.")
        self._usuarios[usuario.id] = usuario

    def atualizar(self, usuario: Usuario) -> None:
        self._usuarios[usuario.id] = replace(usuario)

    def buscar_por_id(self, usuario_id: UUID) -> Optional[Usuario]:
        return self._usuarios.get(usuario_id)

    def buscar_por_email(self, email: Email) -> Optional[Usuario]:
        return next((u for u in self._usuarios.values() if u.email == email), None)

    def buscar_por_perfil(self, perfil_identificador: str) -> Optional[Usuario]:
        return next(
            (u for u in self._usuarios.values() if u.perfil_identificador == perfil_identificador), None
        )

    def buscar_por_identidade(self, provedor: str, subject: str) -> Optional[Usuario]:
        usuario_id = self._identidades.get((provedor, subject))
        return self._usuarios.get(usuario_id) if usuario_id else None

    def vincular_identidade(self, identidade: IdentidadeExterna) -> None:
        chave = (identidade.provedor, identidade.subject)
        if chave in self._identidades:
            raise IdentidadeJaVinculada("Identidade já vinculada.")
        self._identidades[chave] = identidade.usuario_id

    def obter_senha_hash(self, usuario_id: UUID) -> Optional[str]:
        return self._senhas.get(usuario_id)

    def definir_senha_hash(self, usuario_id: UUID, senha_hash: str) -> None:
        self._senhas[usuario_id] = senha_hash

    def remover_senha(self, usuario_id: UUID) -> None:
        self._senhas.pop(usuario_id, None)
