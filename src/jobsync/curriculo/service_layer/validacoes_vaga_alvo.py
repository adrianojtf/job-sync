"""Validações da vaga-alvo comuns aos casos de uso que geram o currículo adaptado."""

IDIOMAS_SUPORTADOS = {"pt", "en"}


def validar_idioma_alvo(idioma_alvo: str) -> None:
    """Levanta ValueError se o idioma alvo não for suportado."""
    if idioma_alvo not in IDIOMAS_SUPORTADOS:
        raise ValueError(
            f"idioma alvo inválido: '{idioma_alvo}'. "
            f"Idiomas suportados: {sorted(IDIOMAS_SUPORTADOS)}"
        )


def validar_cargo_e_empresa_alvo(cargo_alvo: str, empresa_alvo: str) -> None:
    """Levanta ValueError se cargo ou empresa alvo estiverem vazios."""
    if not cargo_alvo or not cargo_alvo.strip():
        raise ValueError("O cargo alvo é obrigatório.")
    if not empresa_alvo or not empresa_alvo.strip():
        raise ValueError("A empresa alvo é obrigatória.")
