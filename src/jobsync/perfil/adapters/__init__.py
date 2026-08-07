"""Adapters concretos do domínio Perfil."""

from jobsync.perfil.adapters.perfil_repository_fake import PerfilRepositoryFake
from jobsync.perfil.adapters.perfil_repository_impl import PerfilRepositoryImpl

__all__ = ["PerfilRepositoryFake", "PerfilRepositoryImpl"]
