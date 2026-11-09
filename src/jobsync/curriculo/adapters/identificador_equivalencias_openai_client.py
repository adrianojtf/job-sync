"""Adapter OpenAI que aponta tecnologias do perfil equivalentes às pedidas pela vaga."""
from __future__ import annotations

from collections.abc import Sequence

from jobsync.curriculo.adapters.prompt_contexto_vaga import linha_cargo_alvo
from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.contexto_vaga import ContextoVaga
from jobsync.curriculo.domain.equivalencia_tecnologia import EquivalenciaTecnologia
from jobsync.curriculo.domain.identificador_equivalencias_port import IdentificadorEquivalenciasPort
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI
from jobsync.vaga.domain.analise_vaga import AnaliseVaga, TipoRequisitoTecnico

_ERRO_FORMATO = "O modelo devolveu as equivalências de tecnologia fora do formato esperado."

_PROMPT_SISTEMA = """\
Você compara as tecnologias das experiências de um candidato com as tecnologias pedidas por uma
vaga e aponta pares equivalentes. Responda somente em JSON no formato:
{"equivalencias": [{"original": "React", "alvo": "Angular"}]}

Regras:
- "original" é uma tecnologia que aparece nas experiências do candidato, escrita como no texto.
- "alvo" é uma tecnologia pedida pela vaga, escrita como na vaga, que não aparece nas experiências.
- Só aponte pares da mesma categoria e com o mesmo papel (ex.: framework de front-end por framework
  de front-end, banco relacional por banco relacional, mensageria por mensageria).
- Não aponte pares entre categorias diferentes nem entre linguagens de programação.
- Não trate idiomas (inglês, espanhol etc.), metodologias ou habilidades comportamentais como tecnologias.
- Sem pares equivalentes, responda {"equivalencias": []}.
"""


class IdentificadorEquivalenciasOpenAIClient(IdentificadorEquivalenciasPort):
    def __init__(self, cliente_openai: ClienteOpenAI | None = None) -> None:
        self._cliente_openai = cliente_openai or ClienteOpenAI()

    def identificar(
        self,
        experiencias: Sequence[ExperienciaParaAvaliacao],
        contexto: ContextoVaga,
    ) -> tuple[EquivalenciaTecnologia, ...]:
        com_descricao = [experiencia for experiencia in experiencias if experiencia.descricao.strip()]
        if not com_descricao or not contexto.analise_vaga.requisitos:
            return ()

        resposta = self._cliente_openai.solicitar_json(
            prompt_sistema=_PROMPT_SISTEMA,
            prompt_usuario=(
                "Experiências do candidato:\n"
                + "\n".join(
                    f"- {experiencia.cargo or 'Cargo não informado'}: {experiencia.descricao.strip()}"
                    for experiencia in com_descricao
                )
                + "\n\n"
                f"{linha_cargo_alvo(contexto)}"
                f"{self._requisitos(contexto.analise_vaga)}"
            ),
        )
        return self._equivalencias(resposta)

    @staticmethod
    def _requisitos(analise_vaga: AnaliseVaga) -> str:
        def nomes(tipo: TipoRequisitoTecnico) -> str:
            return ", ".join(r.nome for r in analise_vaga.requisitos if r.tipo == tipo) or "nenhum"

        return (
            f"Requisitos explícitos da vaga: {nomes(TipoRequisitoTecnico.EXPLICITO)}\n"
            f"Requisitos implícitos da vaga: {nomes(TipoRequisitoTecnico.IMPLICITO)}"
        )

    @staticmethod
    def _equivalencias(resposta: dict) -> tuple[EquivalenciaTecnologia, ...]:
        itens = resposta.get("equivalencias")
        if not isinstance(itens, list):
            raise ValueError(_ERRO_FORMATO)
        equivalencias = []
        for item in itens:
            if not isinstance(item, dict):
                raise ValueError(_ERRO_FORMATO)
            original, alvo = item.get("original"), item.get("alvo")
            if not isinstance(original, str) or not isinstance(alvo, str):
                raise ValueError(_ERRO_FORMATO)
            equivalencias.append(EquivalenciaTecnologia(original=original, alvo=alvo))
        return tuple(equivalencias)
