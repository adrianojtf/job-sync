"""Modelo de domínio para vagas: análise de descrição de vaga e vaga capturada."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Optional, Tuple


class CategoriaRequisitoTecnico(Enum):
    """Categorias gerais de requisitos técnicos extraídos de uma vaga."""

    TECNOLOGIA = auto()
    FERRAMENTA = auto()
    HABILIDADE = auto()
    METODOLOGIA = auto()
    OUTRA = auto()


class TipoRequisitoTecnico(Enum):
    """Classificação do requisito técnico quanto à sua natureza."""

    EXPLICITO = auto()
    IMPLICITO = auto()
    AMBIGUO = auto()


class OrigemRequisitoTecnico(Enum):
    """Origem do requisito técnico para auditoria e rastreabilidade."""

    DESCRICAO_VAGA = auto()
    INTERPRETACAO = auto()
    DESCONHECIDA = auto()


@dataclass(frozen=True)
class RequisitoTecnico:
    nome: str
    categoria: CategoriaRequisitoTecnico
    tipo: TipoRequisitoTecnico
    origem: OrigemRequisitoTecnico

    def __post_init__(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("O nome do requisito técnico não pode ser vazio.")


@dataclass(frozen=True)
class AnaliseVaga:
    requisitos: Tuple[RequisitoTecnico, ...]
    ambiguidade: Tuple[str, ...]
    texto_original: str

    def __post_init__(self) -> None:
        if not self.texto_original or not self.texto_original.strip():
            raise ValueError("O texto original da descrição de vaga não pode ser vazio.")
        if self.requisitos is None:
            raise ValueError("Os requisitos técnicos devem ser fornecidos como uma sequência.")
        if self.ambiguidade is None:
            raise ValueError("A ambiguidade deve ser fornecida como uma sequência.")


@dataclass(frozen=True)
class Vaga:
    """Vaga capturada (via extensão de navegador ou colada manualmente) e associada a um perfil."""

    id: str
    perfil_identificador: str
    texto_descricao: str
    data_captura: datetime
    url_origem: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("O id da vaga não pode ser vazio.")
        if not self.perfil_identificador or not self.perfil_identificador.strip():
            raise ValueError("O identificador do perfil não pode ser vazio.")
        if not self.texto_descricao or not self.texto_descricao.strip():
            raise ValueError("O texto da descrição da vaga não pode ser vazio.")
