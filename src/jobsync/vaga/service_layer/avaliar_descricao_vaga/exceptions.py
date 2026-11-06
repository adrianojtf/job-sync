"""Exceções do caso de uso AvaliarDescricaoVaga."""


class AvaliacaoDescricaoVagaIndisponivel(RuntimeError):
    """Indica que o Jev não conseguiu produzir uma avaliação utilizável."""

    def __init__(self) -> None:
        super().__init__("O serviço de avaliação de vagas está indisponível.")
