"""Implementação SQLite de CandidaturaRepository."""
from __future__ import annotations

from datetime import datetime

from jobsync.shared_kernel.adapters.persistence._conexao_sqlite import criar_conexao

from jobsync.candidatura.domain.candidatura import Candidatura, MudancaStatus, StatusCandidatura
from jobsync.candidatura.domain.candidatura_repository import (
    CandidaturaNaoEncontrada,
    CandidaturaRepository,
)


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
        self._conexao.execute(
            """
            INSERT INTO candidatura (
                id, perfil_identificador, vaga_id, curriculo_salvo_id,
                empresa, cargo, status, data_aplicacao, data_ultima_mudanca_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        self._conexao.commit()
        return candidatura

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[Candidatura, ...]:
        cursor = self._conexao.execute(
            """
            SELECT id, perfil_identificador, vaga_id, curriculo_salvo_id,
                   empresa, cargo, status, data_aplicacao, data_ultima_mudanca_status
            FROM candidatura
            WHERE perfil_identificador = ?
            ORDER BY data_aplicacao DESC
            """,
            (perfil_identificador,),
        )
        return tuple(self._linha_para_candidatura(linha) for linha in cursor.fetchall())

    def atualizar_status(self, candidatura_id: str, novo_status: StatusCandidatura) -> Candidatura:
        agora = datetime.now()
        cursor_atualizacao = self._conexao.execute(
            "UPDATE candidatura SET status = ?, data_ultima_mudanca_status = ? WHERE id = ?",
            (novo_status.name, agora.isoformat(), candidatura_id),
        )
        self._conexao.commit()
        if cursor_atualizacao.rowcount == 0:
            raise CandidaturaNaoEncontrada(candidatura_id)

        cursor = self._conexao.execute(
            """
            SELECT id, perfil_identificador, vaga_id, curriculo_salvo_id,
                   empresa, cargo, status, data_aplicacao, data_ultima_mudanca_status
            FROM candidatura
            WHERE id = ?
            """,
            (candidatura_id,),
        )
        return self._linha_para_candidatura(cursor.fetchone())

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
        )
