"""Servidor HTTP local (FastAPI) que recebe a captura de vagas da extensão de navegador.

Roda em processo separado do Streamlit (porta padrão 8502), pois o Streamlit
não expõe uma API HTTP própria para receber chamadas externas. Único
endpoint exposto: POST /api/vagas/capturar, autenticado por um token opaco
(TokenCaptura) gerado pelo usuário dentro do Streamlit.
"""
from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from jobsync.entrypoints.dependencies import (
    fechar_pool_conexoes,
    preparar_banco,
    obter_repositorio_token,
    obter_repositorio_vaga,
)
from jobsync.token_captura.adapters import TokenCapturaRepositoryImpl
from jobsync.vaga.adapters import VagaRepositoryImpl
from jobsync.vaga.service_layer.capturar_vaga import CapturarVaga, CapturarVagaInputDto

@asynccontextmanager
async def _ciclo_de_vida(_: FastAPI):
    preparar_banco()
    yield
    fechar_pool_conexoes()


app = FastAPI(title="job-sync - Servidor de Captura", lifespan=_ciclo_de_vida)


class CapturaVagaRequest(BaseModel):
    texto: str = Field(min_length=1)
    url: Optional[str] = None


class CapturaVagaResponse(BaseModel):
    id: str


def _extrair_token(authorization: str) -> str:
    prefixo = "Bearer "
    if not authorization.startswith(prefixo):
        raise HTTPException(status_code=401, detail="Cabeçalho Authorization inválido.")
    return authorization[len(prefixo):].strip()


@app.post("/api/vagas/capturar", status_code=201, response_model=CapturaVagaResponse)
def capturar_vaga(
    payload: CapturaVagaRequest,
    authorization: str = Header(...),
    repositorio_token: TokenCapturaRepositoryImpl = Depends(obter_repositorio_token),
    repositorio_vaga: VagaRepositoryImpl = Depends(obter_repositorio_vaga),
) -> CapturaVagaResponse:
    token = _extrair_token(authorization)
    perfil_identificador = repositorio_token.resolver_perfil_por_token(token)
    if perfil_identificador is None:
        raise HTTPException(status_code=401, detail="Token de captura inválido.")

    use_case = CapturarVaga(repositorio_vaga)
    vaga = use_case.executar(
        CapturarVagaInputDto(
            perfil_identificador=perfil_identificador,
            texto_descricao=payload.texto,
            url_origem=payload.url,
        )
    )
    return CapturaVagaResponse(id=vaga.id)
