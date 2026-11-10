import json
import os
from types import SimpleNamespace

import pytest
from fastapi import Request

from jobsync.entrypoints.api.dependencies import obter_usuario_autenticado
from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.dependencies import fechar_pool_conexoes


@pytest.fixture(autouse=True)
def banco_de_teste_da_api(monkeypatch):
    url = os.getenv("TEST_DATABASE_URL")
    if url:
        monkeypatch.setenv("DATABASE_URL", url)
    yield
    fechar_pool_conexoes()


def _usuario_simulado(perfil: str) -> SimpleNamespace:
    return SimpleNamespace(perfil_identificador=perfil)


async def _usuario_do_perfil_pedido(request: Request) -> SimpleNamespace:
    """Sessão simulada para os testes dos routers de dados: o usuário é dono do perfil pedido.

    Os testes de autenticação e de autorização (marcados com `sem_sessao_simulada`) usam a
    sessão real e conferem 401 e 403.
    """
    perfil = request.path_params.get("perfil_identificador") or request.query_params.get("perfil_identificador")
    if perfil is None and request.method in {"POST", "PUT", "PATCH"}:
        try:
            corpo = json.loads(await request.body())
        except ValueError:
            corpo = None
        if isinstance(corpo, dict):
            perfil = corpo.get("perfil_identificador")
    return _usuario_simulado(str(perfil) if perfil is not None else "perfil-de-teste")


@pytest.fixture(autouse=True)
def sessao_simulada(request):
    if request.node.get_closest_marker("sem_sessao_simulada"):
        yield
        return
    app.dependency_overrides[obter_usuario_autenticado] = _usuario_do_perfil_pedido
    yield
    app.dependency_overrides.pop(obter_usuario_autenticado, None)


@pytest.fixture
def como_perfil():
    """Define de qual perfil é a sessão simulada, para rotas que identificam o dono pelo recurso."""

    def definir(perfil: str) -> None:
        app.dependency_overrides[obter_usuario_autenticado] = lambda: _usuario_simulado(perfil)

    return definir
