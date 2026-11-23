"""Testes do adapter RedatorConquistaOpenAIClient."""
from unittest.mock import Mock

import pytest

from jobsync.curriculo.adapters.redator_conquista_openai_client import RedatorConquistaOpenAIClient
from jobsync.curriculo.domain.lacuna_da_vaga import LacunaDaVaga
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI

LACUNA = LacunaDaVaga("Atuação junto ao cliente", "Você já atuou junto ao cliente na entrega de uma solução?")
CASO = "Fiquei no cliente por 2 meses e entreguei a integração de faturamento."


def _cliente(resposta: dict) -> Mock:
    cliente = Mock(spec=ClienteOpenAI)
    cliente.solicitar_json.return_value = resposta
    return cliente


def _redigir(cliente: Mock, caso: str = CASO, cargo: str = "Engenheiro de Software", idioma: str = "pt") -> str:
    return RedatorConquistaOpenAIClient(cliente).redigir(LACUNA, caso, cargo, idioma)


class TestRedatorConquistaOpenAIClient:
    def test_devolve_o_texto_da_conquista_aparado(self):
        resultado = _redigir(_cliente({"conquista": "  Atuei junto ao cliente na integração de faturamento.  "}))

        assert resultado == "Atuei junto ao cliente na integração de faturamento."

    def test_prompt_do_usuario_traz_o_tema_a_pergunta_o_caso_o_cargo_e_o_idioma(self):
        cliente = _cliente({"conquista": "Atuei."})

        _redigir(cliente, idioma="en")

        usuario = cliente.solicitar_json.call_args.kwargs["prompt_usuario"]
        assert "Tema: Atuação junto ao cliente" in usuario
        assert "Pergunta: Você já atuou junto ao cliente na entrega de uma solução?" in usuario
        assert f"Caso descrito pelo candidato: {CASO}" in usuario
        assert "Cargo na experiência: Engenheiro de Software" in usuario
        assert "inglês" in usuario

    def test_prompt_de_sistema_proibe_acrescentar_fato_numero_ou_tecnologia(self):
        cliente = _cliente({"conquista": "Atuei."})

        _redigir(cliente)

        sistema = cliente.solicitar_json.call_args.kwargs["prompt_sistema"].lower()
        assert "use somente o que o candidato informou" in sistema
        assert "não acrescente fato, número, resultado, tecnologia ou prática" in sistema
        assert "verbo de ação" in sistema
        assert "não mencione a vaga" in sistema
        assert '"conquista"' in sistema

    @pytest.mark.parametrize("resposta", [{}, {"conquista": ""}, {"conquista": "   "}, {"conquista": 3}, {"conquista": ["a"]}])
    def test_resposta_fora_do_formato_gera_erro(self, resposta):
        with pytest.raises(ValueError):
            _redigir(_cliente(resposta))
