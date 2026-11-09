"""Testes do adapter AjustadorExperienciaOpenAIClient."""
from unittest.mock import Mock

import pytest

from jobsync.curriculo import ContextoVaga, ExperienciaAdaptada, ExperienciaParaAvaliacao
from jobsync.curriculo.adapters.ajustador_experiencia_openai_client import (
    AjustadorExperienciaOpenAIClient,
)
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI
from jobsync.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)

RESPOSTA = {
    "conquistas": ["Desenvolvi APIs em Java.", "Reduzi o tempo de resposta em 40%."],
    "contexto": "Na TechCorp, atuei na plataforma de pagamentos.",
}


def _cliente(resposta: dict) -> Mock:
    cliente = Mock(spec=ClienteOpenAI)
    cliente.solicitar_json.return_value = resposta
    return cliente


def _analise() -> AnaliseVaga:
    return AnaliseVaga(
        requisitos=(
            RequisitoTecnico(
                nome="Java",
                categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
                tipo=TipoRequisitoTecnico.EXPLICITO,
                origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
            ),
            RequisitoTecnico(
                nome="Trabalho em equipe",
                categoria=CategoriaRequisitoTecnico.HABILIDADE,
                tipo=TipoRequisitoTecnico.IMPLICITO,
                origem=OrigemRequisitoTecnico.INTERPRETACAO,
            ),
        ),
        ambiguidade=(),
        texto_original="Vaga Java sênior",
    )


def _original(descricao: str = "Fiz APIs em Java.") -> ExperienciaParaAvaliacao:
    return ExperienciaParaAvaliacao(
        cargo="Dev", empresa="TechCorp", periodo="2022 - Atual", descricao=descricao
    )


def _atual() -> ExperienciaAdaptada:
    return ExperienciaAdaptada(
        cargo="Dev",
        empresa="TechCorp",
        periodo="2022 - Atual",
        conquistas=("Criei APIs.", "Reduzi custos."),
        contexto="Empresa de pagamentos.",
    )


def _contexto(idioma: str = "pt", cargo_alvo: str = "") -> ContextoVaga:
    return ContextoVaga(
        descricao_vaga="Vaga Java sênior",
        idioma_alvo=idioma,
        analise_vaga=_analise(),
        cargo_alvo=cargo_alvo,
    )


def _ajustar(
    cliente: Mock, descricao: str = "Fiz APIs em Java.", idioma: str = "pt", cargo_alvo: str = ""
):
    return AjustadorExperienciaOpenAIClient(cliente).ajustar(
        experiencia=_original(descricao),
        contexto=_contexto(idioma, cargo_alvo),
    )


def _refinar(cliente: Mock, idioma: str = "pt", cargo_alvo: str = ""):
    return AjustadorExperienciaOpenAIClient(cliente).refinar(
        experiencia=_atual(),
        contexto=_contexto(idioma, cargo_alvo),
    )


class TestAjustadorExperienciaOpenAIClientAjustar:
    def test_devolve_conquistas_e_contexto_preservando_cargo_empresa_e_periodo(self):
        resultado = _ajustar(_cliente(RESPOSTA))

        assert resultado == ExperienciaAdaptada(
            cargo="Dev",
            empresa="TechCorp",
            periodo="2022 - Atual",
            conquistas=("Desenvolvi APIs em Java.", "Reduzi o tempo de resposta em 40%."),
            contexto="Na TechCorp, atuei na plataforma de pagamentos.",
        )

    def test_prompt_de_sistema_define_o_padrao_de_conquistas_e_contexto(self):
        cliente = _cliente(RESPOSTA)

        _ajustar(cliente)

        sistema = cliente.solicitar_json.call_args.kwargs["prompt_sistema"].lower()
        assert "de 2 a 6" in sistema
        assert "verbo de ação" in sistema
        assert "contexto" in sistema
        assert "de 1 a 3 frases" in sistema
        assert "plausíveis" in sistema
        assert "não altere cargo, empresa nem período" in sistema
        assert '"conquistas"' in sistema

    def test_prompt_do_usuario_traz_a_experiencia_a_vaga_os_requisitos_e_o_idioma(self):
        cliente = _cliente(RESPOSTA)

        _ajustar(cliente, idioma="en")

        usuario = cliente.solicitar_json.call_args.kwargs["prompt_usuario"]
        assert "Fiz APIs em Java." in usuario
        assert "Vaga Java sênior" in usuario
        assert "Requisitos explícitos da vaga: Java" in usuario
        assert "Requisitos implícitos da vaga: Trabalho em equipe" in usuario
        assert "inglês" in usuario

    def test_descricao_em_branco_nao_chama_a_ia_nem_inventa_conteudo(self):
        cliente = _cliente(RESPOSTA)

        resultado = _ajustar(cliente, descricao="  ")

        cliente.solicitar_json.assert_not_called()
        assert resultado == ExperienciaAdaptada(
            cargo="Dev", empresa="TechCorp", periodo="2022 - Atual", conquistas=()
        )

    def test_contexto_ausente_vira_texto_vazio_e_os_textos_sao_aparados(self):
        resultado = _ajustar(_cliente({"conquistas": ["  Criei APIs.  "]}))

        assert resultado.conquistas == ("Criei APIs.",)
        assert resultado.contexto == ""

    @pytest.mark.parametrize(
        "resposta",
        [
            {},
            {"conquistas": []},
            {"conquistas": "Criei APIs."},
            {"conquistas": ["Criei APIs.", "  "]},
            {"conquistas": [1]},
            {"conquistas": ["Criei APIs."], "contexto": 5},
        ],
    )
    def test_resposta_fora_do_formato_gera_erro(self, resposta):
        with pytest.raises(ValueError, match="conquistas"):
            _ajustar(_cliente(resposta))


class TestAjustadorExperienciaOpenAIClientRefinar:
    def test_devolve_conquistas_e_contexto_novos_preservando_a_identificacao(self):
        resultado = _refinar(_cliente(RESPOSTA))

        assert resultado == ExperienciaAdaptada(
            cargo="Dev",
            empresa="TechCorp",
            periodo="2022 - Atual",
            conquistas=("Desenvolvi APIs em Java.", "Reduzi o tempo de resposta em 40%."),
            contexto="Na TechCorp, atuei na plataforma de pagamentos.",
        )

    def test_prompt_do_usuario_traz_as_conquistas_e_o_contexto_atuais(self):
        cliente = _cliente(RESPOSTA)

        _refinar(cliente, idioma="en")

        usuario = cliente.solicitar_json.call_args.kwargs["prompt_usuario"]
        assert "- Criei APIs." in usuario
        assert "- Reduzi custos." in usuario
        assert "Empresa de pagamentos." in usuario
        assert "Vaga Java sênior" in usuario
        assert "inglês" in usuario

    def test_resposta_fora_do_formato_gera_erro(self):
        with pytest.raises(ValueError, match="conquistas"):
            _refinar(_cliente({"conquistas": []}))


class TestAjustadorExperienciaOpenAIClientCargoAlvo:
    def test_ajustar_envia_o_cargo_alvo_no_prompt_do_usuario(self):
        cliente = _cliente(RESPOSTA)

        _ajustar(cliente, cargo_alvo="Code Reviewer")

        usuario = cliente.solicitar_json.call_args.kwargs["prompt_usuario"]
        assert "Cargo-alvo (título da vaga): Code Reviewer" in usuario

    def test_refinar_envia_o_cargo_alvo_no_prompt_do_usuario(self):
        cliente = _cliente(RESPOSTA)

        _refinar(cliente, cargo_alvo="Code Reviewer")

        usuario = cliente.solicitar_json.call_args.kwargs["prompt_usuario"]
        assert "Cargo-alvo (título da vaga): Code Reviewer" in usuario

    def test_sem_cargo_alvo_o_prompt_nao_cita_o_cargo_alvo(self):
        cliente = _cliente(RESPOSTA)

        _ajustar(cliente)

        usuario = cliente.solicitar_json.call_args.kwargs["prompt_usuario"]
        assert "Cargo-alvo" not in usuario
