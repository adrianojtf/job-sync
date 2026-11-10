"""Adapters concretos do domínio Autenticação."""

from jobsync.autenticacao.adapters.estado_oauth_repository_fake import EstadoOAuthRepositoryFake
from jobsync.autenticacao.adapters.estado_oauth_repository_impl import EstadoOAuthRepositoryImpl
from jobsync.autenticacao.adapters.enviador_email_log import EnviadorEmailLog
from jobsync.autenticacao.adapters.enviador_email_smtp import EnviadorEmailSmtp
from jobsync.autenticacao.adapters.hasher_senha_argon2 import HasherSenhaArgon2
from jobsync.autenticacao.adapters.limite_tentativas_repository_fake import LimiteTentativasRepositoryFake
from jobsync.autenticacao.adapters.limite_tentativas_repository_impl import LimiteTentativasRepositoryImpl
from jobsync.autenticacao.adapters.provedor_google import ProvedorGoogle
from jobsync.autenticacao.adapters.sessao_repository_fake import SessaoRepositoryFake
from jobsync.autenticacao.adapters.sessao_repository_impl import SessaoRepositoryImpl
from jobsync.autenticacao.adapters.token_uso_unico_repository_fake import TokenUsoUnicoRepositoryFake
from jobsync.autenticacao.adapters.token_uso_unico_repository_impl import TokenUsoUnicoRepositoryImpl
from jobsync.autenticacao.adapters.usuario_repository_fake import UsuarioRepositoryFake
from jobsync.autenticacao.adapters.usuario_repository_impl import UsuarioRepositoryImpl

__all__ = [
    "EnviadorEmailLog",
    "EnviadorEmailSmtp",
    "HasherSenhaArgon2",
    "ProvedorGoogle",
    "EstadoOAuthRepositoryFake",
    "EstadoOAuthRepositoryImpl",
    "LimiteTentativasRepositoryFake",
    "LimiteTentativasRepositoryImpl",
    "SessaoRepositoryFake",
    "SessaoRepositoryImpl",
    "TokenUsoUnicoRepositoryFake",
    "TokenUsoUnicoRepositoryImpl",
    "UsuarioRepositoryFake",
    "UsuarioRepositoryImpl",
]
