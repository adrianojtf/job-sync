"""Camada de domínio da Autenticação."""

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.estado_oauth import EstadoOAuth
from jobsync.autenticacao.domain.exceptions import EmailInvalido, SenhaInvalida
from jobsync.autenticacao.domain.identidade_externa import IdentidadeExterna
from jobsync.autenticacao.domain.senha import Senha
from jobsync.autenticacao.domain.sessao import Sessao
from jobsync.autenticacao.domain.token_uso_unico import Finalidade, TokenUsoUnico
from jobsync.autenticacao.domain.usuario import Usuario, novo_identificador_de_perfil

__all__ = [
    "Email",
    "EmailInvalido",
    "EstadoOAuth",
    "Finalidade",
    "IdentidadeExterna",
    "Senha",
    "SenhaInvalida",
    "Sessao",
    "TokenUsoUnico",
    "Usuario",
    "novo_identificador_de_perfil",
]
