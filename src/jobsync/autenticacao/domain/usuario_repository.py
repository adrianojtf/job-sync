"""Porta de persistência de usuários, identidades externas e credenciais de senha."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.identidade_externa import IdentidadeExterna
from jobsync.autenticacao.domain.usuario import Usuario


class UsuarioRepository(ABC):
    """Contrato de acesso ao agregado Usuario; a implementação concreta fica em `adapters`."""

    @abstractmethod
    def salvar_novo(self, usuario: Usuario) -> None:
        """Cria o usuário e garante a existência do perfil, na mesma transação.

        Levanta `UsuarioDuplicado` se o e-mail ou o perfil já pertencem a outro usuário.
        """

    @abstractmethod
    def atualizar(self, usuario: Usuario) -> None: ...

    @abstractmethod
    def buscar_por_id(self, usuario_id: UUID) -> Optional[Usuario]: ...

    @abstractmethod
    def buscar_por_email(self, email: Email) -> Optional[Usuario]: ...

    @abstractmethod
    def buscar_por_perfil(self, perfil_identificador: str) -> Optional[Usuario]: ...

    @abstractmethod
    def buscar_por_identidade(self, provedor: str, subject: str) -> Optional[Usuario]: ...

    @abstractmethod
    def vincular_identidade(self, identidade: IdentidadeExterna) -> None:
        """Levanta `IdentidadeJaVinculada` se (provedor, subject) já estiver em uso."""

    @abstractmethod
    def obter_senha_hash(self, usuario_id: UUID) -> Optional[str]: ...

    @abstractmethod
    def definir_senha_hash(self, usuario_id: UUID, senha_hash: str) -> None:
        """Cria ou substitui a credencial de senha do usuário."""

    @abstractmethod
    def remover_senha(self, usuario_id: UUID) -> None: ...
