"""DTOs de input/output para o caso de uso AdaptarCurriculoParaVaga."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum

from jobsync.curriculo import (
    AvaliacaoExperiencia,
    Curriculo,
    ExperienciaParaAvaliacao,
    RascunhoCurriculoAdaptado,
)
from jobsync.vaga import AnaliseVaga, AvaliacaoDescricaoVaga


class StatusAvaliacaoAutomatica(str, Enum):
    AVALIADA = "avaliada"
    INDISPONIVEL = "indisponivel"


@dataclass(frozen=True)
class AvaliacaoExperienciaAdaptadaDto:
    experiencia: ExperienciaParaAvaliacao
    status: StatusAvaliacaoAutomatica
    avaliacao: AvaliacaoExperiencia | None


@dataclass(frozen=True)
class AdaptarCurriculoParaVagaInputDto:
    """Dados de entrada do caso de uso, vindos da interface (Streamlit).

    Informe `pdf_curriculo` OU `curriculo_pre_montado` — quando este último
    vier preenchido (perfil estruturado, Fase 5), a extração via IA é pulada.
    """

    descricao_vaga: str
    idioma_alvo: str
    cargo_alvo: str
    empresa_alvo: str
    pdf_curriculo: bytes | None = None
    curriculo_pre_montado: Curriculo | None = None
    data_referencia: date | None = None
    experiencias_profissionais: tuple[ExperienciaParaAvaliacao, ...] | None = None


@dataclass(frozen=True)
class AdaptarCurriculoParaVagaOutputDto:
    """Resultado do caso de uso: o rascunho adaptado, ainda sem PDF (JOB-0033).

    O PDF só é gerado após a revisão do usuário, por `GerarPdfCurriculoRevisado`.
    `curriculo_adaptado` é o rascunho já convertido, para consumidores que não
    passam pela revisão (ex.: carta de apresentação).
    Expõe `analise_vaga` (já calculada internamente) para que outras
    funcionalidades (ATS Score, carta de apresentação) possam reaproveitá-la
    sem uma segunda chamada de IA para analisar a mesma vaga.
    """

    rascunho: RascunhoCurriculoAdaptado
    curriculo_adaptado: Curriculo
    analise_vaga: AnaliseVaga
    avaliacao_vaga: AvaliacaoDescricaoVaga | None = None
    status_avaliacao_vaga: StatusAvaliacaoAutomatica | None = None
    avaliacoes_experiencias: tuple[AvaliacaoExperienciaAdaptadaDto, ...] = ()
