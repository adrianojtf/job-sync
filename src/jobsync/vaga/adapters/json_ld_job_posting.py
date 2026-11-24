"""Leitura de vagas publicadas com dados estruturados schema.org `JobPosting` (JSON-LD)."""
from __future__ import annotations

import html
import json
from typing import Any, Optional

from bs4 import BeautifulSoup

from jobsync.vaga.adapters.html_para_texto import converter_html_em_texto
from jobsync.vaga.domain.dados_vaga import DadosVaga

_TIPOS_DE_CONTRATACAO = {
    "FULL_TIME": "Tempo integral",
    "PART_TIME": "Meio período",
    "CONTRACTOR": "Contrato",
    "TEMPORARY": "Temporário",
    "INTERN": "Estágio",
    "VOLUNTEER": "Voluntário",
    "PER_DIEM": "Por diária",
    "OTHER": "Outro",
}


def extrair_dados_job_posting(pagina_html: str, url: Optional[str]) -> Optional[DadosVaga]:
    """Devolve os dados da vaga descrita em JSON-LD, ou `None` se a página não tiver um `JobPosting` utilizável."""
    sopa = BeautifulSoup(pagina_html, "html.parser")
    for script in sopa.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            conteudo = json.loads(script.string or script.get_text())
        except ValueError:
            continue
        posting = _achar_job_posting(conteudo)
        if posting is None:
            continue
        dados = _montar_dados(posting, url)
        if dados is not None:
            return dados
    return None


def _achar_job_posting(conteudo: Any) -> Optional[dict]:
    if isinstance(conteudo, list):
        for item in conteudo:
            encontrado = _achar_job_posting(item)
            if encontrado is not None:
                return encontrado
        return None
    if not isinstance(conteudo, dict):
        return None
    if _e_job_posting(conteudo.get("@type")):
        return conteudo
    return _achar_job_posting(conteudo.get("@graph"))


def _e_job_posting(tipo: Any) -> bool:
    if isinstance(tipo, list):
        return "JobPosting" in tipo
    return tipo == "JobPosting"


def _montar_dados(posting: dict, url: Optional[str]) -> Optional[DadosVaga]:
    descricao = _descricao(posting.get("description"))
    if not descricao:
        return None
    try:
        return DadosVaga(
            descricao=descricao,
            cargo=_texto(posting.get("title")),
            empresa=_empresa(posting.get("hiringOrganization")),
            local=_local(posting),
            url=url,
            tipo_contratacao=_tipo_de_contratacao(posting.get("employmentType")),
            setor=_texto(posting.get("industry")),
        )
    except ValueError:
        return None


def _texto(valor: Any) -> Optional[str]:
    return valor if isinstance(valor, str) and valor.strip() else None


def _descricao(bruta: Any) -> str:
    if not isinstance(bruta, str):
        return ""
    if "<" not in bruta and "&lt;" in bruta:
        bruta = html.unescape(bruta)
    return converter_html_em_texto(bruta)


def _empresa(organizacao: Any) -> Optional[str]:
    if isinstance(organizacao, dict):
        return _texto(organizacao.get("name"))
    return _texto(organizacao)


def _local(posting: dict) -> Optional[str]:
    locais = posting.get("jobLocation")
    if isinstance(locais, dict):
        locais = [locais]
    descricoes = [d for d in (_descrever_local(item) for item in locais or []) if d]
    if descricoes:
        return "; ".join(descricoes)
    if posting.get("jobLocationType") == "TELECOMMUTE":
        return "Remoto"
    return None


def _descrever_local(local: Any) -> Optional[str]:
    if not isinstance(local, dict):
        return None
    endereco = local.get("address")
    if isinstance(endereco, str):
        return _texto(endereco)
    if not isinstance(endereco, dict):
        return None
    pais = endereco.get("addressCountry")
    if isinstance(pais, dict):
        pais = pais.get("name")
    partes = [endereco.get("addressLocality"), endereco.get("addressRegion"), pais]
    return ", ".join(parte for parte in partes if isinstance(parte, str) and parte.strip()) or None


def _tipo_de_contratacao(valor: Any) -> Optional[str]:
    tipos = valor if isinstance(valor, list) else [valor]
    nomes = [_TIPOS_DE_CONTRATACAO.get(tipo, tipo) for tipo in tipos if isinstance(tipo, str) and tipo.strip()]
    return ", ".join(nomes) or None
