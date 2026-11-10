"""Implementação PostgreSQL de VagaRepository."""
from __future__ import annotations

from psycopg_pool import ConnectionPool

from jobsync.vaga.domain.vaga import Vaga
from jobsync.vaga.domain.vaga_repository import VagaRepository


class VagaRepositoryImpl(VagaRepository):
    """Implementação PostgreSQL da porta de vagas capturadas."""

    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def salvar(self, vaga: Vaga) -> Vaga:
        with self._pool.connection() as conexao:
            conexao.execute(
                """
                INSERT INTO vaga (id, perfil_identificador, texto_descricao, url_origem, data_captura, convertida_em_candidatura)
                VALUES (%s, %s, %s, %s, %s, FALSE)
                """,
                (
                    vaga.id,
                    vaga.perfil_identificador,
                    vaga.texto_descricao,
                    vaga.url_origem,
                    vaga.data_captura,
                ),
            )
        return vaga

    def listar_nao_convertidas(self, perfil_identificador: str) -> tuple[Vaga, ...]:
        with self._pool.connection() as conexao:
            linhas = conexao.execute(
                """
                SELECT id, perfil_identificador, texto_descricao, url_origem, data_captura
                FROM vaga
                WHERE perfil_identificador = %s AND NOT convertida_em_candidatura
                ORDER BY data_captura DESC, id COLLATE "C" ASC
                """,
                (perfil_identificador,),
            ).fetchall()
        return tuple(self._linha_para_vaga(linha) for linha in linhas)

    def marcar_como_convertida(self, vaga_id: str) -> None:
        with self._pool.connection() as conexao:
            conexao.execute(
                "UPDATE vaga SET convertida_em_candidatura = TRUE WHERE id = %s",
                (vaga_id,),
            )

    @staticmethod
    def _linha_para_vaga(linha: tuple) -> Vaga:
        id_, perfil_identificador, texto_descricao, url_origem, data_captura = linha
        return Vaga(
            id=id_,
            perfil_identificador=perfil_identificador,
            texto_descricao=texto_descricao,
            url_origem=url_origem,
            data_captura=data_captura,
        )
