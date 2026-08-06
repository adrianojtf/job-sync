"""Shim de compatibilidade para CatalogoLocalizacao.

O Value Object real agora vive em `jobsync.shared_kernel.domain.catalogo_localizacao`.
Este modulo reexporta o simbolo para manter imports antigos funcionando durante
a migracao incremental.
"""

from jobsync.shared_kernel.domain.catalogo_localizacao import CatalogoLocalizacao

__all__ = ["CatalogoLocalizacao"]
