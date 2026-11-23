"""Testes do caso de uso IdentificarLacunasDaVaga."""
import logging

import pytest

from jobsync.curriculo import ContextoVaga, ExperienciaParaAvaliacao
from jobsync.curriculo.domain.identificador_lacunas_port import IdentificadorLacunasPort
from jobsync.curriculo.domain.lacuna_da_vaga import HistoricoDoCandidato, LacunaDaVaga
from jobsync.curriculo.service_layer.identificar_lacunas_da_vaga import (
    IdentificarLacunasDaVaga,
    IdentificarLacunasDaVagaInputDto,
)
from jobsync.vaga import AnaliseVaga


class IdentificadorFake(IdentificadorLacunasPort):
    def __init__(self, lacunas: tuple[LacunaDaVaga, ...] = (), erro: Exception | None = None):
        self._lacunas = lacunas
        self._erro = erro
        self.chamadas: list[tuple[HistoricoDoCandidato, ContextoVaga]] = []

    def identificar(self, historico: HistoricoDoCandidato, contexto: ContextoVaga) -> tuple[LacunaDaVaga, ...]:
        self.chamadas.append((historico, contexto))
        if self._erro is not None:
            raise self._erro
        return self._lacunas


def _contexto() -> ContextoVaga:
    return ContextoVaga(
        descricao_vaga="Vaga de FDE",
        idioma_alvo="pt",
        analise_vaga=AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="Vaga de FDE"),
        cargo_alvo="Forward Deployed Engineer",
    )


def _historico(com_experiencias: bool = True) -> HistoricoDoCandidato:
    experiencias = (
        (ExperienciaParaAvaliacao(descricao="APIs.", cargo="Dev", empresa="TechCorp", periodo="2020"),)
        if com_experiencias
        else ()
    )
    return HistoricoDoCandidato(resumo="Backend.", experiencias=experiencias, tecnologias=("Java",))


def _entrada(historico: HistoricoDoCandidato | None = None) -> IdentificarLacunasDaVagaInputDto:
    return IdentificarLacunasDaVagaInputDto(historico=historico or _historico(), contexto=_contexto())


def _lacunas(quantidade: int) -> tuple[LacunaDaVaga, ...]:
    return tuple(LacunaDaVaga(tema=f"Tema {n}", pergunta=f"Você já fez o tema {n}?") for n in range(quantidade))


class TestIdentificarLacunasDaVaga:
    def test_devolve_as_lacunas_da_porta(self):
        identificador = IdentificadorFake(_lacunas(3))

        resultado = IdentificarLacunasDaVaga(identificador).executar(_entrada())

        assert resultado == _lacunas(3)

    def test_entrega_o_historico_e_o_contexto_a_porta(self):
        identificador = IdentificadorFake(_lacunas(1))
        entrada = _entrada()

        IdentificarLacunasDaVaga(identificador).executar(entrada)

        assert identificador.chamadas == [(entrada.historico, entrada.contexto)]

    def test_limita_a_5_lacunas_mesmo_que_a_ia_devolva_mais(self):
        identificador = IdentificadorFake(_lacunas(9))

        resultado = IdentificarLacunasDaVaga(identificador).executar(_entrada())

        assert resultado == _lacunas(9)[:5]

    @pytest.mark.parametrize("erro", [RuntimeError("falha"), ValueError("formato")])
    def test_falha_da_ia_vira_sem_lacunas_e_registra_aviso(self, erro, caplog):
        identificador = IdentificadorFake(erro=erro)

        with caplog.at_level(logging.WARNING):
            resultado = IdentificarLacunasDaVaga(identificador).executar(_entrada())

        assert resultado == ()
        assert "indisponível" in " ".join(r.getMessage() for r in caplog.records)

    def test_historico_sem_experiencias_nao_chama_a_ia(self):
        identificador = IdentificadorFake(_lacunas(2))

        resultado = IdentificarLacunasDaVaga(identificador).executar(_entrada(_historico(com_experiencias=False)))

        assert resultado == ()
        assert identificador.chamadas == []

    def test_registra_quantas_lacunas_sem_o_texto(self, caplog):
        identificador = IdentificadorFake(_lacunas(2))

        with caplog.at_level(logging.INFO):
            IdentificarLacunasDaVaga(identificador).executar(_entrada())

        mensagens = " ".join(r.getMessage() for r in caplog.records)
        assert "lacunas=2" in mensagens
        assert "Tema 0" not in mensagens
