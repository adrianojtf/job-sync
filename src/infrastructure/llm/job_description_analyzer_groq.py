"""Adapter para análise de descrição de vaga usando o modelo Groq.

O adapter consome ClienteGroq e retorna o modelo de domínio AnaliseVaga.
"""
from __future__ import annotations

import unicodedata
from typing import Any
from venv import logger

from domain.vaga.job_description_analyzer_port import JobDescriptionAnalyzerPort
from domain.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from infrastructure.llm.cliente_groq import ClienteGroq
import logging

logger = logging.getLogger(__name__)

_PROMPT_SISTEMA = """\
Você é um assistente especializado em extrair requisitos técnicos de descrições de vagas.
Sua tarefa é retornar SOMENTE as informações explicitamente mencionadas ou claramente
inferidas no texto, sem inventar tecnologias, frameworks ou habilidades que não
estejam presentes na descrição.

Responda ESTRITAMENTE em JSON com o formato:
{
  "requisitos": [
    {
      "nome": "string",
      "categoria": "tecnologia | ferramenta | habilidade | metodologia | outra",
      "tipo": "explicito | implicito | ambiguidade",
      "origem": "descricao_vaga | interpretacao | desconhecida"
    }
  ],
  "ambiguidade": ["string" /* textos que indicam inferência ou contexto incerto */]
}

Regras:
- Não promova automaticamente frameworks relacionados a uma linguagem sem que
  eles sejam mencionados de forma explícita.
- Não inclua listas vazias ou itens inventados.
- Se não houver itens claros, retorne um array vazio em "requisitos".
- Em "ambiguidade", liste trechos curtos do texto da vaga que precisam de revisão manual.
"""


class JobDescriptionAnalyzerGroq(JobDescriptionAnalyzerPort):
    """Implementação do adaptador de análise de vaga usando Groq."""

    def __init__(self, cliente_groq: ClienteGroq | None = None) -> None:
        self._cliente_groq = cliente_groq or ClienteGroq()

    def analisar(self, descricao_vaga: str) -> AnaliseVaga:
        if not descricao_vaga or not descricao_vaga.strip():
            raise ValueError("A descrição da vaga é obrigatória para análise de requisitos.")

        prompt_usuario = self._construir_prompt_usuario(descricao_vaga)
        try:
            resposta = self._cliente_groq.solicitar_json(
                prompt_sistema=_PROMPT_SISTEMA,
                prompt_usuario=prompt_usuario,
            )
        except ValueError as erro:
            raise ValueError(
                f"Falha ao parsear a resposta do Groq para análise de vaga: {erro}"
            ) from erro      

        return self._montar_analise(descricao_vaga, resposta)

    @staticmethod
    def _construir_prompt_usuario(descricao_vaga: str) -> str:
        return f"Descrição da vaga a ser analisada:\n\n{descricao_vaga}"

    def _montar_analise(self, descricao_vaga: str, dados: dict[str, Any]) -> AnaliseVaga:
        requisitos_brutos = dados.get("requisitos")
        if requisitos_brutos is None:
            raise ValueError("Resposta inválida do modelo: campo 'requisitos' não encontrado.")
        if not isinstance(requisitos_brutos, list):
            raise ValueError("Resposta inválida do modelo: 'requisitos' deve ser uma lista.")

        requisitos = tuple(self._parse_requisito(item) for item in requisitos_brutos)

        ambiguidade_bruta = dados.get("ambiguidade", [])
        if not isinstance(ambiguidade_bruta, list):
            raise ValueError("Resposta inválida do modelo: 'ambiguidade' deve ser uma lista.")

        ambiguidade = tuple(
            item.strip()
            for item in ambiguidade_bruta
            if isinstance(item, str) and item.strip()
        )

        return AnaliseVaga(
            requisitos=requisitos,
            ambiguidade=ambiguidade,
            texto_original=descricao_vaga,
        )

    def _parse_requisito(self, requisito: Any) -> RequisitoTecnico:
        if not isinstance(requisito, dict):
            raise ValueError("Resposta inválida do modelo: cada requisito deve ser um objeto JSON.")

        nome = self._normalizar_texto(requisito.get("nome") or "")
        if not nome:
            raise ValueError("Resposta inválida do modelo: cada requisito deve conter um nome não vazio.")

        categoria = self._mapear_categoria(requisito.get("categoria"))
        tipo = self._mapear_tipo(requisito.get("tipo"))
        origem = self._mapear_origem(requisito.get("origem"), tipo)

        return RequisitoTecnico(
            nome=nome,
            categoria=categoria,
            tipo=tipo,
            origem=origem,
        )

    def _mapear_categoria(self, categoria: Any) -> CategoriaRequisitoTecnico:
        texto = self._normalizar_texto(categoria or "")
        categorias: dict[str, CategoriaRequisitoTecnico] = {
            "tecnologia": CategoriaRequisitoTecnico.TECNOLOGIA,
            "technology": CategoriaRequisitoTecnico.TECNOLOGIA,
            "linguagem": CategoriaRequisitoTecnico.TECNOLOGIA,
            "linguagem de programacao": CategoriaRequisitoTecnico.TECNOLOGIA,
            "ferramenta": CategoriaRequisitoTecnico.FERRAMENTA,
            "framework": CategoriaRequisitoTecnico.FERRAMENTA,
            "habilidade": CategoriaRequisitoTecnico.HABILIDADE,
            "skill": CategoriaRequisitoTecnico.HABILIDADE,
            "metodologia": CategoriaRequisitoTecnico.METODOLOGIA,
            "metodo": CategoriaRequisitoTecnico.METODOLOGIA,
            "banco de dados": CategoriaRequisitoTecnico.OUTRA,
            "database": CategoriaRequisitoTecnico.OUTRA,
            "outra": CategoriaRequisitoTecnico.OUTRA,
        }
        return categorias.get(texto, CategoriaRequisitoTecnico.OUTRA)

    def _mapear_tipo(self, tipo: Any) -> TipoRequisitoTecnico:
        texto = self._normalizar_texto(tipo or "")
        tipos: dict[str, TipoRequisitoTecnico] = {
            "explicito": TipoRequisitoTecnico.EXPLICITO,
            "explícito": TipoRequisitoTecnico.EXPLICITO,
            "explicit": TipoRequisitoTecnico.EXPLICITO,
            "implicito": TipoRequisitoTecnico.IMPLICITO,
            "implícito": TipoRequisitoTecnico.IMPLICITO,
            "implicit": TipoRequisitoTecnico.IMPLICITO,
            "ambiguidade": TipoRequisitoTecnico.AMBIGUO,
            "ambigous": TipoRequisitoTecnico.AMBIGUO,
            "ambiguous": TipoRequisitoTecnico.AMBIGUO,
        }
        if not texto:
            return TipoRequisitoTecnico.EXPLICITO
        if texto not in tipos:
            raise ValueError(
                f"Resposta inválida do modelo: tipo de requisito desconhecido '{tipo}'."
            )
        return tipos[texto]

    def _mapear_origem(
        self, origem: Any, tipo: TipoRequisitoTecnico
    ) -> OrigemRequisitoTecnico:
        texto = self._normalizar_texto(origem or "")
        origens: dict[str, OrigemRequisitoTecnico] = {
            "descricao_vaga": OrigemRequisitoTecnico.DESCRICAO_VAGA,
            "origem_descricao_vaga": OrigemRequisitoTecnico.DESCRICAO_VAGA,
            "descricao": OrigemRequisitoTecnico.DESCRICAO_VAGA,
            "interpretacao": OrigemRequisitoTecnico.INTERPRETACAO,
            "interpretation": OrigemRequisitoTecnico.INTERPRETACAO,
            "desconhecida": OrigemRequisitoTecnico.DESCONHECIDA,
            "unknown": OrigemRequisitoTecnico.DESCONHECIDA,
        }
        if texto:
            return origens.get(texto, OrigemRequisitoTecnico.DESCONHECIDA)

        if tipo == TipoRequisitoTecnico.EXPLICITO:
            return OrigemRequisitoTecnico.DESCRICAO_VAGA
        return OrigemRequisitoTecnico.INTERPRETACAO

    @staticmethod
    def _normalizar_texto(valor: Any) -> str:
        if valor is None:
            return ""
        texto = str(valor).strip()
        texto = unicodedata.normalize("NFKD", texto)
        return "".join(ch for ch in texto if not unicodedata.combining(ch)).lower()
