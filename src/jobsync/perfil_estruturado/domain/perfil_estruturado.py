"""Entidades de domínio do Perfil Estruturado ("currículo mestre").

Permite ao usuário preencher os dados do próprio currículo em campos
estruturados (como já faz no LinkedIn/Gupy), em vez de depender de upload de
PDF + extração por IA a cada ação. `DadosPerfilExtraidos` tem a mesma forma
de `PerfilEstruturado`, mas sem `perfil_identificador` — é o "rascunho"
devolvido pela extração de um PDF, antes de ser associado a um login e salvo.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum, auto

from jobsync.perfil_estruturado.domain.blocos_experiencia import chave_de_tecnologia
from jobsync.perfil_estruturado.domain.conquistas_parecidas import sao_parecidas
from jobsync.perfil_estruturado.domain.exceptions import ExperienciaNaoEncontrada
from jobsync.shared_kernel.domain.texto_normalizado import normalizar_texto


class NivelIdioma(Enum):
    """Nível de proficiência em um idioma."""

    BASICO = auto()
    INTERMEDIARIO = auto()
    AVANCADO = auto()
    FLUENTE = auto()
    NATIVO = auto()


class OrigemConquista(Enum):
    """De onde veio uma conquista guardada no banco de conquistas."""

    MANUAL = auto()
    RESPOSTA_PERGUNTA = auto()


@dataclass(frozen=True)
class Conquista:
    """Uma conquista da experiência, escrita ou aprovada pelo usuário."""

    texto: str
    origem: OrigemConquista = OrigemConquista.MANUAL

    def __post_init__(self) -> None:
        if not self.texto or not self.texto.strip():
            raise ValueError("O texto da conquista não pode ser vazio.")
        object.__setattr__(self, "texto", self.texto.strip())


def _itens_preenchidos(itens: tuple[str, ...], nome: str) -> tuple[str, ...]:
    if not all(item and item.strip() for item in itens):
        raise ValueError(f"Cada {nome} da experiência precisa de texto.")
    return tuple(item.strip() for item in itens)


@dataclass(frozen=True)
class ExperienciaProfissional:
    """Uma experiência profissional do perfil.

    `periodo` é texto livre (ex: "Jan 2020 - Dez 2022", "2023 - Atual") em vez
    de datas estritas — simplifica a UX, já que o usuário raramente sabe o
    dia exato de início/fim de uma experiência.

    `conquistas` é o banco de conquistas da experiência (JOB-0042); a lista vazia
    mantém o comportamento anterior, a partir da `descricao`.

    Os quatro blocos da experiência (JOB-0045) são `contexto`, `responsabilidades`,
    `conquistas` (as "principais realizações") e `skills`. A `descricao` em texto livre é
    legada: serve de fonte da migração para os blocos. Os limites de itens por bloco valem
    para a geração pela IA, não são invariante: o usuário edita livremente.
    """

    empresa: str
    cargo: str
    periodo: str
    descricao: str
    conquistas: tuple[Conquista, ...] = ()
    contexto: str = ""
    responsabilidades: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.empresa or not self.empresa.strip():
            raise ValueError("A empresa da experiência profissional não pode ser vazia.")
        if not self.cargo or not self.cargo.strip():
            raise ValueError("O cargo da experiência profissional não pode ser vazio.")
        textos = [normalizar_texto(conquista.texto) for conquista in self.conquistas]
        if len(set(textos)) != len(textos):
            raise ValueError("A experiência não pode ter conquistas duplicadas.")
        object.__setattr__(self, "contexto", self.contexto.strip())
        object.__setattr__(
            self, "responsabilidades", _itens_preenchidos(self.responsabilidades, "responsabilidade")
        )
        skills = _itens_preenchidos(self.skills, "skill")
        if len({chave_de_tecnologia(skill) for skill in skills}) != len(skills):
            raise ValueError("A experiência não pode ter skills duplicadas.")
        object.__setattr__(self, "skills", skills)

    @property
    def eh_legada(self) -> bool:
        """Tem descrição em texto livre e nenhum dos quatro blocos: precisa migrar para os blocos."""
        return bool(self.descricao.strip()) and not (
            self.contexto or self.responsabilidades or self.conquistas or self.skills
        )

    def conquistas_parecidas_com(self, texto: str) -> tuple[Conquista, ...]:
        """Conquistas já guardadas que dizem praticamente o mesmo que o texto informado."""
        return tuple(conquista for conquista in self.conquistas if sao_parecidas(conquista.texto, texto))


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

    def com_conquista_na_experiencia(self, indice: int, conquista: Conquista) -> PerfilEstruturado:
        """Perfil novo com a conquista no fim do banco da experiência; o resto não muda."""
        if not 0 <= indice < len(self.experiencias):
            raise ExperienciaNaoEncontrada()
        experiencia = self.experiencias[indice]
        atualizada = replace(experiencia, conquistas=(*experiencia.conquistas, conquista))
        experiencias = (*self.experiencias[:indice], atualizada, *self.experiencias[indice + 1 :])
        return replace(self, experiencias=experiencias)

    def tecnologias_ausentes(self) -> tuple[str, ...]:
        """Skills das experiências que ainda não constam nas tecnologias gerais, sem repetição."""
        conhecidas = {chave_de_tecnologia(tecnologia) for tecnologia in self.tecnologias}
        ausentes: list[str] = []
        for experiencia in self.experiencias:
            for skill in experiencia.skills:
                chave = chave_de_tecnologia(skill)
                if chave not in conhecidas:
                    conhecidas.add(chave)
                    ausentes.append(skill)
        return tuple(ausentes)

    def com_tecnologias_das_experiencias(self) -> PerfilEstruturado:
        """Perfil novo com as skills ausentes incluídas no fim das tecnologias gerais; nada é removido."""
        ausentes = self.tecnologias_ausentes()
        if not ausentes:
            return self
        return replace(self, tecnologias=(*self.tecnologias, *ausentes))
