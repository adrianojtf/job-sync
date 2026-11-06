"""Schemas Pydantic para endpoints do domínio de vaga."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from jobsync.entrypoints.api.schemas.avaliacao import (
    ResultadoDimensaoAvaliacaoResponse,
)
from jobsync.vaga import AvaliacaoDescricaoVaga, Vaga
from jobsync.vaga.service_layer.avaliar_descricao_vaga.dtos import (
    AvaliarDescricaoVagaInputDto,
)
from jobsync.vaga.service_layer.capturar_vaga.dtos import CapturarVagaInputDto


class VagaCapturarRequest(BaseModel):
    """Payload para capturar uma vaga a partir de uma descrição."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "perfil_identificador": "matheus",
                "texto_descricao": "Desenvolvedor Python com experiência em FastAPI.",
                "url_origem": "https://example.com/vaga",
            }
        }
    )

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


class AvaliarDescricaoVagaRequest(BaseModel):
    """Payload para avaliar uma descrição de vaga sem persistir seu conteúdo."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "descricao_vaga": (
                    "Pessoa desenvolvedora Python: desenvolver APIs, colaborar com o "
                    "time e manter serviços. Requer experiência com Python e FastAPI."
                )
            }
        }
    )

    descricao_vaga: str = Field(
        min_length=1,
        description="Texto da descrição de vaga a ser avaliada.",
        examples=["Pessoa desenvolvedora Python com experiência em FastAPI."],
    )

    @field_validator("descricao_vaga")
    @classmethod
    def validar_descricao_nao_vazia(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("O texto da descrição da vaga é obrigatório.")
        return valor

    def to_dto(self) -> AvaliarDescricaoVagaInputDto:
        return AvaliarDescricaoVagaInputDto(descricao_vaga=self.descricao_vaga)


class AvaliacaoDescricaoVagaResponse(BaseModel):
    """Score geral e resultados categóricos da descrição de vaga."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "score": 78,
                "completude": {"score": 75, "nivel": "adequada", "confianca": 0.82},
                "clareza": {"score": 80, "nivel": "clara", "confianca": 0.87},
                "relevancia": {"score": 85, "nivel": "relevante", "confianca": 0.91},
                "inclusao": {"score": 72, "nivel": "inclusiva", "confianca": 0.76},
            }
        }
    )

    score: int = Field(
        ge=0,
        le=100,
        description="Média aritmética das quatro dimensões, normalizada de 0 a 100.",
        examples=[78],
    )
    completude: ResultadoDimensaoAvaliacaoResponse = Field(
        description="Avaliação da presença das informações essenciais da vaga."
    )
    clareza: ResultadoDimensaoAvaliacaoResponse = Field(
        description="Avaliação da clareza, organização e ausência de ambiguidades."
    )
    relevancia: ResultadoDimensaoAvaliacaoResponse = Field(
        description="Avaliação da relação entre o conteúdo e o cargo anunciado."
    )
    inclusao: ResultadoDimensaoAvaliacaoResponse = Field(
        description="Avaliação da linguagem respeitosa e inclusiva."
    )

    @classmethod
    def from_domain(
        cls,
        avaliacao: AvaliacaoDescricaoVaga,
    ) -> "AvaliacaoDescricaoVagaResponse":
        return cls(
            score=avaliacao.score,
            completude=ResultadoDimensaoAvaliacaoResponse.from_domain(
                avaliacao.completude
            ),
            clareza=ResultadoDimensaoAvaliacaoResponse.from_domain(avaliacao.clareza),
            relevancia=ResultadoDimensaoAvaliacaoResponse.from_domain(
                avaliacao.relevancia
            ),
            inclusao=ResultadoDimensaoAvaliacaoResponse.from_domain(avaliacao.inclusao),
        )
