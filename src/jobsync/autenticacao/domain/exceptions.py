"""Exceções do domínio Autenticação."""
from __future__ import annotations


class EmailInvalido(ValueError):
    """O texto informado não é um e-mail válido."""


class SenhaInvalida(ValueError):
    """A senha não atende à política de senhas."""


class UsuarioDuplicado(Exception):
    """Já existe usuário com o mesmo e-mail ou associado ao mesmo perfil."""


class IdentidadeJaVinculada(Exception):
    """A identidade externa já está vinculada a um usuário."""


class ProvedorIndisponivel(Exception):
    """Falha ao falar com o provedor de identidade ou resposta inválida dele."""
