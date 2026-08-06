"""Shim de compatibilidade para NomeArquivo.

O Value Object real agora vive em `jobsync.shared_kernel.domain.nome_arquivo`.
Este modulo reexporta o simbolo para manter imports antigos funcionando durante
a migracao incremental.
"""

from jobsync.shared_kernel.domain.nome_arquivo import NomeArquivo

__all__ = ["NomeArquivo"]
