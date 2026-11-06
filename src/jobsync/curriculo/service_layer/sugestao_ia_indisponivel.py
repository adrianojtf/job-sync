"""Exceção compartilhada pelos casos de uso de sugestão de IA."""


class SugestaoIAIndisponivel(RuntimeError):
    """Indica que a IA não conseguiu produzir uma sugestão utilizável."""

    def __init__(self) -> None:
        super().__init__("O serviço de sugestões de IA está indisponível.")
