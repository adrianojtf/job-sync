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


class EnvioEmailFalhou(Exception):
    """Não foi possível entregar o e-mail ao servidor de saída."""


class CredenciaisInvalidas(Exception):
    """E-mail ou senha incorretos. A mensagem nunca diz qual dos dois."""


class TokenInvalido(Exception):
    """Token de uso único inexistente, expirado, já usado ou de outra finalidade."""


class LimiteTentativasExcedido(Exception):
    """Excesso de tentativas de login; a nova tentativa só é aceita após o bloqueio."""

    def __init__(self, retry_after_segundos: int) -> None:
        super().__init__("Muitas tentativas. Tente novamente mais tarde.")
        self.retry_after_segundos = retry_after_segundos


class NaoAutenticado(Exception):
    """A requisição não tem sessão válida."""


class AcessoNegado(Exception):
    """O usuário autenticado não pode acessar o recurso pedido."""


class ProvedorDesconhecido(Exception):
    """O provedor pedido não está configurado."""


class EstadoOAuthInvalido(Exception):
    """O `state` do retorno OAuth é inexistente, expirado, reaproveitado ou não bate com o navegador."""


class EmailNaoVerificado(Exception):
    """O provedor não confirma que o e-mail pertence à pessoa que autenticou."""
