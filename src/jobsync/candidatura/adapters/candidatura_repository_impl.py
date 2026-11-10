"""Implementação PostgreSQL de CandidaturaRepository."""
from __future__ import annotations

from dataclasses import replace

from psycopg import Connection
from psycopg_pool import ConnectionPool

from jobsync.shared_kernel.domain.relogio import agora_utc

from jobsync.candidatura.domain.candidatura import Candidatura, MudancaStatus, StatusCandidatura
from jobsync.candidatura.domain.candidatura_repository import (
    CandidaturaNaoEncontrada,
    CandidaturaRepository,
)

_COLUNAS = """id, perfil_identificador, vaga_id, curriculo_salvo_id,
                   empresa, cargo, status, data_aplicacao, data_ultima_mudanca_status, posicao"""
_ORDEM_DA_COLUNA = 'ORDER BY posicao ASC, data_aplicacao DESC, id COLLATE "C" ASC'


class CandidaturaRepositoryImpl(CandidaturaRepository):
    """Implementação PostgreSQL da porta de candidaturas (Kanban).

    Toda operação que reordena cartões toma um lock por perfil na transação,
    para que escritas simultâneas do mesmo board não produzam posições repetidas.
    """

    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def salvar(self, candidatura: Candidatura) -> Candidatura:
        data_ultima_mudanca = (
            candidatura.historico_status[-1].data
            if candidatura.historico_status
            else candidatura.data_aplicacao
        )
        with self._pool.connection() as conexao:
            self._travar_perfil(conexao, candidatura.perfil_identificador)
            conexao.execute(
                """
                UPDATE candidatura SET posicao = posicao + 1
                WHERE perfil_identificador = %s AND status = %s
                """,
                (candidatura.perfil_identificador, candidatura.status.name),
            )
            conexao.execute(
                """
                INSERT INTO candidatura (
                    id, perfil_identificador, vaga_id, curriculo_salvo_id,
                    empresa, cargo, status, data_aplicacao, data_ultima_mudanca_status, posicao
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
                """,
                (
                    candidatura.id,
                    candidatura.perfil_identificador,
                    candidatura.vaga_id,
                    candidatura.curriculo_salvo_id,
                    candidatura.empresa,
                    candidatura.cargo,
                    candidatura.status.name,
                    candidatura.data_aplicacao,
                    data_ultima_mudanca,
                ),
            )
        return replace(candidatura, posicao=0)

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[Candidatura, ...]:
        with self._pool.connection() as conexao:
            return self._listar(conexao, perfil_identificador)

    def buscar_por_id(self, candidatura_id: str) -> Candidatura | None:
        with self._pool.connection() as conexao:
            return self._buscar(conexao, candidatura_id)

    def atualizar_status(self, candidatura_id: str, novo_status: StatusCandidatura) -> Candidatura:
        with self._pool.connection() as conexao:
            atual = self._buscar_travando_perfil(conexao, candidatura_id)
            ids_destino = tuple(
                c.id
                for c in self._listar(conexao, atual.perfil_identificador)
                if c.status == novo_status and c.id != candidatura_id
            )
            return self._mover(conexao, atual, novo_status, (candidatura_id, *ids_destino))

    def aplicar_movimento(
        self,
        candidatura_id: str,
        novo_status: StatusCandidatura,
        ids_destino_ordenados: tuple[str, ...],
    ) -> Candidatura:
        with self._pool.connection() as conexao:
            atual = self._buscar_travando_perfil(conexao, candidatura_id)
            return self._mover(conexao, atual, novo_status, ids_destino_ordenados)

    def _mover(
        self,
        conexao: Connection,
        atual: Candidatura,
        novo_status: StatusCandidatura,
        ids_destino_ordenados: tuple[str, ...],
    ) -> Candidatura:
        if atual.status != novo_status:
            conexao.execute(
                "UPDATE candidatura SET status = %s, data_ultima_mudanca_status = %s WHERE id = %s",
                (novo_status.name, agora_utc(), atual.id),
            )
        self._gravar_ordem(conexao, atual.perfil_identificador, ids_destino_ordenados)
        if atual.status != novo_status:
            self._renumerar_coluna(conexao, atual.perfil_identificador, atual.status)
        return self._buscar(conexao, atual.id)

    @staticmethod
    def _travar_perfil(conexao: Connection, perfil_identificador: str) -> None:
        conexao.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (perfil_identificador,))

    def _buscar_travando_perfil(self, conexao: Connection, candidatura_id: str) -> Candidatura:
        linha = conexao.execute(
            "SELECT perfil_identificador FROM candidatura WHERE id = %s", (candidatura_id,)
        ).fetchone()
        if linha is None:
            raise CandidaturaNaoEncontrada(candidatura_id)
        self._travar_perfil(conexao, linha[0])
        atual = self._buscar(conexao, candidatura_id)
        if atual is None:
            raise CandidaturaNaoEncontrada(candidatura_id)
        return atual

    def _listar(self, conexao: Connection, perfil_identificador: str) -> tuple[Candidatura, ...]:
        linhas = conexao.execute(
            f"SELECT {_COLUNAS} FROM candidatura WHERE perfil_identificador = %s {_ORDEM_DA_COLUNA}",
            (perfil_identificador,),
        ).fetchall()
        return tuple(self._linha_para_candidatura(linha) for linha in linhas)

    def _buscar(self, conexao: Connection, candidatura_id: str) -> Candidatura | None:
        linha = conexao.execute(
            f"SELECT {_COLUNAS} FROM candidatura WHERE id = %s",
            (candidatura_id,),
        ).fetchone()
        return self._linha_para_candidatura(linha) if linha else None

    @staticmethod
    def _gravar_ordem(conexao: Connection, perfil_identificador: str, ids_ordenados: tuple[str, ...]) -> None:
        with conexao.cursor() as cursor:
            cursor.executemany(
                "UPDATE candidatura SET posicao = %s WHERE id = %s AND perfil_identificador = %s",
                [(indice, id_, perfil_identificador) for indice, id_ in enumerate(ids_ordenados)],
            )

    def _renumerar_coluna(self, conexao: Connection, perfil_identificador: str, status: StatusCandidatura) -> None:
        linhas = conexao.execute(
            f"SELECT id FROM candidatura WHERE perfil_identificador = %s AND status = %s {_ORDEM_DA_COLUNA}",
            (perfil_identificador, status.name),
        ).fetchall()
        self._gravar_ordem(conexao, perfil_identificador, tuple(linha[0] for linha in linhas))

    @staticmethod
    def _linha_para_candidatura(linha: tuple) -> Candidatura:
        (
            id_,
            perfil_identificador,
            vaga_id,
            curriculo_salvo_id,
            empresa,
            cargo,
            status,
            data_aplicacao,
            data_ultima_mudanca_status,
            posicao,
        ) = linha
        status_candidatura = StatusCandidatura[status]
        return Candidatura(
            id=id_,
            perfil_identificador=perfil_identificador,
            vaga_id=vaga_id,
            curriculo_salvo_id=curriculo_salvo_id,
            empresa=empresa,
            cargo=cargo,
            status=status_candidatura,
            data_aplicacao=data_aplicacao,
            historico_status=(MudancaStatus(status=status_candidatura, data=data_ultima_mudanca_status),),
            posicao=posicao,
        )
