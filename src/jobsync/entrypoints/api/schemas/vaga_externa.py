"""Schemas Pydantic para endpoints do domínio de vaga externa."""

from __future__ import annotations

import base64
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from jobsync.curriculo import Curriculo
from jobsync.entrypoints.api.schemas.curriculo import RequisitoFaltanteResponse
from jobsync.vaga_externa import FonteVagaExterna, VagaComScore, VagaExterna
from jobsync.vaga_externa.service_layer.candidatar_na_vaga_externa import (
    CandidatarNaVagaExternaInputDto,
    CandidatarNaVagaExternaOutputDto,
)


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


class VagaDescobertaRequest(BaseModel):
    """Dados da vaga descoberta, como retornados por POST /v1/vagas/descobrir."""

    titulo: str = Field(min_length=1, description="Título da vaga externa.")
    empresa: str = Field(min_length=1, description="Empresa que publicou a vaga.")
    descricao: str = Field(min_length=1, description="Descrição da vaga externa.")
    url: str = Field(min_length=1, description="URL para a vaga na fonte externa.")
    fonte: str = Field(
        description="Nome da fonte externa de origem, como retornado em `fonte`.",
        json_schema_extra={"enum": [fonte.name for fonte in FonteVagaExterna]},
    )
    descricao_incompleta: bool = Field(
        default=False,
        description="Indica que a fonte só forneceu um trecho da descrição.",
    )
    data_publicacao: date | None = Field(
        default=None,
        description="Data de publicação da vaga, quando disponível.",
    )

    @field_validator("fonte")
    @classmethod
    def validar_fonte(cls, valor: str) -> str:
        if valor not in FonteVagaExterna.__members__:
            raise ValueError(f"Fonte desconhecida: {valor}.")
        return valor

    def to_domain(self) -> VagaExterna:
        return VagaExterna(
            titulo=self.titulo,
            empresa=self.empresa,
            descricao=self.descricao,
            url=self.url,
            fonte=FonteVagaExterna[self.fonte],
            descricao_incompleta=self.descricao_incompleta,
            data_publicacao=self.data_publicacao,
        )


class CandidatarVagaExternaRequest(BaseModel):
    """Payload para gerar os artefatos de candidatura a uma vaga descoberta.

    Informe `perfil_identificador` (perfil estruturado) ou `pdf_base64`.
    Sem `cargo_alvo`/`empresa_alvo`, são usados o título e a empresa da vaga.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "vaga": {
                    "titulo": "Backend Engineer",
                    "empresa": "Olist",
                    "descricao": "Vaga para Java e Kafka.",
                    "url": "https://example.com/vaga/1",
                    "fonte": "REMOTEOK",
                },
                "idioma_alvo": "pt",
                "perfil_identificador": "adriano",
            }
        },
    )

    vaga: VagaDescobertaRequest = Field(description="Vaga descoberta para a candidatura.")
    idioma_alvo: str = Field(description="Idioma do currículo e da carta (pt ou en).")
    cargo_alvo: str | None = Field(default=None, description="Cargo alvo. Padrão: título da vaga.")
    empresa_alvo: str | None = Field(default=None, description="Empresa alvo. Padrão: empresa da vaga.")
    perfil_identificador: str | None = Field(
        default=None,
        description="Perfil estruturado usado como fonte do currículo.",
    )
    pdf_base64: str | None = Field(
        default=None,
        description="PDF do currículo em base64, quando não houver perfil estruturado.",
    )
    data_referencia: date | None = Field(
        default=None,
        description="Data usada no nome do arquivo. Padrão: hoje.",
    )

    def to_dto(self, curriculo_pre_montado: Curriculo | None = None) -> CandidatarNaVagaExternaInputDto:
        return CandidatarNaVagaExternaInputDto(
            vaga=self.vaga.to_domain(),
            idioma_alvo=self.idioma_alvo,
            cargo_alvo=self.cargo_alvo or self.vaga.titulo,
            empresa_alvo=self.empresa_alvo or self.vaga.empresa,
            pdf_curriculo=base64.b64decode(self.pdf_base64.encode()) if self.pdf_base64 else None,
            curriculo_pre_montado=curriculo_pre_montado,
            data_referencia=self.data_referencia,
        )


class CandidatarVagaExternaResponse(BaseModel):
    """Artefatos prontos para a candidatura: PDF adaptado, nota ATS e carta."""

    nome_arquivo: str = Field(description="Nome padronizado do PDF gerado.")
    pdf_base64: str = Field(description="PDF do currículo adaptado codificado em base64.")
    nota: int = Field(description="Nota ATS do currículo adaptado (0 a 100).")
    requisitos_faltantes: list[RequisitoFaltanteResponse] = Field(
        default_factory=list,
        description="Requisitos técnicos não cobertos pelo currículo adaptado.",
    )
    carta: str = Field(description="Texto da carta de apresentação.")
    url_vaga: str = Field(description="URL da vaga original, para o candidato aplicar.")

    @classmethod
    def from_dto(cls, dto: CandidatarNaVagaExternaOutputDto) -> CandidatarVagaExternaResponse:
        return cls(
            nome_arquivo=dto.nome_arquivo.valor,
            pdf_base64=base64.b64encode(dto.pdf_bytes).decode(),
            nota=dto.resultado_ats.nota,
            requisitos_faltantes=[
                RequisitoFaltanteResponse(nome=req.nome, categoria=req.categoria.name, tipo=req.tipo.name)
                for req in dto.resultado_ats.requisitos_faltantes
            ],
            carta=dto.carta_apresentacao,
            url_vaga=dto.url_vaga,
        )
