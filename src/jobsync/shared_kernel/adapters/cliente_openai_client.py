"""Cliente compartilhado para chamadas JSON à API OpenAI."""
from __future__ import annotations

import json
import os
from typing import Any

MODELO_PADRAO = "gpt-6-luna"


class ClienteOpenAI:
    """Encapsula chamadas à Responses API e parsing de respostas JSON."""

    def __init__(
        self,
        chave_api: str | None = None,
        modelo: str | None = None,
        cliente: Any | None = None,
    ) -> None:
        self._modelo = modelo or os.getenv("OPENAI_MODEL") or MODELO_PADRAO
        if cliente is not None:
            self._cliente = cliente
            return

        chave = chave_api or os.getenv("OPENAI_API_KEY")
        if not chave:
            raise ValueError(
                "OPENAI_API_KEY não configurada. Defina a variável de ambiente "
                "ou configure um cliente OpenAI."
            )

        try:
            from openai import OpenAI
        except ImportError as erro:
            raise RuntimeError("O SDK openai não está instalado.") from erro

        self._cliente = OpenAI(api_key=chave)

    def solicitar_json(self, prompt_sistema: str, prompt_usuario: str) -> dict:
        """Envia prompts e retorna a resposta JSON parseada."""
        try:
            resposta = self._cliente.responses.create(
                model=self._modelo,
                input=[
                    {
                        "role": "system",
                        "content": [{"type": "input_text", "text": prompt_sistema}],
                    },
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt_usuario}],
                    },
                ],
                text={"format": {"type": "json_object"}},
            )
        except Exception as erro:
            raise RuntimeError("Falha ao solicitar resposta à API OpenAI.") from erro

        try:
            return json.loads(resposta.output_text)
        except (json.JSONDecodeError, TypeError) as erro:
            raise ValueError(f"Resposta do modelo não é um JSON válido: {erro}") from erro
