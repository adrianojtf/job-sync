"""Implementação SQLite de CurriculoSalvoRepository."""
from __future__ import annotations

from datetime import datetime

from domain.curriculo_salvo import CurriculoSalvo
from domain.curriculo_salvo.curriculo_salvo_repository import CurriculoSalvoRepository
from infrastructure.persistence._conexao_sqlite import criar_conexao


class CurriculoSalvoRepositoryImpl(CurriculoSalvoRepository):
    """Implementação SQLite da porta de biblioteca de currículos salvos."""

    def __init__(self, caminho_banco: str) -> None:
        self._conexao = criar_conexao(caminho_banco)

    def salvar(self, curriculo: CurriculoSalvo) -> CurriculoSalvo:
        self._conexao.execute(
            """
            INSERT INTO curriculo_salvo (id, perfil_identificador, nome_referencia, pdf_bytes, data_upload)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                curriculo.id,
                curriculo.perfil_identificador,
                curriculo.nome_referencia,
                curriculo.pdf_bytes,
                curriculo.data_upload.isoformat(),
            ),
        )
        self._conexao.commit()
        return curriculo

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[CurriculoSalvo, ...]:
        cursor = self._conexao.execute(
            """
            SELECT id, perfil_identificador, nome_referencia, pdf_bytes, data_upload
            FROM curriculo_salvo
            WHERE perfil_identificador = ?
            ORDER BY data_upload DESC
            """,
            (perfil_identificador,),
        )
        return tuple(self._linha_para_curriculo_salvo(linha) for linha in cursor.fetchall())

    def remover(self, curriculo_id: str, perfil_identificador: str) -> None:
        self._conexao.execute(
            "DELETE FROM curriculo_salvo WHERE id = ? AND perfil_identificador = ?",
            (curriculo_id, perfil_identificador),
        )
        self._conexao.commit()

    def contar_por_perfil(self, perfil_identificador: str) -> int:
        cursor = self._conexao.execute(
            "SELECT COUNT(*) FROM curriculo_salvo WHERE perfil_identificador = ?",
            (perfil_identificador,),
        )
        return cursor.fetchone()[0]

    @staticmethod
    def _linha_para_curriculo_salvo(linha: tuple) -> CurriculoSalvo:
        id_, perfil_identificador, nome_referencia, pdf_bytes, data_upload = linha
        return CurriculoSalvo(
            id=id_,
            perfil_identificador=perfil_identificador,
            nome_referencia=nome_referencia,
            pdf_bytes=pdf_bytes,
            data_upload=datetime.fromisoformat(data_upload),
        )
