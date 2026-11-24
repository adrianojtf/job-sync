"""DTO de input para o caso de uso SalvarPerfilEstruturado."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.perfil_estruturado.domain.perfil_estruturado import (
    Certificacao,
    ExperienciaProfissional,
    FormacaoAcademica,
    Idioma,
    PerfilEstruturado,
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


@dataclass(frozen=True)
class SalvarPerfilEstruturadoOutputDto:
    """Perfil salvo e as tecnologias que as skills das experiências acrescentaram às gerais."""

    perfil: PerfilEstruturado
    tecnologias_incluidas: tuple[str, ...]
