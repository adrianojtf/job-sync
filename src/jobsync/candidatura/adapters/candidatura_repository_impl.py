"""Implementação SQLite de CandidaturaRepository."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from jobsync.shared_kernel.adapters.persistence._conexao_sqlite import criar_conexao

from jobsync.candidatura.domain.candidatura import Candidatura, MudancaStatus, StatusCandidatura
from jobsync.candidatura.domain.candidatura_repository import (
    CandidaturaNaoEncontrada,
    CandidaturaRepository,
)

_COLUNAS = """id, perfil_identificador, vaga_id, curriculo_salvo_id,
                   empresa, cargo, status, data_aplicacao, data_ultima_mudanca_status, posicao"""


class CandidaturaRepositoryImpl(CandidaturaRepository):
    """Implementação SQLite da porta de candidaturas (Kanban)."""

    def __init__(self, caminho_banco: str) -> None:
        self._conexao = criar_conexao(caminho_banco)

    def salvar(self, candidatura: Candidatura) -> Candidatura:
        data_ultima_mudanca = (
            candidatura.historico_status[-1].data
            if candidatura.historico_status
            else candidatura.data_aplicacao
        )
        with self._conexao:
            self._conexao.execute(
                """
                UPDATE candidatura SET posicao = posicao + 1
                WHERE perfil_identificador = ? AND status = ?
                """,
                (candidatura.perfil_identificador, candidatura.status.name),
            )
            self._conexao.execute(
                """
                INSERT INTO candidatura (
                    id, perfil_identificador, vaga_id, curriculo_salvo_id,
                    empresa, cargo, status, data_aplicacao, data_ultima_mudanca_status, posicao
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    candidatura.id,
                    candidatura.perfil_identificador,
                    candidatura.vaga_id,
                    candidatura.curriculo_salvo_id,
                    candidatura.empresa,
                    candidatura.cargo,
                    candidatura.status.name,
                    candidatura.data_aplicacao.isoformat(),
                    data_ultima_mudanca.isoformat(),
                ),
            )
        return replace(candidatura, posicao=0)

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[Candidatura, ...]:
        cursor = self._conexao.execute(
            f"""
            SELECT {_COLUNAS}
            FROM candidatura
            WHERE perfil_identificador = ?
            ORDER BY posicao ASC, data_aplicacao DESC, id ASC
            """,
            (perfil_identificador,),
        )
        return tuple(self._linha_para_candidatura(linha) for linha in cursor.fetchall())

    def buscar_por_id(self, candidatura_id: str) -> Candidatura | None:
        cursor = self._conexao.execute(
            f"SELECT {_COLUNAS} FROM candidatura WHERE id = ?",
            (candidatura_id,),
        )
        linha = cursor.fetchone()
        return self._linha_para_candidatura(linha) if linha else None

    def atualizar_status(self, candidatura_id: str, novo_status: StatusCandidatura) -> Candidatura:
        atual = self.buscar_por_id(candidatura_id)
        if atual is None:
            raise CandidaturaNaoEncontrada(candidatura_id)
        ids_destino = tuple(
            c.id
            for c in self.listar_por_perfil(atual.perfil_identificador)
            if c.status == novo_status and c.id != candidatura_id
        )
        return self.aplicar_movimento(candidatura_id, novo_status, (candidatura_id, *ids_destino))

    def aplicar_movimento(
        self,
        candidatura_id: str,
        novo_status: StatusCandidatura,
        ids_destino_ordenados: tuple[str, ...],
    ) -> Candidatura:
        atual = self.buscar_por_id(candidatura_id)
        if atual is None:
            raise CandidaturaNaoEncontrada(candidatura_id)

        with self._conexao:
            if atual.status != novo_status:
                self._conexao.execute(
                    "UPDATE candidatura SET status = ?, data_ultima_mudanca_status = ? WHERE id = ?",
                    (novo_status.name, datetime.now().isoformat(), candidatura_id),
                )
            self._gravar_ordem(atual.perfil_identificador, ids_destino_ordenados)
            if atual.status != novo_status:
                self._renumerar_coluna(atual.perfil_identificador, atual.status)

        return self.buscar_por_id(candidatura_id)

    def _gravar_ordem(self, perfil_identificador: str, ids_ordenados: tuple[str, ...]) -> None:
        self._conexao.executemany(
            "UPDATE candidatura SET posicao = ? WHERE id = ? AND perfil_identificador = ?",
            [(indice, id_, perfil_identificador) for indice, id_ in enumerate(ids_ordenados)],
        )

    def _renumerar_coluna(self, perfil_identificador: str, status: StatusCandidatura) -> None:
        cursor = self._conexao.execute(
            """
            SELECT id FROM candidatura
            WHERE perfil_identificador = ? AND status = ?
            ORDER BY posicao ASC, data_aplicacao DESC, id ASC
            """,
            (perfil_identificador, status.name),
        )
        self._gravar_ordem(perfil_identificador, tuple(linha[0] for linha in cursor.fetchall()))

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
        data_mudanca = datetime.fromisoformat(data_ultima_mudanca_status)
        return Candidatura(
            id=id_,
            perfil_identificador=perfil_identificador,
            vaga_id=vaga_id,
            curriculo_salvo_id=curriculo_salvo_id,
            empresa=empresa,
            cargo=cargo,
            status=status_candidatura,
            data_aplicacao=datetime.fromisoformat(data_aplicacao),
            historico_status=(MudancaStatus(status=status_candidatura, data=data_mudanca),),
            posicao=posicao,
        )
