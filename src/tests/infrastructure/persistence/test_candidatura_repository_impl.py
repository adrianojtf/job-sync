"""Testes de integração do CandidaturaRepositoryImpl."""

import os
import tempfile
from datetime import datetime

import pytest

from domain.candidatura import Candidatura, MudancaStatus, StatusCandidatura
from infrastructure.persistence.candidatura_repository_impl import CandidaturaRepositoryImpl
from infrastructure.persistence.perfil_repository_impl import PerfilRepositoryImpl


@pytest.fixture
def caminho_banco():
    fd, caminho = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield caminho
    os.remove(caminho)


@pytest.fixture
def repositorio(caminho_banco):
    PerfilRepositoryImpl(caminho_banco=caminho_banco).criar("matheus")
    PerfilRepositoryImpl(caminho_banco=caminho_banco).criar("outra-pessoa")
    return CandidaturaRepositoryImpl(caminho_banco=caminho_banco)


def _criar_candidatura(**overrides) -> Candidatura:
    dados = dict(
        id="candidatura-1",
        perfil_identificador="matheus",
        vaga_id="vaga-1",
        curriculo_salvo_id="curriculo-1",
        empresa="TechCorp",
        cargo="Engenheiro de Software",
        status=StatusCandidatura.APLICADO,
        data_aplicacao=datetime(2026, 7, 26, 10, 0, 0),
        historico_status=(MudancaStatus(status=StatusCandidatura.APLICADO, data=datetime(2026, 7, 26, 10, 0, 0)),),
    )
    dados.update(overrides)
    return Candidatura(**dados)


class TestCandidaturaRepositoryImpl:
    def test_salvar_e_listar_por_perfil(self, repositorio):
        candidatura = _criar_candidatura()

        repositorio.salvar(candidatura)

        assert repositorio.listar_por_perfil("matheus") == (candidatura,)

    def test_atualizar_status_persiste_mudanca(self, repositorio):
        candidatura = _criar_candidatura()
        repositorio.salvar(candidatura)

        atualizada = repositorio.atualizar_status(candidatura.id, StatusCandidatura.ENTREVISTA)

        assert atualizada.status == StatusCandidatura.ENTREVISTA
        listadas = repositorio.listar_por_perfil("matheus")
        assert listadas[0].status == StatusCandidatura.ENTREVISTA

    def test_isolamento_entre_perfis_diferentes(self, repositorio):
        candidatura_matheus = _criar_candidatura(id="c-matheus", perfil_identificador="matheus")
        candidatura_outra = _criar_candidatura(id="c-outra", perfil_identificador="outra-pessoa")

        repositorio.salvar(candidatura_matheus)
        repositorio.salvar(candidatura_outra)

        assert repositorio.listar_por_perfil("matheus") == (candidatura_matheus,)
        assert repositorio.listar_por_perfil("outra-pessoa") == (candidatura_outra,)
