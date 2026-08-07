"""Schemas Pydantic para endpoints do domínio de currículo."""

from __future__ import annotations

import base64
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from jobsync.curriculo import Curriculo
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.dtos import (
    AdaptarCurriculoParaVagaInputDto,
    AdaptarCurriculoParaVagaOutputDto,
)
from jobsync.curriculo.service_layer.analisar_ats_vaga.dtos import (
    AnalisarAtsVagaInputDto,
    AnalisarAtsVagaOutputDto,
)
from jobsync.curriculo_salvo import CurriculoSalvo
from jobsync.curriculo_salvo.service_layer.salvar_curriculo.dtos import (
    SalvarCurriculoInputDto,
)


class CurriculoSalvarRequest(BaseModel):
    """Payload para salvar um currículo PDF na biblioteca de um perfil."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "perfil_identificador": "matheus",
                "nome_referencia": "Curriculo.pdf",
                "pdf_base64": "JVBERi0xLjQgdGVzdA==",
            }
        }
    )

    perfil_identificador: str = Field(description="Identificador único do perfil dono do currículo.")
    nome_referencia: str = Field(description="Nome amigável para o currículo salvo.")
    pdf_base64: str = Field(description="Conteúdo do PDF codificado em base64.")

    def to_dto(self) -> SalvarCurriculoInputDto:
        return SalvarCurriculoInputDto(
            perfil_identificador=self.perfil_identificador,
            nome_referencia=self.nome_referencia,
            pdf_bytes=base64.b64decode(self.pdf_base64.encode()),
        )


class CurriculoSalvoResponse(BaseModel):
    """Representação de um currículo salvo na biblioteca."""

    id: str = Field(description="Identificador único do currículo salvo.")
    perfil_identificador: str = Field(description="Identificador do perfil dono do currículo.")
    nome_referencia: str = Field(description="Nome amigável do currículo salvo.")
    data_upload: datetime = Field(description="Data e hora do upload do currículo.")

    @classmethod
    def from_dto(cls, dto: CurriculoSalvo) -> CurriculoSalvoResponse:
        return cls(
            id=dto.id,
            perfil_identificador=dto.perfil_identificador,
            nome_referencia=dto.nome_referencia,
            data_upload=dto.data_upload,
        )


class AdaptarCurriculoRequest(BaseModel):
    """Payload para adaptar um currículo a uma vaga específica."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "descricao_vaga": "Desenvolvedor Python com experiência em FastAPI.",
                "idioma_alvo": "pt",
                "cargo_alvo": "Engenheiro de Software",
                "empresa_alvo": "TechCorp",
                "pdf_base64": "JVBERi0xLjQgdGVzdA==",
            }
        }
    )

    descricao_vaga: str = Field(description="Texto completo da descrição da vaga.")
    idioma_alvo: str = Field(description="Idioma de destino do currículo adaptado.")
    cargo_alvo: str = Field(description="Cargo alvo do currículo.")
    empresa_alvo: str = Field(description="Empresa alvo do currículo.")
    pdf_base64: str = Field(description="Conteúdo do PDF do currículo codificado em base64.")
    data_referencia: date | None = Field(
        default=None,
        description="Data de referência para composição do nome do arquivo.",
    )

    def to_dto(self) -> AdaptarCurriculoParaVagaInputDto:
        return AdaptarCurriculoParaVagaInputDto(
            descricao_vaga=self.descricao_vaga,
            idioma_alvo=self.idioma_alvo,
            cargo_alvo=self.cargo_alvo,
            empresa_alvo=self.empresa_alvo,
            pdf_curriculo=base64.b64decode(self.pdf_base64.encode()),
            curriculo_pre_montado=None,
            data_referencia=self.data_referencia,
        )


class AdaptarCurriculoResponse(BaseModel):
    """Resultado da adaptação de um currículo para uma vaga."""

    nome_arquivo: str = Field(description="Nome padronizado do PDF gerado.")
    pdf_base64: str = Field(description="PDF do currículo adaptado codificado em base64.")
    nome_completo: str = Field(description="Nome completo do candidato extraído do currículo.")

    @classmethod
    def from_dto(cls, dto: AdaptarCurriculoParaVagaOutputDto) -> AdaptarCurriculoResponse:
        return cls(
            nome_arquivo=dto.nome_arquivo.valor,
            pdf_base64=base64.b64encode(dto.pdf_bytes).decode(),
            nome_completo=dto.curriculo_adaptado.nome_completo,
        )


class AnalisarAtsRequest(BaseModel):
    """Payload para análise de aderência ATS de um currículo a uma vaga."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "descricao_vaga": "Desenvolvedor Python com experiência em FastAPI.",
                "pdf_base64": "JVBERi0xLjQgdGVzdA==",
            }
        }
    )

    descricao_vaga: str = Field(description="Texto completo da descrição da vaga.")
    pdf_base64: str = Field(description="Conteúdo do PDF do currículo codificado em base64.")

    def to_dto(self) -> AnalisarAtsVagaInputDto:
        return AnalisarAtsVagaInputDto(
            descricao_vaga=self.descricao_vaga,
            pdf_curriculo=base64.b64decode(self.pdf_base64.encode()),
            curriculo_pre_montado=None,
        )


class RequisitoFaltanteResponse(BaseModel):
    """Requisito técnico não coberto pelo currículo."""

    nome: str = Field(description="Nome do requisito técnico faltante.")
    categoria: str = Field(description="Categoria do requisito técnico.")
    tipo: str = Field(description="Tipo do requisito técnico (explícito, implícito ou ambíguo).")


class AnalisarAtsResponse(BaseModel):
    """Resultado da análise de aderência ATS."""

    nome_completo: str = Field(description="Nome completo do candidato.")
    nota: int = Field(description="Nota de aderência (0 a 100).")
    requisitos_faltantes: list[RequisitoFaltanteResponse] = Field(
        default_factory=list,
        description="Requisitos técnicos explícitos não cobertos pelo currículo.",
    )
    sugestoes: list[str] = Field(
        default_factory=list,
        description="Sugestões de melhoria para aumentar a aderência.",
    )

    @classmethod
    def from_dto(cls, dto: AnalisarAtsVagaOutputDto) -> AnalisarAtsResponse:
        return cls(
            nome_completo=dto.curriculo.nome_completo,
            nota=dto.resultado_ats.nota,
            requisitos_faltantes=[
                RequisitoFaltanteResponse(
                    nome=req.nome,
                    categoria=req.categoria.name,
                    tipo=req.tipo.name,
                )
                for req in dto.resultado_ats.requisitos_faltantes
            ],
            sugestoes=list(dto.sugestoes),
        )
