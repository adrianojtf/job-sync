"""Exceções do domínio Currículo Adaptado."""


class CurriculoAdaptadoNaoEncontrado(Exception):
    """O currículo adaptado não existe ou pertence a outro perfil."""

    def __init__(self) -> None:
        super().__init__("Currículo adaptado não encontrado.")
