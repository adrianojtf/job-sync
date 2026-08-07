"""Dependências FastAPI (Depends) para repositórios e services."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from jobsync.entrypoints.dependencies import (
    obter_caminho_banco,
    obter_repositorio_candidatura,
    obter_repositorio_curriculo_salvo,
    obter_repositorio_perfil,
    obter_repositorio_perfil_estruturado,
    obter_repositorio_token,
    obter_repositorio_vaga,
)

CaminhoBancoDep = Annotated[str, Depends(obter_caminho_banco)]
RepositorioVagaDep = Annotated[object, Depends(obter_repositorio_vaga)]
RepositorioCandidaturaDep = Annotated[object, Depends(obter_repositorio_candidatura)]
RepositorioCurriculoSalvoDep = Annotated[object, Depends(obter_repositorio_curriculo_salvo)]
RepositorioPerfilDep = Annotated[object, Depends(obter_repositorio_perfil)]
RepositorioPerfilEstruturadoDep = Annotated[
    object, Depends(obter_repositorio_perfil_estruturado)
]
RepositorioTokenDep = Annotated[object, Depends(obter_repositorio_token)]
