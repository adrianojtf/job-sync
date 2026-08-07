"""Aplicação FastAPI do backend job-sync."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jobsync.entrypoints.api.exceptions import adicionar_handlers_excecao
from jobsync.entrypoints.api.routers import health

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
