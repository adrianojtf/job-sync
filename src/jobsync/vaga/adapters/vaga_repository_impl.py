"""Implementação SQLite de VagaRepository."""
from __future__ import annotations

from datetime import datetime

from infrastructure.persistence._conexao_sqlite import criar_conexao

from jobsync.vaga.domain.vaga import Vaga
from jobsync.vaga.domain.vaga_repository import VagaRepository


class VagaRepositoryImpl(VagaRepository):
    """Implementação SQLite da porta de vagas capturadas."""

    def __init__(self, caminho_banco: str) -> None:
        self._conexao = criar_conexao(caminho_banco)

    def salvar(self, vaga: Vaga) -> Vaga:
        self._conexao.execute(
            """
            INSERT INTO vaga (id, perfil_identificador, texto_descricao, url_origem, data_captura, convertida_em_candidatura)
            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (
                vaga.id,
                vaga.perfil_identificador,
                vaga.texto_descricao,
                vaga.url_origem,
                vaga.data_captura.isoformat(),
            ),
        )
        self._conexao.commit()
        return vaga

    def listar_nao_convertidas(self, perfil_identificador: str) -> tuple[Vaga, ...]:
        cursor = self._conexao.execute(
            """
            SELECT id, perfil_identificador, texto_descricao, url_origem, data_captura
            FROM vaga
            WHERE perfil_identificador = ? AND convertida_em_candidatura = 0
            ORDER BY data_captura DESC
            """,
            (perfil_identificador,),
        )
        return tuple(self._linha_para_vaga(linha) for linha in cursor.fetchall())

    def marcar_como_convertida(self, vaga_id: str) -> None:
        self._conexao.execute(
            "UPDATE vaga SET convertida_em_candidatura = 1 WHERE id = ?",
            (vaga_id,),
        )
        self._conexao.commit()

    @staticmethod
    def _linha_para_vaga(linha: tuple) -> Vaga:
        id_, perfil_identificador, texto_descricao, url_origem, data_captura = linha
        return Vaga(
            id=id_,
            perfil_identificador=perfil_identificador,
            texto_descricao=texto_descricao,
            url_origem=url_origem,
            data_captura=datetime.fromisoformat(data_captura),
        )
