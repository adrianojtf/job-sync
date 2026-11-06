"""Schemas Pydantic para endpoints do domínio de candidatura."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from jobsync.candidatura import Candidatura, MudancaStatus, StatusCandidatura
from jobsync.candidatura.service_layer.criar_candidatura.dtos import (
    CriarCandidaturaInputDto,
)


class CandidaturaCriarRequest(BaseModel):
    """Payload para criar uma nova candidatura."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "perfil_identificador": "matheus",
                "vaga_id": "vaga-123",
                "curriculo_salvo_id": "curriculo-123",
                "empresa": "TechCorp",
                "cargo": "Engenheiro de Software",
            }
        }
    )

    perfil_identificador: str = Field(description="Identificador do perfil candidato.")
    vaga_id: str = Field(description="Identificador da vaga associada.")
    curriculo_salvo_id: str = Field(description="Identificador do currículo salvo a ser usado.")
    empresa: str = Field(description="Nome da empresa da vaga.")
    cargo: str = Field(description="Cargo da vaga.")

    def to_dto(self) -> CriarCandidaturaInputDto:
        return CriarCandidaturaInputDto(
            perfil_identificador=self.perfil_identificador,
            vaga_id=self.vaga_id,
            curriculo_salvo_id=self.curriculo_salvo_id,
            empresa=self.empresa,
            cargo=self.cargo,
        )


class CandidaturaSubmeterRequest(BaseModel):
    """Payload para submeter/mover o status de uma candidatura."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "novo_status": "entrevista",
            }
        }
    )

    novo_status: str = Field(
        description="Novo status da candidatura (aplicado, entrevista, oferta ou rejeitado).",
        json_schema_extra={"enum": [status.name.lower() for status in StatusCandidatura]},
    )

    @field_validator("novo_status")
    @classmethod
    def validar_novo_status(cls, valor: str) -> str:
        if valor.upper() not in StatusCandidatura.__members__:
            aceitos = ", ".join(status.name.lower() for status in StatusCandidatura)
            raise ValueError(f"O status deve ser um destes: {aceitos}.")
        return valor

    def to_dto(self) -> dict[str, Any]:
        return {
            "novo_status": StatusCandidatura[self.novo_status.upper()],
        }


class MudancaStatusResponse(BaseModel):
    """Registro de uma mudança de status da candidatura."""

    status: str = Field(description="Status registrado.")
    data: datetime = Field(description="Data e hora da mudança.")

    @classmethod
    def from_dto(cls, dto: MudancaStatus) -> MudancaStatusResponse:
        return cls(
            status=dto.status.name,
            data=dto.data,
        )


class CandidaturaResponse(BaseModel):
    """Representação de uma candidatura."""

    id: str = Field(description="Identificador único da candidatura.")
    perfil_identificador: str = Field(description="Identificador do perfil candidato.")
    vaga_id: str = Field(description="Identificador da vaga associada.")
    curriculo_salvo_id: str = Field(description="Identificador do currículo salvo usado.")
    empresa: str = Field(description="Nome da empresa da vaga.")
    cargo: str = Field(description="Cargo da vaga.")
    status: str = Field(description="Status atual da candidatura.")
    data_aplicacao: datetime = Field(description="Data e hora de criação da candidatura.")
    historico_status: list[MudancaStatusResponse] = Field(
        default_factory=list,
        description="Histórico de mudanças de status.",
    )

    @classmethod
    def from_dto(cls, dto: Candidatura) -> CandidaturaResponse:
        return cls(
            id=dto.id,
            perfil_identificador=dto.perfil_identificador,
            vaga_id=dto.vaga_id,
            curriculo_salvo_id=dto.curriculo_salvo_id,
            empresa=dto.empresa,
            cargo=dto.cargo,
            status=dto.status.name,
            data_aplicacao=dto.data_aplicacao,
            historico_status=[MudancaStatusResponse.from_dto(m) for m in dto.historico_status],
        )


class CandidaturasListagemResponse(BaseModel):
    """Resposta da listagem de candidaturas agrupadas por status."""

    por_status: dict[str, list[CandidaturaResponse]] = Field(
        default_factory=dict,
        description="Candidaturas agrupadas por status.",
    )
    total: int = Field(description="Quantidade total de candidaturas.")

    @classmethod
    def from_dto(
        cls,
        agrupadas: dict[StatusCandidatura, tuple[Candidatura, ...]],
    ) -> CandidaturasListagemResponse:
        por_status = {
            status.name: [CandidaturaResponse.from_dto(c) for c in agrupadas.get(status, ())]
            for status in StatusCandidatura
        }
        total = sum(len(cands) for cands in por_status.values())
        return cls(
            por_status=por_status,
            total=total,
        )
