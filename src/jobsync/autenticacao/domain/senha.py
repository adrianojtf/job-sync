"""Value object de senha com a política de senhas do produto."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import SenhaInvalida

TAMANHO_MINIMO = 10
TAMANHO_MAXIMO = 128

_SENHAS_COMUNS = frozenset(
    {
        "1234567890",
        "0123456789",
        "12345678910",
        "123456789012",
        "1q2w3e4r5t",
        "1qaz2wsx3e",
        "qwertyuiop",
        "qwerty1234",
        "qwerty12345",
        "asdfghjkl1",
        "abcdefghij",
        "abcd123456",
        "password12",
        "password123",
        "password1234",
        "passw0rd123",
        "senha12345",
        "senha123456",
        "senhasenha",
        "mudar12345",
        "adminadmin",
        "admin12345",
        "iloveyou12",
        "welcome123",
        "letmein123",
        "0000000000",
        "1111111111",
        "aaaaaaaaaa",
    }
)


@dataclass(frozen=True)
class Senha:
    """Senha em texto puro que já passou pela política; vive só até ser transformada em hash."""

    valor: str = field(repr=False)
    email: Optional[Email] = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not TAMANHO_MINIMO <= len(self.valor) <= TAMANHO_MAXIMO:
            raise SenhaInvalida(
                f"A senha deve ter entre {TAMANHO_MINIMO} e {TAMANHO_MAXIMO} caracteres."
            )
        minuscula = self.valor.lower()
        if minuscula in _SENHAS_COMUNS:
            raise SenhaInvalida("Essa senha é muito comum. Escolha outra.")
        if self.email is not None and minuscula == self.email.parte_local:
            raise SenhaInvalida("A senha não pode ser igual ao seu e-mail.")
