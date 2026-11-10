"""Camada de domínio da Autenticação."""

from jobsync.autenticacao.domain.configuracao import ConfiguracaoAutenticacao
from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.enviador_email import EnviadorEmail
from jobsync.autenticacao.domain.estado_oauth import EstadoOAuth
from jobsync.autenticacao.domain.estado_oauth_repository import EstadoOAuthRepository
from jobsync.autenticacao.domain.exceptions import (
    AcessoNegado,
    CredenciaisInvalidas,
    EmailInvalido,
    EmailNaoVerificado,
    EnvioEmailFalhou,
    EstadoOAuthInvalido,
    IdentidadeJaVinculada,
    LimiteTentativasExcedido,
    NaoAutenticado,
    ProvedorDesconhecido,
    ProvedorIndisponivel,
    SenhaInvalida,
    TokenInvalido,
    UsuarioDuplicado,
)
from jobsync.autenticacao.domain.hasher_senha import HasherSenha
from jobsync.autenticacao.domain.identidade_externa import IdentidadeExterna
from jobsync.autenticacao.domain.limite_tentativa import LimiteTentativa, PoliticaLimiteTentativas
from jobsync.autenticacao.domain.limite_tentativas_repository import LimiteTentativasRepository
from jobsync.autenticacao.domain.provedor_identidade import IdentidadeAutenticada, ProvedorIdentidade
from jobsync.autenticacao.domain.senha import Senha
from jobsync.autenticacao.domain.sessao import Sessao
from jobsync.autenticacao.domain.sessao_repository import SessaoRepository
from jobsync.autenticacao.domain.token_uso_unico import Finalidade, TokenUsoUnico
from jobsync.autenticacao.domain.token_uso_unico_repository import TokenUsoUnicoRepository
from jobsync.autenticacao.domain.usuario import Usuario, novo_identificador_de_perfil
from jobsync.autenticacao.domain.usuario_repository import UsuarioRepository

__all__ = [
    "AcessoNegado",
    "ConfiguracaoAutenticacao",
    "CredenciaisInvalidas",
    "LimiteTentativasExcedido",
    "NaoAutenticado",
    "TokenInvalido",
    "Email",
    "EmailInvalido",
    "EmailNaoVerificado",
    "EnviadorEmail",
    "EnvioEmailFalhou",
    "EstadoOAuth",
    "EstadoOAuthInvalido",
    "EstadoOAuthRepository",
    "Finalidade",
    "HasherSenha",
    "IdentidadeAutenticada",
    "IdentidadeExterna",
    "IdentidadeJaVinculada",
    "LimiteTentativa",
    "LimiteTentativasRepository",
    "PoliticaLimiteTentativas",
    "ProvedorDesconhecido",
    "ProvedorIdentidade",
    "ProvedorIndisponivel",
    "Senha",
    "SenhaInvalida",
    "Sessao",
    "SessaoRepository",
    "TokenUsoUnico",
    "TokenUsoUnicoRepository",
    "Usuario",
    "UsuarioDuplicado",
    "UsuarioRepository",
    "novo_identificador_de_perfil",
]
