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


class CompletarBlocosIndisponivel(RuntimeError):
    """A IA não conseguiu completar os blocos de uma experiência."""

    def __init__(self) -> None:
        super().__init__("O serviço de IA para completar os blocos da experiência está indisponível.")
