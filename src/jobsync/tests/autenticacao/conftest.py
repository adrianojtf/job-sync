from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from jobsync.autenticacao.adapters import (
    EstadoOAuthRepositoryFake,
    EstadoOAuthRepositoryImpl,
    LimiteTentativasRepositoryFake,
    LimiteTentativasRepositoryImpl,
    SessaoRepositoryFake,
    SessaoRepositoryImpl,
    TokenUsoUnicoRepositoryFake,
    TokenUsoUnicoRepositoryImpl,
    UsuarioRepositoryFake,
    UsuarioRepositoryImpl,
)
from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.usuario import Usuario

AGORA = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(params=["fake", "postgres"])
def repositorios(request):
    if request.param == "fake":
        return SimpleNamespace(
            usuarios=UsuarioRepositoryFake(),
            sessoes=SessaoRepositoryFake(),
            tokens=TokenUsoUnicoRepositoryFake(),
            estados=EstadoOAuthRepositoryFake(),
            limites=LimiteTentativasRepositoryFake(),
        )
    pool = request.getfixturevalue("pool_postgres")
    return SimpleNamespace(
        usuarios=UsuarioRepositoryImpl(pool),
        sessoes=SessaoRepositoryImpl(pool),
        tokens=TokenUsoUnicoRepositoryImpl(pool),
        estados=EstadoOAuthRepositoryImpl(pool),
        limites=LimiteTentativasRepositoryImpl(pool),
    )


@pytest.fixture
def usuario(repositorios):
    novo = Usuario.novo(Email("ana@exemplo.com"), "u-aaaaaaaaaaaa", AGORA, nome="Ana")
    repositorios.usuarios.salvar_novo(novo)
    return novo


@pytest.fixture
def ambiente():
    from jobsync.autenticacao.domain.configuracao import ConfiguracaoAutenticacao
    from jobsync.tests.autenticacao.dobles import EnviadorEmailFalso, HasherSenhaFalso, RelogioFalso

    return SimpleNamespace(
        usuarios=UsuarioRepositoryFake(),
        sessoes=SessaoRepositoryFake(),
        tokens=TokenUsoUnicoRepositoryFake(),
        estados=EstadoOAuthRepositoryFake(),
        limites=LimiteTentativasRepositoryFake(),
        hasher=HasherSenhaFalso(),
        enviador=EnviadorEmailFalso(),
        relogio=RelogioFalso(),
        config=ConfiguracaoAutenticacao(),
    )
