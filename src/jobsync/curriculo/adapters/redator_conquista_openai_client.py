"""Adapter OpenAI que redige uma conquista a partir do caso descrito pelo candidato."""
from __future__ import annotations

from jobsync.curriculo.domain.lacuna_da_vaga import LacunaDaVaga
from jobsync.curriculo.domain.redator_conquista_port import RedatorConquistaPort
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI

_NOME_IDIOMA = {
    "pt": "português do Brasil",
    "en": "inglês (formato americano de currículo)",
}

_ERRO_FORMATO = "O modelo devolveu a conquista fora do formato esperado."

_PROMPT_SISTEMA = """\
Você escreve uma conquista de currículo a partir do caso que o candidato descreveu em resposta a uma
pergunta. Responda somente em JSON no formato: {"conquista": "texto da conquista"}

Regras:
- Use somente o que o candidato informou no caso.
- Não acrescente fato, número, resultado, tecnologia ou prática que ele não citou.
- Uma frase curta (no máximo duas), começando com verbo de ação no passado.
- Cite o resultado só quando o candidato o informou.
- Não mencione a vaga, a pergunta nem o tema; escreva a conquista como parte do histórico dele.
"""


class RedatorConquistaOpenAIClient(RedatorConquistaPort):
    """Pede ao modelo a redação da conquista e valida o formato da resposta."""

    def __init__(self, cliente_openai: ClienteOpenAI | None = None) -> None:
        self._cliente_openai = cliente_openai or ClienteOpenAI()

    def redigir(self, lacuna: LacunaDaVaga, caso: str, cargo: str, idioma_alvo: str) -> str:
        resposta = self._cliente_openai.solicitar_json(
            prompt_sistema=_PROMPT_SISTEMA,
            prompt_usuario=(
                f"Tema: {lacuna.tema}\n"
                f"Pergunta: {lacuna.pergunta}\n"
                f"Caso descrito pelo candidato: {caso}\n"
                f"Cargo na experiência: {cargo or 'não informado'}\n\n"
                f"Idioma de saída obrigatório: {_NOME_IDIOMA.get(idioma_alvo, idioma_alvo)}"
            ),
        )
        conquista = resposta.get("conquista")
        if not isinstance(conquista, str) or not conquista.strip():
            raise ValueError(_ERRO_FORMATO)
        return conquista.strip()
