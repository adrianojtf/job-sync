"""Schemas Pydantic para endpoints do domínio de vaga externa."""

from __future__ import annotations

import base64
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from jobsync.vaga_externa import VagaComScore


class DescobrirVagasRequest(BaseModel):
    """Payload para descobrir vagas externas com cálculo de match."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "termo": "python",
                "pdf_base64": "JVBERi0xLjQgdGVzdA==",
                "dias_maximo": 30,
            }
        }
    )

    termo: str = Field(description="Termo de busca para as fontes externas.")
    pdf_base64: str = Field(description="Conteúdo do PDF do currículo codificado em base64.")
    dias_maximo: int | None = Field(
        default=None,
        description="Limite de dias desde a publicação das vagas.",
    )

    def to_dto(self) -> dict[str, Any]:
        return {
            "termo": self.termo,
            "pdf_curriculo": base64.b64decode(self.pdf_base64.encode()),
            "dias_maximo": self.dias_maximo,
        }


class RequisitoFaltanteExternoResponse(BaseModel):
    """Requisito técnico não coberto pelo currículo para a vaga externa."""

    nome: str = Field(description="Nome do requisito técnico faltante.")


class VagaDescobertaResponse(BaseModel):
    """Vaga externa descoberta com score de compatibilidade."""

    titulo: str = Field(description="Título da vaga externa.")
    empresa: str = Field(description="Empresa que publicou a vaga.")
    descricao: str = Field(description="Descrição da vaga externa.")
    url: str = Field(description="URL para a vaga na fonte externa.")
    fonte: str = Field(description="Nome da fonte externa de origem.")
    data_publicacao: date | None = Field(
        default=None,
        description="Data de publicação da vaga, quando disponível.",
    )
    nota: int = Field(description="Nota de compatibilidade (0 a 100).")
    requisitos_faltantes: list[RequisitoFaltanteExternoResponse] = Field(
        default_factory=list,
        description="Requisitos técnicos explícitos não cobertos pelo currículo.",
    )

    @classmethod
    def from_dto(cls, dto: VagaComScore) -> VagaDescobertaResponse:
        return cls(
            titulo=dto.vaga.titulo,
            empresa=dto.vaga.empresa,
            descricao=dto.vaga.descricao,
            url=dto.vaga.url,
            fonte=dto.vaga.fonte.name,
            data_publicacao=dto.vaga.data_publicacao,
            nota=dto.resultado_score.nota,
            requisitos_faltantes=[
                RequisitoFaltanteExternoResponse(nome=req.nome)
                for req in dto.resultado_score.requisitos_faltantes
            ],
        )


class DescobrirVagasResponse(BaseModel):
    """Resposta da descoberta de vagas externas."""

    items: list[VagaDescobertaResponse] = Field(
        default_factory=list,
        description="Vagas externas ordenadas por score de compatibilidade.",
    )
    total: int = Field(description="Quantidade total de vagas retornadas.")

    @classmethod
    def from_dto(cls, vagas: tuple[VagaComScore, ...]) -> DescobrirVagasResponse:
        return cls(
            items=[VagaDescobertaResponse.from_dto(vaga) for vaga in vagas],
            total=len(vagas),
        )
