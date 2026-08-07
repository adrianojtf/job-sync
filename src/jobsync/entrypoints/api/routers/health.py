"""Router de health check para o backend FastAPI."""

from fastapi import APIRouter, status

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK, summary="Health check")
def health_check() -> dict:
    """Retorna o status de saúde da API."""
    return {"status": "ok"}
