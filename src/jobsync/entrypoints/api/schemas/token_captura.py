"""Schemas Pydantic para endpoints do domínio de token de captura."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from jobsync.token_captura import TokenCaptura


class TokenCapturaCriarRequest(BaseModel):
    """Payload para gerar um novo token de captura para um perfil."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"perfil_identificador": "adriano"}}
    )

    perfil_identificador: str = Field(
        min_length=1,
        description="Identificador do perfil dono do token.",
    )

    @field_validator("perfil_identificador")
    @classmethod
    def validar_perfil_nao_vazio(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("O identificador do perfil é obrigatório.")
        return valor.strip()


class TokenCapturaResponse(BaseModel):
    """Token opaco usado pela extensão de navegador para capturar vagas."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "kq3Jx0d9X1r8yJ2wq7l1u5H4nM6bV0cA",
                "perfil_identificador": "adriano",
            }
        }
    )

    token: str = Field(description="Token opaco a ser informado na extensão de navegador.")
    perfil_identificador: str = Field(description="Identificador do perfil dono do token.")

    @classmethod
    def from_domain(cls, token: TokenCaptura) -> TokenCapturaResponse:
        return cls(token=token.token, perfil_identificador=token.perfil_identificador)
