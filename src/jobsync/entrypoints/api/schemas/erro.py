"""Schema de erro RFC 7807 usado pela API."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProblemaResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "https://jobsync.com/erros/avaliacao-vaga-indisponivel",
                "title": "Avaliação de vaga indisponível",
                "status": 502,
                "detail": "O serviço de avaliação de vagas está indisponível.",
                "instance": "http://localhost/v1/vagas/avaliacoes",
            }
        }
    )

    type: str = Field(
        description="URI que identifica o tipo de problema.",
        examples=["https://jobsync.com/erros/avaliacao-vaga-indisponivel"],
    )
    title: str = Field(
        description="Resumo legível do problema.",
        examples=["Avaliação de vaga indisponível"],
    )
    status: int = Field(
        description="Código HTTP retornado.",
        examples=[502],
    )
    detail: str = Field(
        description="Descrição segura do problema.",
        examples=["O serviço de avaliação de vagas está indisponível."],
    )
    instance: str = Field(
        description="URI da requisição que encontrou o problema.",
        examples=["http://localhost/v1/vagas/avaliacoes"],
    )
