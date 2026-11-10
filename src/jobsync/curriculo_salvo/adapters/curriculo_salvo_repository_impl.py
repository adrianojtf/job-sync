"""Implementação PostgreSQL de CurriculoSalvoRepository."""
from __future__ import annotations

from psycopg_pool import ConnectionPool

from jobsync.curriculo_salvo.domain.curriculo_salvo import CurriculoSalvo
from jobsync.curriculo_salvo.domain.curriculo_salvo_repository import CurriculoSalvoRepository


class CurriculoSalvoRepositoryImpl(CurriculoSalvoRepository):
    """Implementação PostgreSQL da porta de biblioteca de currículos salvos."""

    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def salvar(self, curriculo: CurriculoSalvo) -> CurriculoSalvo:
        with self._pool.connection() as conexao:
            conexao.execute(
                """
                INSERT INTO curriculo_salvo (id, perfil_identificador, nome_referencia, pdf_bytes, data_upload)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    curriculo.id,
                    curriculo.perfil_identificador,
                    curriculo.nome_referencia,
                    curriculo.pdf_bytes,
                    curriculo.data_upload,
                ),
            )
        return curriculo

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[CurriculoSalvo, ...]:
        with self._pool.connection() as conexao:
            linhas = conexao.execute(
                """
                SELECT id, perfil_identificador, nome_referencia, pdf_bytes, data_upload
                FROM curriculo_salvo
                WHERE perfil_identificador = %s
                ORDER BY data_upload DESC, id COLLATE "C" ASC
                """,
                (perfil_identificador,),
            ).fetchall()
        return tuple(self._linha_para_curriculo_salvo(linha) for linha in linhas)

    def remover(self, curriculo_id: str, perfil_identificador: str) -> None:
        with self._pool.connection() as conexao:
            conexao.execute(
                "DELETE FROM curriculo_salvo WHERE id = %s AND perfil_identificador = %s",
                (curriculo_id, perfil_identificador),
            )

    def contar_por_perfil(self, perfil_identificador: str) -> int:
        with self._pool.connection() as conexao:
            return conexao.execute(
                "SELECT COUNT(*) FROM curriculo_salvo WHERE perfil_identificador = %s",
                (perfil_identificador,),
            ).fetchone()[0]

    @staticmethod
    def _linha_para_curriculo_salvo(linha: tuple) -> CurriculoSalvo:
        id_, perfil_identificador, nome_referencia, pdf_bytes, data_upload = linha
        return CurriculoSalvo(
            id=id_,
            perfil_identificador=perfil_identificador,
            nome_referencia=nome_referencia,
            pdf_bytes=bytes(pdf_bytes),
            data_upload=data_upload,
        )
