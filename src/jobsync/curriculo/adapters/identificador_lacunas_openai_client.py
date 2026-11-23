"""Adapter OpenAI que aponta os temas da vaga sem sustentação no histórico do candidato."""
from __future__ import annotations

from jobsync.curriculo.adapters.prompt_contexto_vaga import linha_cargo_alvo
from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.contexto_vaga import ContextoVaga
from jobsync.curriculo.domain.identificador_lacunas_port import IdentificadorLacunasPort
from jobsync.curriculo.domain.lacuna_da_vaga import LIMITE_DE_LACUNAS, HistoricoDoCandidato, LacunaDaVaga
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI

_ERRO_FORMATO = "O modelo devolveu as lacunas fora do formato esperado."

_PROMPT_SISTEMA = f"""\
Você ajuda um candidato a adaptar o currículo a uma vaga. Compare a vaga com o histórico do candidato
e aponte os temas centrais da vaga e do cargo-alvo (práticas, tipo de atuação, contexto do cargo,
tecnologias pedidas) que o histórico NÃO sustenta. Para cada tema, escreva uma pergunta ao candidato.
Responda somente em JSON no formato:
{{"lacunas": [{{"tema": "tema curto", "pergunta": "Você já ...?"}}]}}

Regras:
- No máximo {LIMITE_DE_LACUNAS} lacunas; ordene do tema mais central para o menos central.
- Não pergunte o que o histórico já sustenta: considere o resumo, as experiências, as conquistas
  cadastradas e as tecnologias do perfil.
- Cada pergunta é uma pergunta fechada (sim ou não), direta, começando com "Você já", sobre uma
  única atuação ou prática. Não afirme nada sobre o candidato dentro da pergunta.
- Escreva os temas e as perguntas em português do Brasil, qualquer que seja o idioma da vaga.
- Sem lacunas, devolva {{"lacunas": []}}.
"""


class IdentificadorLacunasOpenAIClient(IdentificadorLacunasPort):
    """Pede ao modelo as lacunas da vaga e valida o formato da resposta."""

    def __init__(self, cliente_openai: ClienteOpenAI | None = None) -> None:
        self._cliente_openai = cliente_openai or ClienteOpenAI()

    def identificar(
        self, historico: HistoricoDoCandidato, contexto: ContextoVaga
    ) -> tuple[LacunaDaVaga, ...]:
        resposta = self._cliente_openai.solicitar_json(
            prompt_sistema=_PROMPT_SISTEMA,
            prompt_usuario=(
                f"{linha_cargo_alvo(contexto)}"
                f"Descrição da vaga-alvo:\n{contexto.descricao_vaga}\n\n"
                f"{self._requisitos(contexto)}"
                f"{self._historico(historico)}"
            ),
        )
        return self._lacunas(resposta)

    @staticmethod
    def _requisitos(contexto: ContextoVaga) -> str:
        nomes = ", ".join(requisito.nome for requisito in contexto.analise_vaga.requisitos)
        return f"Requisitos técnicos da vaga: {nomes}\n\n" if nomes else ""

    @staticmethod
    def _historico(historico: HistoricoDoCandidato) -> str:
        experiencias = "\n\n".join(_experiencia(experiencia) for experiencia in historico.experiencias)
        return (
            "Histórico do candidato:\n"
            f"Resumo: {historico.resumo.strip() or '(sem resumo)'}\n"
            f"Tecnologias do perfil: {', '.join(historico.tecnologias) or 'nenhuma'}\n\n"
            f"Experiências:\n{experiencias}"
        )

    @staticmethod
    def _lacunas(resposta: dict) -> tuple[LacunaDaVaga, ...]:
        itens = resposta.get("lacunas")
        if not isinstance(itens, list):
            raise ValueError(_ERRO_FORMATO)
        lacunas = []
        for item in itens:
            if not isinstance(item, dict) or not all(isinstance(item.get(c), str) for c in ("tema", "pergunta")):
                raise ValueError(_ERRO_FORMATO)
            try:
                lacunas.append(LacunaDaVaga(tema=item["tema"], pergunta=item["pergunta"]))
            except ValueError as erro:
                raise ValueError(_ERRO_FORMATO) from erro
        return tuple(lacunas)


def _experiencia(experiencia: ExperienciaParaAvaliacao) -> str:
    cabecalho = f"{experiencia.cargo or 'Cargo não informado'} - {experiencia.empresa or 'empresa não informada'}"
    if experiencia.periodo:
        cabecalho += f" ({experiencia.periodo})"
    linhas = [cabecalho, experiencia.descricao.strip() or "(sem descrição)"]
    linhas.extend(f"- {conquista}" for conquista in experiencia.conquistas)
    return "\n".join(linhas)
