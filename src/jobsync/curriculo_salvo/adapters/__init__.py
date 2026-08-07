"""Adapters concretos do domínio Currículo Salvo."""

from jobsync.curriculo_salvo.adapters.curriculo_salvo_repository_fake import CurriculoSalvoRepositoryFake
from jobsync.curriculo_salvo.adapters.curriculo_salvo_repository_impl import CurriculoSalvoRepositoryImpl

__all__ = ["CurriculoSalvoRepositoryFake", "CurriculoSalvoRepositoryImpl"]
