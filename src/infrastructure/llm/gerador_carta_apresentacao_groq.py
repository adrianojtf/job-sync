"""Adapter (implementa GerarCartaApresentacaoPort) que gera a carta de apresentação via IA.

Reaproveita o mesmo padrão de prompt estruturado já usado em AjustadorTextoGroq:
inclui a análise de vaga (requisitos explícitos/implícitos) e o currículo,
sem jamais inventar fatos que não constem no currículo original.
"""
from __future__ import annotations

from domain.curriculo import Curriculo
from domain.curriculo.gerar_carta_apresentacao_port import GerarCartaApresentacaoPort
from domain.vaga import AnaliseVaga, TipoRequisitoTecnico
from infrastructure.llm.cliente_groq import ClienteGroq

_NOME_IDIOMA = {"pt": "português do Brasil", "en": "inglês (formato americano)"}

_PROMPT_SISTEMA = """\
Você é um especialista em redação de cartas de apresentação (cover letters) que \
ajuda candidatos a se candidatarem a vagas específicas, SEM jamais inventar \
experiência, tecnologia ou resultado que não exista no currículo original.

Responda ESTRITAMENTE em JSON no formato:
{"carta": "texto completo da carta de apresentação"}
"""


class GeradorCartaApresentacaoGroq(GerarCartaApresentacaoPort):
    """Gera o texto da carta de apresentação usando o modelo Groq."""

    def __init__(self, cliente_groq: ClienteGroq | None = None) -> None:
        self._cliente_groq = cliente_groq or ClienteGroq()

    def gerar(self, curriculo: Curriculo, analise_vaga: AnaliseVaga, idioma_alvo: str) -> str:
        nome_idioma = _NOME_IDIOMA.get(idioma_alvo, idioma_alvo)

        requisitos_explicitos = [
            requisito.nome
            for requisito in analise_vaga.requisitos
            if requisito.tipo == TipoRequisitoTecnico.EXPLICITO
        ]
        requisitos_implicitos = [
            requisito.nome
            for requisito in analise_vaga.requisitos
            if requisito.tipo == TipoRequisitoTecnico.IMPLICITO
        ]

        conteudo_curriculo = "\n\n".join(
            f"{secao.titulo}:\n{secao.conteudo}" for secao in curriculo.secoes
        )

        prompt_usuario = (
            f"Nome do candidato: {curriculo.nome_completo}\n\n"
            f"Currículo:\n{conteudo_curriculo}\n\n"
            f"Descrição da vaga-alvo:\n{analise_vaga.texto_original}\n\n"
            f"Análise de vaga estruturada:\n"
            f"- Requisitos explícitos: {', '.join(requisitos_explicitos) or 'nenhum'}\n"
            f"- Requisitos implícitos: {', '.join(requisitos_implicitos) or 'nenhum'}\n\n"
            f"Idioma de saída obrigatório: {nome_idioma}\n\n"
            "Escreva uma carta de apresentação concisa (saudação, motivação para a vaga, "
            "principais qualificações alinhadas ao currículo, encerramento). "
            "Use apenas fatos presentes no currículo acima — não invente experiências, "
            "tecnologias ou resultados que não estejam listados."
        )

        resposta = self._cliente_groq.solicitar_json(
            prompt_sistema=_PROMPT_SISTEMA,
            prompt_usuario=prompt_usuario,
        )
        carta_bruta = resposta.get("carta")
        # O modelo às vezes devolve um objeto/lista estruturado em vez de texto puro,
        # apesar da instrução no prompt — normaliza pra string em vez de quebrar.
        carta = str(carta_bruta).strip() if carta_bruta else ""
        if not carta:
            raise ValueError("O modelo não retornou o texto da carta de apresentação.")

        return carta
