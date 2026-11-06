"""Schemas Pydantic de request/response da API v1."""

from jobsync.entrypoints.api.schemas.candidatura import (
    CandidaturaCriarRequest,
    CandidaturaResponse,
    CandidaturasListagemResponse,
    CandidaturaSubmeterRequest,
)
from jobsync.entrypoints.api.schemas.erro import ProblemaResponse
from jobsync.entrypoints.api.schemas.curriculo import (
    AdaptarCurriculoRequest,
    AdaptarCurriculoResponse,
    AvaliacaoExperienciaResponse,
    AvaliarExperienciaRequest,
    AnalisarAtsRequest,
    AnalisarAtsResponse,
    CurriculoSalvarRequest,
    CurriculoSalvoResponse,
    ExperienciaParaAvaliacaoRequest,
)
from jobsync.entrypoints.api.schemas.perfil import (
    PerfisListagemResponse,
    PerfilResponse,
)
from jobsync.entrypoints.api.schemas.token_captura import (
    TokenCapturaCriarRequest,
    TokenCapturaResponse,
)
from jobsync.entrypoints.api.schemas.vaga import (
    AvaliacaoDescricaoVagaResponse,
    AvaliarDescricaoVagaRequest,
    VagaCapturarRequest,
    VagaResponse,
    VagasListagemResponse,
)
from jobsync.entrypoints.api.schemas.vaga_externa import (
    CandidatarVagaExternaRequest,
    CandidatarVagaExternaResponse,
    DescobrirVagasRequest,
    DescobrirVagasResponse,
    VagaDescobertaResponse,
)

__all__ = [
    "AdaptarCurriculoRequest",
    "AdaptarCurriculoResponse",
    "AnalisarAtsRequest",
    "AnalisarAtsResponse",
    "AvaliacaoDescricaoVagaResponse",
    "AvaliacaoExperienciaResponse",
    "AvaliarDescricaoVagaRequest",
    "AvaliarExperienciaRequest",
    "CandidatarVagaExternaRequest",
    "CandidatarVagaExternaResponse",
    "CandidaturaCriarRequest",
    "CandidaturaResponse",
    "CandidaturasListagemResponse",
    "CandidaturaSubmeterRequest",
    "CurriculoSalvarRequest",
    "CurriculoSalvoResponse",
    "DescobrirVagasRequest",
    "DescobrirVagasResponse",
    "ExperienciaParaAvaliacaoRequest",
    "PerfisListagemResponse",
    "PerfilResponse",
    "ProblemaResponse",
    "TokenCapturaCriarRequest",
    "TokenCapturaResponse",
    "VagaCapturarRequest",
    "VagaDescobertaResponse",
    "VagaResponse",
    "VagasListagemResponse",
]
