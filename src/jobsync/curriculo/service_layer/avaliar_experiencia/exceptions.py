"""Exceções do caso de uso AvaliarExperiencia."""


class AvaliacaoExperienciaIndisponivel(RuntimeError):
    """Indica que o Jev não conseguiu produzir uma avaliação utilizável."""

    def __init__(self) -> None:
        super().__init__("O serviço de avaliação de experiência está indisponível.")
