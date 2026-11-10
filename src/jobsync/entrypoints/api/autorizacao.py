"""Autorização por perfil: cada usuário só acessa os dados do próprio perfil.

`exigir_perfil_da_requisicao` roda em todo router de dados: exige sessão e confere o
`perfil_identificador` que o cliente enviar no caminho, na query ou no corpo JSON. Como é uma
dependência do router, uma rota nova já nasce protegida.
"""
from __future__ import annotations

import json
from typing import Any

from fastapi import Request

from jobsync.autenticacao.domain.exceptions import AcessoNegado
from jobsync.autenticacao.domain.usuario import Usuario
from jobsync.entrypoints.api.dependencies import UsuarioAutenticadoDep

_CAMPO_PERFIL = "perfil_identificador"
_METODOS_COM_CORPO = {"POST", "PUT", "PATCH"}


def exigir_acesso_ao_perfil(perfil_identificador: str, usuario: Usuario) -> None:
    if perfil_identificador != usuario.perfil_identificador:
        raise AcessoNegado("Você não tem acesso a este perfil.")


async def _perfil_no_corpo(request: Request) -> list[Any]:
    if request.method not in _METODOS_COM_CORPO:
        return []
    if "json" not in request.headers.get("content-type", ""):
        return []
    try:
        corpo = json.loads(await request.body())
    except ValueError:
        return []
    if isinstance(corpo, dict) and _CAMPO_PERFIL in corpo:
        return [corpo[_CAMPO_PERFIL]]
    return []


async def exigir_perfil_da_requisicao(request: Request, usuario: UsuarioAutenticadoDep) -> None:
    informados: list[Any] = []
    if _CAMPO_PERFIL in request.path_params:
        informados.append(request.path_params[_CAMPO_PERFIL])
    informados.extend(request.query_params.getlist(_CAMPO_PERFIL))
    informados.extend(await _perfil_no_corpo(request))
    for perfil in informados:
        exigir_acesso_ao_perfil(str(perfil), usuario)
