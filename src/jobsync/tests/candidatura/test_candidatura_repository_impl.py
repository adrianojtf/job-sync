"""Testes de integração do CandidaturaRepositoryImpl."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import pytest

from jobsync.candidatura import Candidatura, CandidaturaNaoEncontrada, MudancaStatus, StatusCandidatura
from jobsync.candidatura.adapters import CandidaturaRepositoryImpl
from jobsync.curriculo_salvo import CurriculoSalvo
from jobsync.curriculo_salvo.adapters import CurriculoSalvoRepositoryImpl
from jobsync.perfil.adapters.perfil_repository_impl import PerfilRepositoryImpl
from jobsync.vaga import Vaga
from jobsync.vaga.adapters import VagaRepositoryImpl


@pytest.fixture
def repositorio(pool_postgres):
    PerfilRepositoryImpl(pool_postgres).criar("matheus")
    PerfilRepositoryImpl(pool_postgres).criar("outra-pessoa")
    VagaRepositoryImpl(pool_postgres).salvar(
        Vaga(
            id="vaga-1",
            perfil_identificador="matheus",
            texto_descricao="Vaga",
            url_origem=None,
            data_captura=datetime(2026, 7, 26, tzinfo=timezone.utc),
        )
    )
    CurriculoSalvoRepositoryImpl(pool_postgres).salvar(
        CurriculoSalvo(
            id="curriculo-1",
            perfil_identificador="matheus",
            nome_referencia="curriculo",
            pdf_bytes=b"%PDF",
            data_upload=datetime(2026, 7, 26, tzinfo=timezone.utc),
        )
    )
    return CandidaturaRepositoryImpl(pool_postgres)


def _criar_candidatura(**overrides) -> Candidatura:
    dados = dict(
        id="candidatura-1",
        perfil_identificador="matheus",
        vaga_id="vaga-1",
        curriculo_salvo_id="curriculo-1",
        empresa="TechCorp",
        cargo="Engenheiro de Software",
        status=StatusCandidatura.APLICADO,
        data_aplicacao=datetime(2026, 7, 26, 10, 0, 0, tzinfo=timezone.utc),
        historico_status=(MudancaStatus(status=StatusCandidatura.APLICADO, data=datetime(2026, 7, 26, 10, 0, 0, tzinfo=timezone.utc)),),
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

    def test_atualizar_status_de_candidatura_inexistente_levanta_nao_encontrada(self, repositorio):
        with pytest.raises(CandidaturaNaoEncontrada):
            repositorio.atualizar_status("nao-existe", StatusCandidatura.ENTREVISTA)


def _ids(candidaturas) -> list[str]:
    return [c.id for c in candidaturas]


class TestOrdemDasCandidaturas:
    def test_salvar_insere_no_topo_da_coluna(self, repositorio):
        repositorio.salvar(_criar_candidatura(id="primeira"))
        repositorio.salvar(_criar_candidatura(id="segunda"))

        listadas = repositorio.listar_por_perfil("matheus")

        assert _ids(listadas) == ["segunda", "primeira"]
        assert [c.posicao for c in listadas] == [0, 1]

    def test_salvar_devolve_candidatura_com_posicao_zero(self, repositorio):
        repositorio.salvar(_criar_candidatura(id="primeira"))

        salva = repositorio.salvar(_criar_candidatura(id="segunda"))

        assert salva.posicao == 0

    def test_salvar_nao_altera_posicao_de_outra_coluna(self, repositorio):
        repositorio.salvar(_criar_candidatura(id="entrevista", status=StatusCandidatura.ENTREVISTA))

        repositorio.salvar(_criar_candidatura(id="aplicada"))

        por_id = {c.id: c for c in repositorio.listar_por_perfil("matheus")}
        assert por_id["entrevista"].posicao == 0
        assert por_id["aplicada"].posicao == 0

    def test_buscar_por_id_devolve_candidatura_existente(self, repositorio):
        candidatura = repositorio.salvar(_criar_candidatura())

        assert repositorio.buscar_por_id(candidatura.id) == candidatura

    def test_buscar_por_id_devolve_none_quando_nao_existe(self, repositorio):
        assert repositorio.buscar_por_id("nao-existe") is None


class TestAplicarMovimento:
    @pytest.fixture
    def tres_aplicadas(self, repositorio):
        for id_ in ("c", "b", "a"):
            repositorio.salvar(_criar_candidatura(id=id_))
        return repositorio

    def test_reordena_na_mesma_coluna(self, tres_aplicadas):
        tres_aplicadas.aplicar_movimento("a", StatusCandidatura.APLICADO, ("b", "c", "a"))

        listadas = tres_aplicadas.listar_por_perfil("matheus")

        assert _ids(listadas) == ["b", "c", "a"]
        assert [c.posicao for c in listadas] == [0, 1, 2]

    def test_reordenar_na_mesma_coluna_nao_muda_data_do_status(self, tres_aplicadas):
        antes = tres_aplicadas.buscar_por_id("a").historico_status

        tres_aplicadas.aplicar_movimento("a", StatusCandidatura.APLICADO, ("a", "b", "c"))

        assert tres_aplicadas.buscar_por_id("a").historico_status == antes

    def test_move_para_outra_coluna_na_posicao_informada(self, tres_aplicadas):
        tres_aplicadas.salvar(_criar_candidatura(id="x", status=StatusCandidatura.ENTREVISTA))

        movida = tres_aplicadas.aplicar_movimento("b", StatusCandidatura.ENTREVISTA, ("x", "b"))

        assert movida.status == StatusCandidatura.ENTREVISTA
        assert movida.posicao == 1
        por_id = {c.id: c for c in tres_aplicadas.listar_por_perfil("matheus")}
        assert por_id["x"].posicao == 0

    def test_mudar_de_coluna_registra_nova_data_de_status(self, tres_aplicadas):
        antes = tres_aplicadas.buscar_por_id("b").historico_status[-1].data

        movida = tres_aplicadas.aplicar_movimento("b", StatusCandidatura.OFERTA, ("b",))

        assert movida.historico_status[-1].data > antes

    def test_fecha_o_vazio_na_coluna_de_origem(self, tres_aplicadas):
        tres_aplicadas.aplicar_movimento("c", StatusCandidatura.REJEITADO, ("c",))

        restantes = [c for c in tres_aplicadas.listar_por_perfil("matheus") if c.status == StatusCandidatura.APLICADO]

        assert _ids(restantes) == ["a", "b"]
        assert [c.posicao for c in restantes] == [0, 1]

    def test_candidatura_inexistente_levanta_nao_encontrada(self, repositorio):
        with pytest.raises(CandidaturaNaoEncontrada):
            repositorio.aplicar_movimento("nao-existe", StatusCandidatura.OFERTA, ("nao-existe",))

    def test_inexistente_nao_altera_as_demais(self, tres_aplicadas):
        with pytest.raises(CandidaturaNaoEncontrada):
            tres_aplicadas.aplicar_movimento("nao-existe", StatusCandidatura.OFERTA, ("nao-existe",))

        assert [c.posicao for c in tres_aplicadas.listar_por_perfil("matheus")] == [0, 1, 2]


class TestCurriculoRemovidoEmUso:
    def test_remover_curriculo_usado_por_candidatura_mantem_a_candidatura(self, repositorio, pool_postgres):
        repositorio.salvar(_criar_candidatura(id="c-1"))

        CurriculoSalvoRepositoryImpl(pool_postgres).remover("curriculo-1", "matheus")

        candidatura = repositorio.buscar_por_id("c-1")
        assert candidatura.curriculo_salvo_id == "curriculo-1"


class TestConcorrenciaNoBoard:
    def test_salvamentos_simultaneos_no_mesmo_perfil_geram_posicoes_distintas(self, repositorio):
        def salvar(indice):
            repositorio.salvar(_criar_candidatura(id=f"c-{indice}"))

        with ThreadPoolExecutor(max_workers=6) as executor:
            list(executor.map(salvar, range(6)))

        candidaturas = repositorio.listar_por_perfil("matheus")
        assert sorted(c.posicao for c in candidaturas) == list(range(6))
