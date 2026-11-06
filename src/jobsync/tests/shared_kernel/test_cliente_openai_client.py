import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from jobsync.shared_kernel.adapters.cliente_openai_client import (
    MODELO_PADRAO,
    ClienteOpenAI,
)


class ResponsesFake:
    def __init__(self, output_text: str | None = None, erro: Exception | None = None):
        self.output_text = output_text
        self.erro = erro
        self.argumentos: dict | None = None

    def create(self, **argumentos):
        self.argumentos = argumentos
        if self.erro is not None:
            raise self.erro
        return SimpleNamespace(output_text=self.output_text)


class OpenAIFake:
    def __init__(self, responses: ResponsesFake):
        self.responses = responses


class TestClienteOpenAI:
    def test_solicitar_json_usa_modelo_e_modo_json(self):
        responses = ResponsesFake('{"resultado": "ok"}')
        cliente = ClienteOpenAI(modelo="gpt-test", cliente=OpenAIFake(responses))

        resposta = cliente.solicitar_json("sistema", "usuario")

        assert resposta == {"resultado": "ok"}
        assert responses.argumentos is not None
        assert responses.argumentos["model"] == "gpt-test"
        assert responses.argumentos["text"] == {"format": {"type": "json_object"}}
        assert responses.argumentos["input"][0]["role"] == "system"
        assert responses.argumentos["input"][1]["role"] == "user"

    def test_usa_modelo_configurado_no_ambiente(self):
        responses = ResponsesFake('{"resultado": "ok"}')
        with patch.dict(os.environ, {"OPENAI_MODEL": "gpt-configurado"}):
            cliente = ClienteOpenAI(cliente=OpenAIFake(responses))

            cliente.solicitar_json("sistema", "usuario")

        assert responses.argumentos["model"] == "gpt-configurado"

    def test_usa_modelo_padrao_quando_nao_configurado(self):
        responses = ResponsesFake('{"resultado": "ok"}')
        with patch.dict(os.environ):
            os.environ.pop("OPENAI_MODEL", None)
            cliente = ClienteOpenAI(cliente=OpenAIFake(responses))

            cliente.solicitar_json("sistema", "usuario")

        assert responses.argumentos["model"] == MODELO_PADRAO

    def test_resposta_json_invalida_gera_value_error(self):
        cliente = ClienteOpenAI(cliente=OpenAIFake(ResponsesFake("não é JSON")))

        with pytest.raises(ValueError, match="Resposta do modelo não é um JSON válido"):
            cliente.solicitar_json("sistema", "usuario")

    def test_falha_da_api_e_traduzida_sem_expor_detalhes(self):
        cliente = ClienteOpenAI(
            cliente=OpenAIFake(ResponsesFake(erro=RuntimeError("segredo interno")))
        )

        with pytest.raises(RuntimeError, match="Falha ao solicitar resposta à API OpenAI") as erro:
            cliente.solicitar_json("sistema", "usuario")

        assert "segredo interno" not in str(erro.value)

    def test_chave_api_e_obrigatoria_sem_cliente_injetado(self):
        with patch.dict(os.environ):
            os.environ.pop("OPENAI_API_KEY", None)

            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                ClienteOpenAI()

    def test_cria_cliente_sdk_com_chave_do_ambiente(self):
        chaves_recebidas = []

        class OpenAISDKFake:
            def __init__(self, api_key: str):
                chaves_recebidas.append(api_key)

        sdk = SimpleNamespace(OpenAI=OpenAISDKFake)
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch.dict(sys.modules, {"openai": sdk}):
                ClienteOpenAI()

        assert chaves_recebidas == ["test-key"]
