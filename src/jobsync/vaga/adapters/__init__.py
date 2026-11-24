"""Adapters concretos do domínio Vaga."""

from jobsync.vaga.adapters.extrator_dados_vaga_ia_client import ExtratorDadosVagaIaClient
from jobsync.vaga.adapters.job_description_analyzer_client import JobDescriptionAnalyzerClient
from jobsync.vaga.adapters.leitor_vaga_generico_client import LeitorVagaGenericoClient
from jobsync.vaga.adapters.vaga_repository_fake import VagaRepositoryFake
from jobsync.vaga.adapters.vaga_repository_impl import VagaRepositoryImpl

__all__ = [
    "ExtratorDadosVagaIaClient",
    "JobDescriptionAnalyzerClient",
    "LeitorVagaGenericoClient",
    "VagaRepositoryFake",
    "VagaRepositoryImpl",
]
