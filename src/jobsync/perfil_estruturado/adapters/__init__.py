"""Adapters concretos do domínio Perfil Estruturado."""

from jobsync.perfil_estruturado.adapters.extrator_perfil_estruturado_client import (
    ExtratorPerfilEstruturadoClient,
)
from jobsync.perfil_estruturado.adapters.perfil_estruturado_repository_fake import (
    PerfilEstruturadoRepositoryFake,
)
from jobsync.perfil_estruturado.adapters.perfil_estruturado_repository_impl import (
    PerfilEstruturadoRepositoryImpl,
)

__all__ = [
    "ExtratorPerfilEstruturadoClient",
    "PerfilEstruturadoRepositoryFake",
    "PerfilEstruturadoRepositoryImpl",
]
