"""Value Object que representa o link de uma vaga, já validado e normalizado."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from jobsync.vaga.domain.exceptions import LinkVagaInvalido

_LIMITE_TAMANHO_LINK = 2048
_ESQUEMAS_ACEITOS = ("http", "https")
_PARAMETROS_DE_RASTREAMENTO = frozenset(
    {
        "trk",
        "trkemail",
        "trackingid",
        "refid",
        "midtoken",
        "midsig",
        "otptoken",
        "eid",
        "ebp",
        "lipi",
        "licu",
        "originalsubdomain",
        "fbclid",
        "gclid",
        "mc_cid",
        "mc_eid",
    }
)
_PREFIXO_UTM = "utm_"
_PADRAO_ESQUEMA = re.compile(r"^[a-z][a-z0-9+.\-]*:", re.IGNORECASE)
_PADRAO_ID_NO_CAMINHO_LINKEDIN = re.compile(r"^/jobs/view/(?:[^/?#]*-)?(\d{6,})/?$")
_PADRAO_ID_NUMERICO = re.compile(r"^\d{6,}$")
_URL_CANONICA_LINKEDIN = "https://www.linkedin.com/jobs/view/{id_vaga}/"


class FonteVaga(Enum):
    """Origem do link da vaga, que define como a leitura é feita."""

    LINKEDIN = "linkedin"
    OUTRA = "outra"


@dataclass(frozen=True)
class LinkVaga:
    """Link de vaga validado: apenas http/https, sem rastreamento e com a fonte identificada."""

    url: str
    fonte: FonteVaga
    id_vaga: Optional[str] = None

    @classmethod
    def criar(cls, entrada: str) -> LinkVaga:
        texto = (entrada or "").strip()
        if not texto:
            raise LinkVagaInvalido("Informe o link da vaga.")
        if len(texto) > _LIMITE_TAMANHO_LINK:
            raise LinkVagaInvalido("O link da vaga é longo demais.")

        partes = urlsplit(cls._com_esquema(texto))
        cls._validar_partes(partes)

        host = (partes.hostname or "").lower()
        if cls._e_linkedin(host):
            return cls._criar_do_linkedin(partes)
        return cls._criar_de_outra_fonte(partes, host)

    @staticmethod
    def _com_esquema(texto: str) -> str:
        if "://" in texto:
            return texto
        if _PADRAO_ESQUEMA.match(texto):
            return texto
        if " " in texto or "." not in texto.split("/")[0]:
            raise LinkVagaInvalido("O texto informado não parece um link de vaga.")
        return f"https://{texto}"

    @staticmethod
    def _validar_partes(partes) -> None:
        if partes.scheme.lower() not in _ESQUEMAS_ACEITOS:
            raise LinkVagaInvalido("O link da vaga deve começar com http ou https.")
        if not partes.hostname:
            raise LinkVagaInvalido("O link da vaga não tem um endereço válido.")
        if partes.username is not None or partes.password is not None:
            raise LinkVagaInvalido("O link da vaga não pode conter usuário e senha.")

    @staticmethod
    def _e_linkedin(host: str) -> bool:
        return host == "linkedin.com" or host.endswith(".linkedin.com")

    @classmethod
    def _criar_do_linkedin(cls, partes) -> LinkVaga:
        id_vaga = cls._extrair_id_linkedin(partes)
        if id_vaga is None:
            raise LinkVagaInvalido(
                "O link do LinkedIn não identifica uma vaga específica. Abra a vaga e copie o link dela."
            )
        return cls(
            url=_URL_CANONICA_LINKEDIN.format(id_vaga=id_vaga),
            fonte=FonteVaga.LINKEDIN,
            id_vaga=id_vaga,
        )

    @staticmethod
    def _extrair_id_linkedin(partes) -> Optional[str]:
        correspondencia = _PADRAO_ID_NO_CAMINHO_LINKEDIN.match(partes.path)
        if correspondencia:
            return correspondencia.group(1)
        for nome, valor in parse_qsl(partes.query):
            if nome == "currentJobId" and _PADRAO_ID_NUMERICO.match(valor):
                return valor
        return None

    @classmethod
    def _criar_de_outra_fonte(cls, partes, host: str) -> LinkVaga:
        consulta = urlencode(
            [
                (nome, valor)
                for nome, valor in parse_qsl(partes.query, keep_blank_values=True)
                if not cls._e_rastreamento(nome)
            ]
        )
        porta = f":{partes.port}" if partes.port else ""
        url = urlunsplit((partes.scheme.lower(), f"{host}{porta}", partes.path, consulta, ""))
        return cls(url=url, fonte=FonteVaga.OUTRA)

    @staticmethod
    def _e_rastreamento(nome: str) -> bool:
        minusculo = nome.lower()
        return minusculo in _PARAMETROS_DE_RASTREAMENTO or minusculo.startswith(_PREFIXO_UTM)
