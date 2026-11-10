"""Schemas Pydantic dos endpoints de autenticação."""
from __future__ import annotations

from typing import Annotated, Optional

from pydantic import BaseModel, Field, StringConstraints

from jobsync.autenticacao.domain.usuario import Usuario

Identificador = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class CadastroRequest(BaseModel):
    email: str = Field(max_length=254, description="E-mail que será confirmado por link.")
    senha: str = Field(max_length=256, description="Senha escolhida; só vale após confirmar o e-mail.")


class LoginRequest(BaseModel):
    email: str = Field(max_length=254)
    senha: str = Field(max_length=256)


class LoginSimplesRequest(BaseModel):
    identificador: Identificador = Field(description="Identificador do perfil (apenas desenvolvimento).")


class SolicitacaoRedefinicaoRequest(BaseModel):
    email: str = Field(max_length=254)


class NovaSenhaRequest(BaseModel):
    nova_senha: str = Field(max_length=256)


class MensagemResponse(BaseModel):
    mensagem: str


class UsuarioResponse(BaseModel):
    id: str
    email: str
    nome: Optional[str] = None
    perfil_identificador: str = Field(description="Perfil dono dos dados deste usuário.")

    @classmethod
    def from_domain(cls, usuario: Usuario) -> UsuarioResponse:
        return cls(
            id=str(usuario.id),
            email=usuario.email.valor,
            nome=usuario.nome,
            perfil_identificador=usuario.perfil_identificador,
        )


class ProvedoresResponse(BaseModel):
    provedores: list[str] = Field(description="Provedores de identidade configurados (ex.: google).")
    senha: bool = Field(description="Se o login por e-mail e senha está disponível.")
    login_simples: bool = Field(description="Se o login legado por identificador está habilitado.")
