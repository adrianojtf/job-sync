"""DTOs de input/output para o caso de uso AdaptarCurriculoParaVaga."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from domain.curriculo import Curriculo
from jobsync.shared_kernel.domain import NomeArquivo
from domain.vaga import AnaliseVaga


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


@dataclass(frozen=True)
class AdaptarCurriculoParaVagaOutputDto:
    """Resultado do caso de uso: PDF gerado e nome de arquivo padronizado.

    Expõe `analise_vaga` (já calculada internamente) para que outras
    funcionalidades (ATS Score, carta de apresentação) possam reaproveitá-la
    sem uma segunda chamada de IA para analisar a mesma vaga.
    """

    pdf_bytes: bytes
    nome_arquivo: NomeArquivo
    curriculo_adaptado: Curriculo
    analise_vaga: AnaliseVaga
