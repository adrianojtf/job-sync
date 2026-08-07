"""Raiz de composição (Composition Root) para os entrypoints da aplicação.

Centraliza a instanciação de adapters concretos e a injeção de dependências
nos services, mantendo os entrypoints livres de lógica de composição.
"""
from __future__ import annotations

import os
from pathlib import Path

from jobsync.candidatura.adapters import CandidaturaRepositoryImpl
from jobsync.curriculo_salvo.adapters import CurriculoSalvoRepositoryImpl
from jobsync.perfil.adapters import PerfilRepositoryImpl
from jobsync.perfil_estruturado.adapters import PerfilEstruturadoRepositoryImpl
from jobsync.token_captura.adapters import TokenCapturaRepositoryImpl
from jobsync.vaga.adapters import VagaRepositoryImpl

_DIRETORIO_ARMAZENAMENTO = Path(__file__).resolve().parent.parent.parent.parent / "storage"
_CAMINHO_BANCO_PADRAO = str(_DIRETORIO_ARMAZENAMENTO / "job_sync.db")


def obter_caminho_banco() -> str:
    """Permite apontar para um banco alternativo (ex: testes) via variável de ambiente."""
    return os.getenv("JOB_SYNC_DB_PATH", _CAMINHO_BANCO_PADRAO)


def obter_repositorio_token(caminho_banco: str | None = None) -> TokenCapturaRepositoryImpl:
    return TokenCapturaRepositoryImpl(caminho_banco=caminho_banco or obter_caminho_banco())


def obter_repositorio_vaga(caminho_banco: str | None = None) -> VagaRepositoryImpl:
    return VagaRepositoryImpl(caminho_banco=caminho_banco or obter_caminho_banco())


def obter_repositorio_candidatura(caminho_banco: str | None = None) -> CandidaturaRepositoryImpl:
    return CandidaturaRepositoryImpl(caminho_banco=caminho_banco or obter_caminho_banco())


def obter_repositorio_curriculo_salvo(caminho_banco: str | None = None) -> CurriculoSalvoRepositoryImpl:
    return CurriculoSalvoRepositoryImpl(caminho_banco=caminho_banco or obter_caminho_banco())


def obter_repositorio_perfil(caminho_banco: str | None = None) -> PerfilRepositoryImpl:
    return PerfilRepositoryImpl(caminho_banco=caminho_banco or obter_caminho_banco())


def obter_repositorio_perfil_estruturado(caminho_banco: str | None = None) -> PerfilEstruturadoRepositoryImpl:
    return PerfilEstruturadoRepositoryImpl(caminho_banco=caminho_banco or obter_caminho_banco())
