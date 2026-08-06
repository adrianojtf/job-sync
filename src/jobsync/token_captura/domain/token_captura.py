"""Entidade de domínio associando um token opaco de captura a um perfil.

Usado pela extensão de navegador para autenticar a captura de vagas sem
exigir um novo sistema de login completo (contexto de uso pessoal/portfólio).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenCaptura:
    """Token opaco que identifica o perfil dono de uma captura de vaga."""

    token: str
    perfil_identificador: str

    def __post_init__(self) -> None:
        if not self.token or not self.token.strip():
            raise ValueError("O token de captura não pode ser vazio.")
        if not self.perfil_identificador or not self.perfil_identificador.strip():
            raise ValueError("O identificador do perfil não pode ser vazio.")
