"""Exceções do domínio Autenticação."""
from __future__ import annotations


class EmailInvalido(ValueError):
    """O texto informado não é um e-mail válido."""


class SenhaInvalida(ValueError):
    """A senha não atende à política de senhas."""
