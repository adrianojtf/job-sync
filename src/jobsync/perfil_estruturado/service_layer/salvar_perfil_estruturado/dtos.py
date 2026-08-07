"""DTO de input para o caso de uso SalvarPerfilEstruturado."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.perfil_estruturado.domain.perfil_estruturado import (
    Certificacao,
    ExperienciaProfissional,
    FormacaoAcademica,
    Idioma,
)


@dataclass(frozen=True)
class SalvarPerfilEstruturadoInputDto:
    """Dados de entrada do caso de uso, vindos da interface (Streamlit)."""

    perfil_identificador: str
    nome_completo: str
    email: str
    linkedin: str
    resumo_profissional: str
    experiencias: tuple[ExperienciaProfissional, ...]
    formacoes: tuple[FormacaoAcademica, ...]
    certificacoes: tuple[Certificacao, ...]
    idiomas: tuple[Idioma, ...]
    tecnologias: tuple[str, ...]
