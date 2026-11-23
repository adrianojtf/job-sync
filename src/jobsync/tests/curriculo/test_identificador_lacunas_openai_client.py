"""Testes do adapter IdentificadorLacunasOpenAIClient."""
from unittest.mock import Mock

import pytest

from jobsync.curriculo import ContextoVaga, ExperienciaParaAvaliacao
from jobsync.curriculo.adapters.identificador_lacunas_openai_client import IdentificadorLacunasOpenAIClient
from jobsync.curriculo.domain.lacuna_da_vaga import HistoricoDoCandidato, LacunaDaVaga
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI
from jobsync.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)

RESPOSTA = {
    "lacunas": [
        {"tema": "Atuação junto ao cliente", "pergunta": "Você já atuou junto ao cliente na entrega de uma solução?"},
        {"tema": "Construção de MVPs", "pergunta": "Você já construiu um MVP do zero?"},
    ]
}


def _cliente(resposta: dict) -> Mock:
    cliente = Mock(spec=ClienteOpenAI)
    cliente.solicitar_json.return_value = resposta
    return cliente


def _contexto(cargo_alvo: str = "Forward Deployed Engineer", com_requisitos: bool = True) -> ContextoVaga:
    requisitos = (
        (
            RequisitoTecnico(
                nome="Python",
                categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
                tipo=TipoRequisitoTecnico.EXPLICITO,
                origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
            ),
        )
        if com_requisitos
        else ()
    )
    analise = AnaliseVaga(requisitos=requisitos, ambiguidade=(), texto_original="Vaga de FDE")
    return ContextoVaga(
        descricao_vaga="Atuar junto ao cliente e construir MVPs.",
        idioma_alvo="en",
        analise_vaga=analise,
        cargo_alvo=cargo_alvo,
    )


def _historico() -> HistoricoDoCandidato:
    experiencia = ExperienciaParaAvaliacao(
        descricao="Backend em Java.",
        cargo="Engenheiro de Software",
        empresa="TechCorp",
        periodo="2020 - Atual",
        conquistas=("Reduzi o tempo de deploy.",),
    )
    return HistoricoDoCandidato(
        resumo="Engenheiro backend com foco em integrações.", experiencias=(experiencia,), tecnologias=("Java", "PostgreSQL")
    )


def _identificar(cliente: Mock, cargo_alvo: str = "Forward Deployed Engineer", com_requisitos: bool = True):
    return IdentificadorLacunasOpenAIClient(cliente).identificar(
        _historico(), _contexto(cargo_alvo, com_requisitos)
    )


class TestIdentificadorLacunasOpenAIClient:
    def test_devolve_as_lacunas_da_resposta(self):
        resultado = _identificar(_cliente(RESPOSTA))

        assert resultado == (
            LacunaDaVaga("Atuação junto ao cliente", "Você já atuou junto ao cliente na entrega de uma solução?"),
            LacunaDaVaga("Construção de MVPs", "Você já construiu um MVP do zero?"),
        )

    def test_resposta_sem_lacunas_devolve_tupla_vazia(self):
        assert _identificar(_cliente({"lacunas": []})) == ()

    def test_prompt_do_usuario_traz_a_vaga_o_cargo_alvo_e_os_requisitos(self):
        cliente = _cliente(RESPOSTA)

        _identificar(cliente)

        usuario = cliente.solicitar_json.call_args.kwargs["prompt_usuario"]
        assert "Cargo-alvo (título da vaga): Forward Deployed Engineer" in usuario
        assert "Atuar junto ao cliente e construir MVPs." in usuario
        assert "Requisitos técnicos da vaga: Python" in usuario

    def test_sem_requisitos_analisados_o_prompt_nao_traz_a_linha_de_requisitos(self):
        cliente = _cliente(RESPOSTA)

        _identificar(cliente, com_requisitos=False)

        assert "Requisitos técnicos da vaga" not in cliente.solicitar_json.call_args.kwargs["prompt_usuario"]

    def test_prompt_do_usuario_traz_o_historico_do_candidato_com_as_conquistas(self):
        cliente = _cliente(RESPOSTA)

        _identificar(cliente)

        usuario = cliente.solicitar_json.call_args.kwargs["prompt_usuario"]
        assert "Engenheiro backend com foco em integrações." in usuario
        assert "Engenheiro de Software - TechCorp (2020 - Atual)" in usuario
        assert "Backend em Java." in usuario
        assert "- Reduzi o tempo de deploy." in usuario
        assert "Tecnologias do perfil: Java, PostgreSQL" in usuario

    def test_prompt_de_sistema_define_as_regras_das_perguntas(self):
        cliente = _cliente(RESPOSTA)

        _identificar(cliente)

        sistema = cliente.solicitar_json.call_args.kwargs["prompt_sistema"].lower()
        assert "no máximo 5" in sistema
        assert "não pergunte o que o histórico já sustenta" in sistema
        assert "ordene do tema mais central" in sistema
        assert "pergunta fechada" in sistema
        assert "português do brasil" in sistema
        assert '"lacunas"' in sistema

    def test_prompt_nao_pede_idioma_da_vaga_para_as_perguntas(self):
        cliente = _cliente(RESPOSTA)

        _identificar(cliente)

        usuario = cliente.solicitar_json.call_args.kwargs["prompt_usuario"]
        assert "inglês" not in usuario.lower()

    def test_sem_cargo_alvo_o_prompt_nao_cita_o_cargo_alvo(self):
        cliente = _cliente(RESPOSTA)

        _identificar(cliente, cargo_alvo="")

        assert "Cargo-alvo" not in cliente.solicitar_json.call_args.kwargs["prompt_usuario"]

    @pytest.mark.parametrize(
        "resposta",
        [
            {},
            {"lacunas": "texto"},
            {"lacunas": [{"tema": "Só tema"}]},
            {"lacunas": [{"tema": "", "pergunta": "Você já?"}]},
            {"lacunas": ["Tema solto"]},
            {"lacunas": [{"tema": 1, "pergunta": "Você já?"}]},
        ],
    )
    def test_resposta_fora_do_formato_gera_erro(self, resposta):
        with pytest.raises(ValueError):
            _identificar(_cliente(resposta))
