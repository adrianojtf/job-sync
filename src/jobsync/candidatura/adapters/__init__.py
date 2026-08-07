"""Adapters concretos do domínio Candidatura."""

from jobsync.candidatura.adapters.candidatura_repository_fake import CandidaturaRepositoryFake
from jobsync.candidatura.adapters.candidatura_repository_impl import CandidaturaRepositoryImpl

__all__ = ["CandidaturaRepositoryFake", "CandidaturaRepositoryImpl"]
