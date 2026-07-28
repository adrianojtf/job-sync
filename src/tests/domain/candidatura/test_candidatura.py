"""Testes das entidades de domínio Candidatura, StatusCandidatura e MudancaStatus."""

from datetime import datetime

import pytest

from domain.candidatura import Candidatura, MudancaStatus, StatusCandidatura


def _criar_candidatura(**overrides) -> Candidatura:
    dados = dict(
        id="uuid-1",
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


class TestCandidatura:
    def test_cria_candidatura_valida(self):
        candidatura = _criar_candidatura()

        assert candidatura.status == StatusCandidatura.APLICADO
        assert candidatura.empresa == "TechCorp"

    def test_id_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            _criar_candidatura(id="")

    def test_empresa_vazia_gera_erro(self):
        with pytest.raises(ValueError):
            _criar_candidatura(empresa="")

    def test_cargo_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            _criar_candidatura(cargo="   ")

    def test_status_candidatura_possui_quatro_estagios(self):
        assert {s.name for s in StatusCandidatura} == {"APLICADO", "ENTREVISTA", "OFERTA", "REJEITADO"}
