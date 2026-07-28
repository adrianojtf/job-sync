"""Entidades de domínio do Perfil Estruturado ("currículo mestre").

Permite ao usuário preencher os dados do próprio currículo em campos
estruturados (como já faz no LinkedIn/Gupy), em vez de depender de upload de
PDF + extração por IA a cada ação. `DadosPerfilExtraidos` tem a mesma forma
de `PerfilEstruturado`, mas sem `perfil_identificador` — é o "rascunho"
devolvido pela extração de um PDF, antes de ser associado a um login e salvo.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class NivelIdioma(Enum):
    """Nível de proficiência em um idioma."""

    BASICO = auto()
    INTERMEDIARIO = auto()
    AVANCADO = auto()
    FLUENTE = auto()
    NATIVO = auto()


@dataclass(frozen=True)
class ExperienciaProfissional:
    """Uma experiência profissional do perfil.

    `periodo` é texto livre (ex: "Jan 2020 - Dez 2022", "2023 - Atual") em vez
    de datas estritas — simplifica a UX, já que o usuário raramente sabe o
    dia exato de início/fim de uma experiência.
    """

    empresa: str
    cargo: str
    periodo: str
    descricao: str

    def __post_init__(self) -> None:
        if not self.empresa or not self.empresa.strip():
            raise ValueError("A empresa da experiência profissional não pode ser vazia.")
        if not self.cargo or not self.cargo.strip():
            raise ValueError("O cargo da experiência profissional não pode ser vazio.")


@dataclass(frozen=True)
class FormacaoAcademica:
    """Uma formação acadêmica do perfil."""

    instituicao: str
    curso: str
    periodo: str

    def __post_init__(self) -> None:
        if not self.instituicao or not self.instituicao.strip():
            raise ValueError("A instituição da formação acadêmica não pode ser vazia.")
        if not self.curso or not self.curso.strip():
            raise ValueError("O curso da formação acadêmica não pode ser vazio.")


@dataclass(frozen=True)
class Certificacao:
    """Uma certificação do perfil."""

    nome: str
    instituicao: str
    ano: str

    def __post_init__(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("O nome da certificação não pode ser vazio.")


@dataclass(frozen=True)
class Idioma:
    """Um idioma do perfil, com o nível de proficiência."""

    idioma: str
    nivel: NivelIdioma

    def __post_init__(self) -> None:
        if not self.idioma or not self.idioma.strip():
            raise ValueError("O nome do idioma não pode ser vazio.")


@dataclass(frozen=True)
class DadosPerfilExtraidos:
    """Rascunho de perfil extraído de um PDF via IA, antes de revisão e salvamento.

    Mesma forma de `PerfilEstruturado`, mas sem `perfil_identificador` — ainda
    não está associado a um login, e não é persistido diretamente.
    """

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
class PerfilEstruturado:
    """Agregado raiz: o currículo mestre estruturado de um perfil de login."""

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

    def __post_init__(self) -> None:
        if not self.perfil_identificador or not self.perfil_identificador.strip():
            raise ValueError("O identificador do perfil não pode ser vazio.")
        if not self.nome_completo or not self.nome_completo.strip():
            raise ValueError("O nome completo do perfil não pode ser vazio.")
        if not self.email or not self.email.strip():
            raise ValueError("O email do perfil não pode ser vazio.")
