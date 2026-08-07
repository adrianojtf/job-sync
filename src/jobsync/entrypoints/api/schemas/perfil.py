"""Schemas Pydantic para endpoints do domínio de perfil."""

from __future__ import annotations

from pydantic import BaseModel, Field

from jobsync.perfil import Perfil


class PerfilResponse(BaseModel):
    """Representação de um perfil de usuário."""

    identificador: str = Field(description="Identificador único do perfil.")

    @classmethod
    def from_dto(cls, dto: Perfil) -> PerfilResponse:
        return cls(identificador=dto.identificador)


class PerfisListagemResponse(BaseModel):
    """Resposta da listagem de perfis."""

    items: list[PerfilResponse] = Field(
        default_factory=list,
        description="Lista de perfis.",
    )
    total: int = Field(description="Quantidade total de perfis.")

    @classmethod
    def from_dto(cls, perfis: tuple[Perfil, ...]) -> PerfisListagemResponse:
        return cls(
            items=[PerfilResponse.from_dto(perfil) for perfil in perfis],
            total=len(perfis),
        )
