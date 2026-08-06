"""Adapters concretos do domínio Vaga."""

from jobsync.vaga.adapters.job_description_analyzer_client import JobDescriptionAnalyzerClient
from jobsync.vaga.adapters.vaga_repository_impl import VagaRepositoryImpl

__all__ = ["JobDescriptionAnalyzerClient", "VagaRepositoryImpl"]
