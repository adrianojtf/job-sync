"""Testes do caso de uso MoverCandidatura."""

import logging
from datetime import datetime

import pytest

from jobsync.candidatura import Candidatura, CandidaturaNaoEncontrada, MudancaStatus, StatusCandidatura
from jobsync.candidatura.adapters.candidatura_repository_fake import CandidaturaRepositoryFake
from jobsync.candidatura.service_layer.mover_candidatura import MoverCandidatura


def _criar_candidatura(**overrides) -> Candidatura:
    dados = dict(
        id="candidatura-1",
        perfil_identificador="matheus",
        vaga_id="vaga-1",
        curriculo_salvo_id="curriculo-1",
        empresa="TechCorp",
        cargo="Engenheiro de Software",
        status=StatusCandidatura.APLICADO,
        data_aplicacao=datetime(2026, 7, 26),
        historico_status=(MudancaStatus(status=StatusCandidatura.APLICADO, data=datetime(2026, 7, 26)),),
    )
    dados.update(overrides)
    return Candidatura(**dados)


def _repositorio_com(*candidaturas: Candidatura) -> CandidaturaRepositoryFake:
    repositorio = CandidaturaRepositoryFake()
    for candidatura in reversed(candidaturas):
        repositorio.salvar(candidatura)
    return repositorio


def _ids_da_coluna(repositorio, status, perfil="matheus") -> list[str]:
    return [c.id for c in repositorio.listar_por_perfil(perfil) if c.status == status]


class TestMoverCandidatura:
    def test_atualiza_o_status(self):
        repositorio = _repositorio_com(_criar_candidatura())
        use_case = MoverCandidatura(repositorio_candidatura=repositorio)

        resultado = use_case.executar("candidatura-1", StatusCandidatura.ENTREVISTA)

        assert resultado.status == StatusCandidatura.ENTREVISTA

    def test_aceita_qualquer_transicao_entre_colunas(self):
        repositorio = _repositorio_com(_criar_candidatura(status=StatusCandidatura.OFERTA))
        use_case = MoverCandidatura(repositorio_candidatura=repositorio)

        resultado = use_case.executar("candidatura-1", StatusCandidatura.APLICADO)

        assert resultado.status == StatusCandidatura.APLICADO

    def test_posicao_omitida_coloca_no_topo_da_coluna_de_destino(self):
        repositorio = _repositorio_com(
            _criar_candidatura(id="a"),
            _criar_candidatura(id="x", status=StatusCandidatura.ENTREVISTA),
            _criar_candidatura(id="y", status=StatusCandidatura.ENTREVISTA),
        )
        use_case = MoverCandidatura(repositorio_candidatura=repositorio)

        resultado = use_case.executar("a", StatusCandidatura.ENTREVISTA)

        assert resultado.posicao == 0
        assert _ids_da_coluna(repositorio, StatusCandidatura.ENTREVISTA) == ["a", "x", "y"]

    def test_move_para_a_posicao_informada_em_outra_coluna(self):
        repositorio = _repositorio_com(
            _criar_candidatura(id="a"),
            _criar_candidatura(id="x", status=StatusCandidatura.ENTREVISTA),
            _criar_candidatura(id="y", status=StatusCandidatura.ENTREVISTA),
        )
        use_case = MoverCandidatura(repositorio_candidatura=repositorio)

        resultado = use_case.executar("a", StatusCandidatura.ENTREVISTA, posicao=1)

        assert resultado.posicao == 1
        assert _ids_da_coluna(repositorio, StatusCandidatura.ENTREVISTA) == ["x", "a", "y"]

    def test_reordena_dentro_da_mesma_coluna(self):
        repositorio = _repositorio_com(
            _criar_candidatura(id="a"),
            _criar_candidatura(id="b"),
            _criar_candidatura(id="c"),
        )
        use_case = MoverCandidatura(repositorio_candidatura=repositorio)

        use_case.executar("a", StatusCandidatura.APLICADO, posicao=2)

        assert _ids_da_coluna(repositorio, StatusCandidatura.APLICADO) == ["b", "c", "a"]

    def test_fecha_o_vazio_na_coluna_de_origem(self):
        repositorio = _repositorio_com(_criar_candidatura(id="a"), _criar_candidatura(id="b"))
        use_case = MoverCandidatura(repositorio_candidatura=repositorio)

        use_case.executar("a", StatusCandidatura.OFERTA)

        restante = repositorio.buscar_por_id("b")
        assert restante.posicao == 0

    def test_nao_mexe_nas_candidaturas_de_outro_perfil(self):
        repositorio = _repositorio_com(
            _criar_candidatura(id="a"),
            _criar_candidatura(id="z", perfil_identificador="outra-pessoa"),
        )
        use_case = MoverCandidatura(repositorio_candidatura=repositorio)

        use_case.executar("a", StatusCandidatura.APLICADO, posicao=0)

        assert _ids_da_coluna(repositorio, StatusCandidatura.APLICADO, "outra-pessoa") == ["z"]

    def test_candidatura_inexistente_levanta_nao_encontrada(self):
        use_case = MoverCandidatura(repositorio_candidatura=CandidaturaRepositoryFake())

        with pytest.raises(CandidaturaNaoEncontrada):
            use_case.executar("nao-existe", StatusCandidatura.OFERTA)

    def test_posicao_negativa_levanta_value_error(self):
        repositorio = _repositorio_com(_criar_candidatura())
        use_case = MoverCandidatura(repositorio_candidatura=repositorio)

        with pytest.raises(ValueError):
            use_case.executar("candidatura-1", StatusCandidatura.OFERTA, posicao=-1)

    def test_registra_log_informativo_sem_dados_pessoais(self, caplog):
        repositorio = _repositorio_com(_criar_candidatura())
        use_case = MoverCandidatura(repositorio_candidatura=repositorio)

        with caplog.at_level(logging.INFO):
            use_case.executar("candidatura-1", StatusCandidatura.ENTREVISTA, posicao=0)

        assert "candidatura-1" in caplog.text
        assert "APLICADO" in caplog.text
        assert "ENTREVISTA" in caplog.text
        assert "TechCorp" not in caplog.text
        assert "matheus" not in caplog.text

    def test_posicao_acima_do_tamanho_registra_aviso_e_vai_para_o_fim(self, caplog):
        repositorio = _repositorio_com(_criar_candidatura(id="a"), _criar_candidatura(id="b"))
        use_case = MoverCandidatura(repositorio_candidatura=repositorio)

        with caplog.at_level(logging.WARNING):
            use_case.executar("a", StatusCandidatura.APLICADO, posicao=99)

        assert _ids_da_coluna(repositorio, StatusCandidatura.APLICADO) == ["b", "a"]
        assert "limitada" in caplog.text.lower()
