"""Testes das entidades de domínio Candidatura, StatusCandidatura e MudancaStatus."""

import uuid
from datetime import datetime

import pytest

from jobsync.candidatura import Candidatura, MudancaStatus, StatusCandidatura


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


class TestCandidaturaNova:
    @staticmethod
    def _nova(**overrides) -> Candidatura:
        dados = dict(
            perfil_identificador="matheus",
            vaga_id="vaga-1",
            curriculo_salvo_id="curriculo-1",
            empresa="TechCorp",
            cargo="Engenheiro de Software",
            agora=datetime(2026, 11, 9, 10, 30),
        )
        dados.update(overrides)
        return Candidatura.nova(**dados)

    def test_nasce_com_status_aplicado_e_data_de_aplicacao_igual_a_agora(self):
        candidatura = self._nova()

        assert candidatura.status == StatusCandidatura.APLICADO
        assert candidatura.data_aplicacao == datetime(2026, 11, 9, 10, 30)

    def test_historico_inicial_tem_uma_mudanca_para_aplicado_na_mesma_data(self):
        candidatura = self._nova()

        assert candidatura.historico_status == (
            MudancaStatus(status=StatusCandidatura.APLICADO, data=datetime(2026, 11, 9, 10, 30)),
        )

    def test_guarda_os_identificadores_e_os_dados_informados(self):
        candidatura = self._nova()

        assert candidatura.perfil_identificador == "matheus"
        assert candidatura.vaga_id == "vaga-1"
        assert candidatura.curriculo_salvo_id == "curriculo-1"
        assert candidatura.empresa == "TechCorp"
        assert candidatura.cargo == "Engenheiro de Software"

    def test_gera_um_id_uuid_diferente_a_cada_candidatura(self):
        primeira = self._nova()
        segunda = self._nova()

        assert primeira.id != segunda.id
        assert str(uuid.UUID(primeira.id)) == primeira.id

    @pytest.mark.parametrize("campo", ["empresa", "cargo", "perfil_identificador"])
    def test_campo_obrigatorio_em_branco_gera_erro(self, campo):
        with pytest.raises(ValueError):
            self._nova(**{campo: "  "})


class TestPosicaoDaCandidatura:
    def test_posicao_padrao_eh_zero(self):
        assert _criar_candidatura().posicao == 0

    def test_aceita_posicao_positiva(self):
        assert _criar_candidatura(posicao=3).posicao == 3

    def test_posicao_negativa_levanta_value_error(self):
        with pytest.raises(ValueError):
            _criar_candidatura(posicao=-1)
