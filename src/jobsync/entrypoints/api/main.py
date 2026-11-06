"""Aplicação FastAPI do backend job-sync."""

from dotenv import load_dotenv
from fastapi import FastAPI, status

load_dotenv()
from jobsync.entrypoints.api.cors import configurar_cors, obter_origens_cors
from jobsync.entrypoints.api.exceptions import adicionar_handlers_excecao
from jobsync.entrypoints.api.routers import (
    candidatura_router,
    curriculo_router,
    health,
    perfil_estruturado_router,
    perfil_router,
    token_captura_router,
    vaga_externa_router,
    vaga_router,
)

app = FastAPI(
    title="Job Sync API",
    version="1.0.0",
    description="API do hexágono de domínio do job-sync",
)

configurar_cors(app, obter_origens_cors())

adicionar_handlers_excecao(app)


@app.get("/health", status_code=status.HTTP_200_OK, summary="Health check")
def root_health_check() -> dict:
    """Endpoint de health check sem versionamento para deploy/orquestradores."""
    return health.health_check()


app.include_router(health.router, prefix="/v1")
app.include_router(curriculo_router.router, prefix="/v1")
app.include_router(vaga_router.router, prefix="/v1")
app.include_router(vaga_externa_router.router, prefix="/v1")
app.include_router(candidatura_router.router, prefix="/v1")
app.include_router(perfil_router.router, prefix="/v1")
app.include_router(perfil_estruturado_router.router, prefix="/v1")
app.include_router(token_captura_router.router, prefix="/v1")
