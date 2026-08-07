"""Schemas Pydantic para endpoints do domínio de vaga."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from jobsync.vaga import Vaga
from jobsync.vaga.service_layer.capturar_vaga.dtos import CapturarVagaInputDto


class VagaCapturarRequest(BaseModel):
    """Payload para capturar uma vaga a partir de uma descrição."""

    perfil_identificador: str = Field(description="Identificador único do perfil que capturou a vaga.")
    texto_descricao: str = Field(description="Texto completo da descrição da vaga.")
    url_origem: str | None = Field(
        default=None,
        description="URL de origem da vaga, quando disponível.",
    )

    def to_dto(self) -> CapturarVagaInputDto:
        return CapturarVagaInputDto(
            perfil_identificador=self.perfil_identificador,
            texto_descricao=self.texto_descricao,
            url_origem=self.url_origem,
        )


class VagaResponse(BaseModel):
    """Representação de uma vaga capturada."""

    id: str = Field(description="Identificador único da vaga.")
    perfil_identificador: str = Field(description="Identificador do perfil que capturou a vaga.")
    texto_descricao: str = Field(description="Texto completo da descrição da vaga.")
    data_captura: datetime = Field(description="Data e hora em que a vaga foi capturada.")
    url_origem: str | None = Field(
        default=None,
        description="URL de origem da vaga, quando disponível.",
    )

    @classmethod
    def from_dto(cls, dto: Vaga) -> VagaResponse:
        return cls(
            id=dto.id,
            perfil_identificador=dto.perfil_identificador,
            texto_descricao=dto.texto_descricao,
            data_captura=dto.data_captura,
            url_origem=dto.url_origem,
        )


class VagasListagemResponse(BaseModel):
    """Resposta paginada da listagem de vagas capturadas de um perfil."""

    items: list[VagaResponse] = Field(
        default_factory=list,
        description="Lista de vagas capturadas.",
    )
    total: int = Field(description="Quantidade total de vagas na listagem.")
    limite: int = Field(description="Quantidade máxima de itens retornados.")
    offset: int = Field(description="Quantidade de itens pulados a partir do início.")

    @classmethod
    def from_dto(
        cls,
        vagas: tuple[Vaga, ...],
        limite: int = 100,
        offset: int = 0,
    ) -> VagasListagemResponse:
        return cls(
            items=[VagaResponse.from_dto(vaga) for vaga in vagas],
            total=len(vagas),
            limite=limite,
            offset=offset,
        )
