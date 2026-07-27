"""Value Object responsável por gerar o nome padronizado do arquivo de currículo.

Padrão: nomeCompleto-data-cargoDoCandidato-empresa.pdf
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date


def _remover_acentos(texto: str) -> str:
    forma_normalizada = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in forma_normalizada if not unicodedata.combining(c))


def _para_segmento_camel_case(texto: str) -> str:
    """Converte um texto livre em um segmento único, sem espaços ou pontuação.

    Cada palavra é capitalizada e concatenada (PascalCase), preservando
    siglas já em maiúsculas quando fizer sentido para o cargo/empresa.
    """
    texto_sem_acento = _remover_acentos(texto)
    texto_com_separadores = re.sub(r"[^a-zA-Z0-9]+", " ", texto_sem_acento)
    palavras = texto_com_separadores.split()
    return "".join(palavra.capitalize() for palavra in palavras)


def _validar_obrigatorio(valor: str, nome_campo: str) -> None:
    if not valor or not valor.strip():
        raise ValueError(f"O campo '{nome_campo}' é obrigatório e não pode ser vazio.")


@dataclass(frozen=True)
class NomeArquivo:
    """Value Object imutável representando o nome do arquivo PDF do currículo."""

    valor: str

    @staticmethod
    def criar(
        nome_completo: str,
        cargo: str,
        empresa: str,
        data: date | None = None,
    ) -> "NomeArquivo":
        _validar_obrigatorio(nome_completo, "nome completo")
        _validar_obrigatorio(cargo, "cargo")
        _validar_obrigatorio(empresa, "empresa")

        data_referencia = data or date.today()

        segmento_nome = _para_segmento_camel_case(nome_completo)
        segmento_cargo = _para_segmento_camel_case(cargo)
        segmento_empresa = _para_segmento_camel_case(empresa)
        segmento_data = data_referencia.isoformat()

        valor = f"{segmento_nome}-{segmento_data}-{segmento_cargo}-{segmento_empresa}.pdf"
        return NomeArquivo(valor)

    def __str__(self) -> str:
        return self.valor
