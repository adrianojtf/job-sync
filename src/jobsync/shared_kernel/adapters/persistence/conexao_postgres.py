"""Pool de conexões PostgreSQL compartilhado pelos *RepositoryImpl.

Os RepositoryImpl são classes separadas (uma por Repository) em vez de uma única
classe implementando todas as portas, porque `CurriculoSalvoRepository`,
`VagaRepository` e `CandidaturaRepository` declaram métodos com o mesmo nome
(`salvar`, `listar_por_perfil`) para tipos de domínio diferentes — Python não
suporta sobrecarga por tipo de parâmetro. Todas recebem o mesmo pool.

As sessões trabalham em UTC: instantes são gravados em `TIMESTAMPTZ` e lidos
como `datetime` com fuso. Quem exibe a data (o navegador) aplica o fuso do
usuário.
"""
from __future__ import annotations

import logging
import os

from psycopg.conninfo import conninfo_to_dict
from psycopg_pool import ConnectionPool, PoolTimeout

logger = logging.getLogger(__name__)

VARIAVEL_URL_BANCO = "DATABASE_URL"
_TIMEOUT_CONEXAO_SEGUNDOS = 10.0


class ErroConexaoBanco(RuntimeError):
    """A configuração do banco está ausente ou o PostgreSQL não está acessível."""


def obter_url_banco() -> str:
    url = os.getenv(VARIAVEL_URL_BANCO, "").strip()
    if not url:
        raise ErroConexaoBanco(
            f"A variável {VARIAVEL_URL_BANCO} não está definida. "
            "Exemplo: postgresql://usuario:senha@localhost:5432/job_sync"
        )
    return url


def descrever_destino(url: str) -> str:
    """Host, porta e banco da URL, sem usuário nem senha, para logs e mensagens."""
    partes = conninfo_to_dict(url)
    return f"{partes.get('host', 'localhost')}:{partes.get('port', 5432)}/{partes.get('dbname', '')}"


def criar_pool(url: str, tamanho_maximo: int = 10) -> ConnectionPool:
    """Abre o pool e falha rápido, sem expor credenciais, se o banco não responder."""
    pool = ConnectionPool(
        url,
        min_size=1,
        max_size=tamanho_maximo,
        kwargs={"options": "-c TimeZone=UTC"},
        open=False,
    )
    try:
        pool.open(wait=True, timeout=_TIMEOUT_CONEXAO_SEGUNDOS)
    except PoolTimeout as erro:
        pool.close()
        raise ErroConexaoBanco(
            f"Não foi possível conectar ao PostgreSQL em {descrever_destino(url)}. "
            "Confira se o servidor está no ar e se usuário, senha e banco estão corretos."
        ) from erro
    logger.info("Pool PostgreSQL aberto em %s (máximo de %d conexões)", descrever_destino(url), tamanho_maximo)
    return pool
