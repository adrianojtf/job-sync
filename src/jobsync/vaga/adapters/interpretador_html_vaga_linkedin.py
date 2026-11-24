"""Interpretação do HTML público de uma vaga do LinkedIn.

O LinkedIn não documenta esse HTML e pode alterá-lo sem aviso: todas as classes
usadas ficam concentradas neste módulo. Se o título ou a descrição não forem
encontrados, a interpretação falha de forma explícita (devolve `None`).
"""
from __future__ import annotations

from typing import Optional

from bs4 import BeautifulSoup, Tag

from jobsync.vaga.adapters.html_para_texto import converter_html_em_texto
from jobsync.vaga.domain.dados_vaga import DadosVaga

_SELETOR_TITULO = "h2.top-card-layout__title, h1.top-card-layout__title"
_SELETOR_EMPRESA = "a.topcard__org-name-link"
_SELETOR_LOCAL = "span.topcard__flavor--bullet:not(.topcard__flavor--metadata)"
_SELETOR_DESCRICAO = "div.show-more-less-html__markup"
_SELETOR_CRITERIO = "li.description__job-criteria-item"
_SELETOR_ROTULO_CRITERIO = ".description__job-criteria-subheader"
_SELETOR_VALOR_CRITERIO = ".description__job-criteria-text"

_ROTULOS_SENIORIDADE = frozenset({"seniority level", "nível de experiência", "nivel de experiencia", "nível hierárquico"})
_ROTULOS_TIPO_CONTRATACAO = frozenset({"employment type", "tipo de emprego", "tipo de contratação"})
_ROTULOS_SETOR = frozenset({"industries", "setores", "setor"})
_VALORES_NAO_APLICAVEIS = frozenset({"not applicable", "não aplicável", "nao aplicavel"})
_TIPOS_DE_CONTRATACAO = {
    "full-time": "Tempo integral",
    "part-time": "Meio período",
    "contract": "Contrato",
    "temporary": "Temporário",
    "internship": "Estágio",
    "volunteer": "Voluntário",
    "other": "Outro",
}


def interpretar_html_vaga_linkedin(pagina: str, url: str) -> Optional[DadosVaga]:
    """Devolve os dados da vaga ou `None` quando o HTML não tem título e descrição."""
    sopa = BeautifulSoup(pagina or "", "html.parser")
    titulo = _texto(sopa.select_one(_SELETOR_TITULO))
    marcacao = sopa.select_one(_SELETOR_DESCRICAO)
    if not titulo or marcacao is None:
        return None
    descricao = converter_html_em_texto(str(marcacao))
    if not descricao:
        return None

    criterios = _ler_criterios(sopa)
    try:
        return DadosVaga(
            descricao=descricao,
            cargo=titulo,
            empresa=_texto(sopa.select_one(_SELETOR_EMPRESA)),
            local=_texto(sopa.select_one(_SELETOR_LOCAL)),
            url=url,
            tipo_contratacao=_traduzir_tipo_de_contratacao(criterios.get("tipo_contratacao")),
            senioridade=criterios.get("senioridade"),
            setor=criterios.get("setor"),
        )
    except ValueError:
        return None


def _texto(tag: Optional[Tag]) -> Optional[str]:
    if tag is None:
        return None
    return " ".join(tag.get_text().split()) or None


def _ler_criterios(sopa: BeautifulSoup) -> dict[str, str]:
    criterios: dict[str, str] = {}
    for item in sopa.select(_SELETOR_CRITERIO):
        rotulo = (_texto(item.select_one(_SELETOR_ROTULO_CRITERIO)) or "").lower()
        valor = _texto(item.select_one(_SELETOR_VALOR_CRITERIO))
        if not valor or valor.lower() in _VALORES_NAO_APLICAVEIS:
            continue
        if rotulo in _ROTULOS_SENIORIDADE:
            criterios["senioridade"] = valor
        elif rotulo in _ROTULOS_TIPO_CONTRATACAO:
            criterios["tipo_contratacao"] = valor
        elif rotulo in _ROTULOS_SETOR:
            criterios["setor"] = valor
    return criterios


def _traduzir_tipo_de_contratacao(valor: Optional[str]) -> Optional[str]:
    if valor is None:
        return None
    return _TIPOS_DE_CONTRATACAO.get(valor.lower(), valor)
