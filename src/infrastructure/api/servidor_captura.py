"""Servidor HTTP local (FastAPI) que recebe a captura de vagas da extensão de navegador.

Roda em processo separado do Streamlit (porta padrão 8502), pois o Streamlit
não expõe uma API HTTP própria para receber chamadas externas. Único
endpoint exposto: POST /api/vagas/capturar, autenticado por um token opaco
(TokenCaptura) gerado pelo usuário dentro do Streamlit.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from application.use_cases.capturar_vaga import CapturarVaga, CapturarVagaInputDto
from infrastructure.persistence.token_captura_repository_impl import TokenCapturaRepositoryImpl
from infrastructure.persistence.vaga_repository_impl import VagaRepositoryImpl

_DIRETORIO_ARMAZENAMENTO = Path(__file__).resolve().parent.parent.parent.parent / "storage"
_CAMINHO_BANCO_PADRAO = str(_DIRETORIO_ARMAZENAMENTO / "job_sync.db")

app = FastAPI(title="job-sync - Servidor de Captura")


class CapturaVagaRequest(BaseModel):
    texto: str = Field(min_length=1)
    url: Optional[str] = None


class CapturaVagaResponse(BaseModel):
    id: str


def obter_caminho_banco() -> str:
    """Permite apontar para um banco alternativo (ex: testes) via variável de ambiente."""
    return os.getenv("JOB_SYNC_DB_PATH", _CAMINHO_BANCO_PADRAO)


def obter_repositorio_token() -> TokenCapturaRepositoryImpl:
    return TokenCapturaRepositoryImpl(caminho_banco=obter_caminho_banco())


def obter_repositorio_vaga() -> VagaRepositoryImpl:
    return VagaRepositoryImpl(caminho_banco=obter_caminho_banco())


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

    use_case = CapturarVaga(repositorio_vaga=repositorio_vaga)
    vaga = use_case.executar(
        CapturarVagaInputDto(
            perfil_identificador=perfil_identificador,
            texto_descricao=payload.texto,
            url_origem=payload.url,
        )
    )
    return CapturaVagaResponse(id=vaga.id)
