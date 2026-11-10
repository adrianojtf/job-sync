"""Raiz de composição (Composition Root) para os entrypoints da aplicação.

Centraliza a instanciação de adapters concretos e a injeção de dependências
nos services, mantendo os entrypoints livres de lógica de composição.
"""
from __future__ import annotations

import os
from functools import lru_cache

from psycopg_pool import ConnectionPool

from jobsync.candidatura.adapters import CandidaturaRepositoryImpl
from jobsync.curriculo_salvo.adapters import CurriculoSalvoRepositoryImpl
from jobsync.entrypoints.autenticacao_servicos import ServicosAutenticacao, servicos_autenticacao_do_ambiente
from jobsync.perfil.adapters import PerfilRepositoryImpl
from jobsync.perfil_estruturado.adapters import PerfilEstruturadoRepositoryImpl
from jobsync.shared_kernel.adapters.persistence.conexao_postgres import criar_pool, obter_url_banco
from jobsync.shared_kernel.adapters.persistence.executor_migracoes import executar_migracoes
from jobsync.token_captura.adapters import TokenCapturaRepositoryImpl
from jobsync.vaga.adapters import VagaRepositoryImpl


@lru_cache(maxsize=1)
def obter_pool_conexoes() -> ConnectionPool:
    """Pool único do processo, aberto na primeira necessidade a partir de DATABASE_URL."""
    return criar_pool(obter_url_banco())


def preparar_banco() -> None:
    """Abre o pool (falha rápido sem banco) e aplica as migrações pendentes."""
    with obter_pool_conexoes().connection() as conexao:
        executar_migracoes(conexao)


@lru_cache(maxsize=1)
def obter_servicos_autenticacao() -> ServicosAutenticacao:
    """Serviços de autenticação do processo (únicos, para reaproveitar o hash fictício do login)."""
    return servicos_autenticacao_do_ambiente(obter_pool_conexoes(), os.environ)


def fechar_pool_conexoes() -> None:
    obter_servicos_autenticacao.cache_clear()
    if obter_pool_conexoes.cache_info().currsize:
        obter_pool_conexoes().close()
        obter_pool_conexoes.cache_clear()


def obter_repositorio_token() -> TokenCapturaRepositoryImpl:
    return TokenCapturaRepositoryImpl(obter_pool_conexoes())


def obter_repositorio_vaga() -> VagaRepositoryImpl:
    return VagaRepositoryImpl(obter_pool_conexoes())


def obter_repositorio_candidatura() -> CandidaturaRepositoryImpl:
    return CandidaturaRepositoryImpl(obter_pool_conexoes())


def obter_repositorio_curriculo_salvo() -> CurriculoSalvoRepositoryImpl:
    return CurriculoSalvoRepositoryImpl(obter_pool_conexoes())


def obter_repositorio_perfil() -> PerfilRepositoryImpl:
    return PerfilRepositoryImpl(obter_pool_conexoes())


def obter_repositorio_perfil_estruturado() -> PerfilEstruturadoRepositoryImpl:
    return PerfilEstruturadoRepositoryImpl(obter_pool_conexoes())
