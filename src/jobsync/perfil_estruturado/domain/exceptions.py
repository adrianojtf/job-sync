"""Exceções de domínio do Perfil Estruturado."""
from __future__ import annotations


class PerfilEstruturadoNaoEncontrado(LookupError):
    """O perfil estruturado do identificador informado não existe."""

    def __init__(self) -> None:
        super().__init__("Perfil estruturado não encontrado.")


class ExperienciaNaoEncontrada(LookupError):
    """O perfil não tem experiência na posição informada."""

    def __init__(self) -> None:
        super().__init__("Experiência não encontrada no perfil.")
