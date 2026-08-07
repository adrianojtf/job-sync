"""Schemas Pydantic de request/response da API v1."""

from jobsync.entrypoints.api.schemas.candidatura import (
    CandidaturaCriarRequest,
    CandidaturaResponse,
    CandidaturasListagemResponse,
    CandidaturaSubmeterRequest,
)
from jobsync.entrypoints.api.schemas.curriculo import (
    AdaptarCurriculoRequest,
    AdaptarCurriculoResponse,
    AnalisarAtsRequest,
    AnalisarAtsResponse,
    CurriculoSalvarRequest,
    CurriculoSalvoResponse,
)
from jobsync.entrypoints.api.schemas.perfil import (
    PerfisListagemResponse,
    PerfilResponse,
)
from jobsync.entrypoints.api.schemas.vaga import (
    VagaCapturarRequest,
    VagaResponse,
    VagasListagemResponse,
)
from jobsync.entrypoints.api.schemas.vaga_externa import (
    DescobrirVagasRequest,
    DescobrirVagasResponse,
    VagaDescobertaResponse,
)

__all__ = [
    "AdaptarCurriculoRequest",
    "AdaptarCurriculoResponse",
    "AnalisarAtsRequest",
    "AnalisarAtsResponse",
    "CandidaturaCriarRequest",
    "CandidaturaResponse",
    "CandidaturasListagemResponse",
    "CandidaturaSubmeterRequest",
    "CurriculoSalvarRequest",
    "CurriculoSalvoResponse",
    "DescobrirVagasRequest",
    "DescobrirVagasResponse",
    "PerfisListagemResponse",
    "PerfilResponse",
    "VagaCapturarRequest",
    "VagaDescobertaResponse",
    "VagaResponse",
    "VagasListagemResponse",
]
