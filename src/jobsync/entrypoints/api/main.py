"""Aplicação FastAPI do backend job-sync."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jobsync.entrypoints.api.exceptions import adicionar_handlers_excecao
from jobsync.entrypoints.api.routers import (
    candidatura_router,
    curriculo_router,
    health,
    perfil_router,
    vaga_externa_router,
    vaga_router,
)

app = FastAPI(
    title="Job Sync API",
    version="1.0.0",
    description="API do hexágono de domínio do job-sync",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

adicionar_handlers_excecao(app)

app.include_router(health.router, prefix="/v1")
app.include_router(curriculo_router.router, prefix="/v1")
app.include_router(vaga_router.router, prefix="/v1")
app.include_router(vaga_externa_router.router, prefix="/v1")
app.include_router(candidatura_router.router, prefix="/v1")
app.include_router(perfil_router.router, prefix="/v1")
