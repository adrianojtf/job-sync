"""Cliente de baixo nível para a API Groq (modelo LLM gratuito).

Centraliza a configuração da chamada (modelo, chave de API, tratamento de
erro) para ser reutilizado pelos adapters de segmentação e de ajuste de texto,
evitar duplicação (DRY).
"""
from __future__ import annotations

import json
import os

from groq import Groq

MODELO_PADRAO = "llama-3.3-70b-versatile"


class ClienteGroq:
    """Encapsula a comunicação com a API Groq, incluindo parsing de JSON."""

    def __init__(self, chave_api: str | None = None, modelo: str = MODELO_PADRAO) -> None:
        chave = chave_api or os.getenv("GROQ_API_KEY")
        if not chave:
            raise ValueError(
                "GROQ_API_KEY não configurada. Defina a variável de ambiente "
                "ou crie um arquivo .env com GROQ_API_KEY=sua_chave. "
                "Obtenha uma chave gratuita em https://console.groq.com/keys"
            )
        self._cliente = Groq(api_key=chave)
        self._modelo = modelo

    def solicitar_json(self, prompt_sistema: str, prompt_usuario: str) -> dict:
        """Envia o prompt ao modelo e retorna a resposta já parseada como dict.

        Levanta ValueError se a resposta não for um JSON válido, evitando que
        erros de parsing se propaguem como exceções genéricas para o caller.
        """
        resposta = self._cliente.chat.completions.create(
            model=self._modelo,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        conteudo = resposta.choices[0].message.content
        try:
            return json.loads(conteudo)
        except json.JSONDecodeError as erro:
            raise ValueError(f"Resposta do modelo não é um JSON válido: {erro}") from erro
