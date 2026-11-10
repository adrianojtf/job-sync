"""Value object de e-mail, sempre normalizado."""
from __future__ import annotations

import re
from dataclasses import dataclass

from jobsync.autenticacao.domain.exceptions import EmailInvalido

_TAMANHO_MAXIMO = 254
_FORMATO = re.compile(r"^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$")


@dataclass(frozen=True)
class Email:
    """E-mail em minúsculas e sem espaços nas pontas."""

    valor: str

    def __post_init__(self) -> None:
        normalizado = self.valor.strip().lower()
        if len(normalizado) > _TAMANHO_MAXIMO or not _FORMATO.match(normalizado):
            raise EmailInvalido("O e-mail informado não é válido.")
        object.__setattr__(self, "valor", normalizado)

    @property
    def parte_local(self) -> str:
        return self.valor.split("@", 1)[0]
