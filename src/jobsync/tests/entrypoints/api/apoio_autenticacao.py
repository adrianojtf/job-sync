"""Apoio dos testes de API: monta os serviços de autenticação sobre repositórios fake."""

from types import SimpleNamespace

from jobsync.autenticacao.adapters import (
    EstadoOAuthRepositoryFake,
    LimiteTentativasRepositoryFake,
    SessaoRepositoryFake,
    TokenUsoUnicoRepositoryFake,
    UsuarioRepositoryFake,
)
from jobsync.autenticacao.domain.configuracao import ConfiguracaoAutenticacao
from jobsync.autenticacao.domain.provedor_identidade import IdentidadeAutenticada
from jobsync.entrypoints.autenticacao_config import ConfiguracaoHttpAutenticacao
from jobsync.entrypoints.autenticacao_servicos import montar_servicos_autenticacao
from jobsync.tests.autenticacao.dobles import EnviadorEmailFalso, HasherSenhaFalso, ProvedorFalso, RelogioFalso

FRONTEND = "http://localhost:8080"


def montar_mundo(login_simples=False, cookie_secure=False, cabecalho_ip_cliente=None):
    mundo = SimpleNamespace(
        usuarios=UsuarioRepositoryFake(),
        sessoes=SessaoRepositoryFake(),
        tokens=TokenUsoUnicoRepositoryFake(),
        estados=EstadoOAuthRepositoryFake(),
        limites=LimiteTentativasRepositoryFake(),
        enviador=EnviadorEmailFalso(),
        relogio=RelogioFalso(),
        provedor=ProvedorFalso(),
    )
    mundo.provedor.identidade = IdentidadeAutenticada("google", "sub-1", "ana@exemplo.com", True, "Ana Souza")
    mundo.servicos = montar_servicos_autenticacao(
        usuarios=mundo.usuarios,
        sessoes=mundo.sessoes,
        tokens=mundo.tokens,
        estados=mundo.estados,
        limites=mundo.limites,
        hasher=HasherSenhaFalso(),
        enviador=mundo.enviador,
        provedores={"google": mundo.provedor},
        config=ConfiguracaoAutenticacao(url_frontend=FRONTEND),
        http=ConfiguracaoHttpAutenticacao(
            cookie_secure=cookie_secure,
            login_simples_habilitado=login_simples,
            origens_permitidas=(FRONTEND,),
            cabecalho_ip_cliente=cabecalho_ip_cliente,
        ),
        relogio=mundo.relogio,
    )
    return mundo
