"""Testes de integração do VagaRepositoryImpl."""

import os
import tempfile
from datetime import datetime

import pytest

from jobsync.perfil.adapters.perfil_repository_impl import PerfilRepositoryImpl
from jobsync.vaga import Vaga
from jobsync.vaga.adapters import VagaRepositoryImpl


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
    return VagaRepositoryImpl(caminho_banco=caminho_banco)


def _criar_vaga(**overrides) -> Vaga:
    dados = dict(
        id="vaga-1",
        perfil_identificador="matheus",
        texto_descricao="Vaga para Engenheiro de Software",
        data_captura=datetime(2026, 7, 26, 10, 0, 0),
        url_origem="https://exemplo.com/vaga/1",
    )
    dados.update(overrides)
    return Vaga(**dados)


class TestVagaRepositoryImpl:
    def test_salvar_e_listar_nao_convertidas(self, repositorio):
        vaga = _criar_vaga()

        repositorio.salvar(vaga)

        assert repositorio.listar_nao_convertidas("matheus") == (vaga,)

    def test_marcar_como_convertida_remove_da_listagem(self, repositorio):
        vaga = _criar_vaga()
        repositorio.salvar(vaga)

        repositorio.marcar_como_convertida(vaga.id)

        assert repositorio.listar_nao_convertidas("matheus") == ()

    def test_isolamento_entre_perfis_diferentes(self, repositorio):
        vaga_matheus = _criar_vaga(id="vaga-matheus", perfil_identificador="matheus")
        vaga_outra = _criar_vaga(id="vaga-outra", perfil_identificador="outra-pessoa")

        repositorio.salvar(vaga_matheus)
        repositorio.salvar(vaga_outra)

        assert repositorio.listar_nao_convertidas("matheus") == (vaga_matheus,)
        assert repositorio.listar_nao_convertidas("outra-pessoa") == (vaga_outra,)

    def test_ordena_por_data_captura_decrescente(self, repositorio):
        mais_antiga = _criar_vaga(id="vaga-antiga", data_captura=datetime(2026, 1, 1))
        mais_recente = _criar_vaga(id="vaga-recente", data_captura=datetime(2026, 6, 1))

        repositorio.salvar(mais_antiga)
        repositorio.salvar(mais_recente)

        assert repositorio.listar_nao_convertidas("matheus") == (mais_recente, mais_antiga)
