"""Agregado RascunhoCurriculoAdaptado: o currículo adaptado em revisão pelo usuário.

A adaptação via IA produz um rascunho em vez de um PDF. O usuário revisa e
edita livremente qualquer parte do rascunho; a confirmação é única e atômica,
e só então o rascunho é convertido no `Curriculo` usado para gerar o PDF.
As seções são partes do mesmo agregado, sem ciclo de vida próprio.

Quando a fonte é o perfil estruturado, as experiências ficam estruturadas
(`ExperienciaAdaptada`: cargo, empresa, período, conquistas e contexto); quando a fonte
é um PDF, elas ficam como uma seção de texto em `secoes`.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace

from jobsync.curriculo.domain.competencias import CATEGORIA_PADRAO, CategoriaCompetencia, categorias_para_texto
from jobsync.curriculo.domain.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from jobsync.curriculo.domain.equivalencia_tecnologia import AjusteTecnologia
from jobsync.curriculo.domain.experiencia_adaptada import ExperienciaAdaptada
from jobsync.curriculo.domain.rotulos_experiencia import rotulo_contexto

TITULO_EXPERIENCIAS_PADRAO = "Experiências"
TITULO_COMPETENCIAS_PADRAO = "Competências"

ExperienciaEditada = tuple[str, str, str, Iterable[str], str, Iterable[str], Iterable[str]]
"""Experiência como o usuário a editou: cargo, empresa, período, conquistas, contexto, responsabilidades e skills."""

CategoriaEditada = tuple[str, Iterable[str]]
"""Categoria de competências como o usuário a editou: nome e tags."""


def _preenchido(valor: str) -> bool:
    return bool(valor and valor.strip())


@dataclass(frozen=True)
class RascunhoCurriculoAdaptado:
    """Agregado raiz do currículo adaptado em revisão."""

    nome_completo: str
    email: str
    linkedin: str
    secoes: tuple[SecaoCurriculo, ...]
    experiencias: tuple[ExperienciaAdaptada, ...] | None = None
    titulo_experiencias: str = TITULO_EXPERIENCIAS_PADRAO
    competencias: tuple[CategoriaCompetencia, ...] | None = None
    """Competências por categoria e tag; exclusivas com a seção de texto de tecnologias."""
    titulo_competencias: str = TITULO_COMPETENCIAS_PADRAO
    lacunas_tecnologia: tuple[str, ...] = ()
    """Tecnologias da vaga sem evidência no perfil, que não entraram em Competências (JOB-0044)."""
    ajustes_tecnologia: tuple[AjusteTecnologia, ...] = ()
    """Trocas de tecnologia que a IA fez nas experiências, para o usuário conferir na revisão."""

    def __post_init__(self) -> None:
        if not _preenchido(self.nome_completo):
            raise ValueError("O nome completo do candidato é obrigatório.")
        if not self.secoes and not self.experiencias and not self.competencias:
            raise ValueError("O currículo precisa de ao menos uma seção com conteúdo.")
        if self.experiencias is not None and any(
            secao.tipo == TipoSecao.EXPERIENCIAS for secao in self.secoes
        ):
            raise ValueError(
                "As experiências devem vir estruturadas ou como seção de texto, não ambos."
            )
        if self.competencias is not None and any(
            secao.tipo == TipoSecao.TECNOLOGIAS for secao in self.secoes
        ):
            raise ValueError(
                "As competências devem vir por categoria ou como seção de texto, não ambas."
            )
        quantidade_experiencias = len(self.experiencias or ())
        if any(
            not 0 <= ajuste.indice_experiencia < quantidade_experiencias
            for ajuste in self.ajustes_tecnologia
        ):
            raise ValueError("Cada ajuste de tecnologia precisa apontar uma experiência estruturada.")

    @classmethod
    def revisado(
        cls,
        nome_completo: str,
        email: str,
        linkedin: str,
        secoes: Iterable[tuple[TipoSecao, str, str]],
        experiencias: Iterable[ExperienciaEditada] | None,
        titulo_experiencias: str = TITULO_EXPERIENCIAS_PADRAO,
        competencias: Iterable[CategoriaEditada] | None = None,
        titulo_competencias: str = TITULO_COMPETENCIAS_PADRAO,
    ) -> RascunhoCurriculoAdaptado:
        """Monta o rascunho editado pelo usuário, descartando trechos deixados em branco."""
        return cls(
            nome_completo=nome_completo,
            email=email,
            linkedin=linkedin,
            secoes=tuple(
                SecaoCurriculo(tipo=tipo, titulo=titulo, conteudo=conteudo)
                for tipo, titulo, conteudo in secoes
                if _preenchido(conteudo)
            ),
            experiencias=(
                None
                if experiencias is None
                else tuple(
                    experiencia
                    for editada in experiencias
                    if (experiencia := ExperienciaAdaptada.revisada(*editada)) is not None
                )
            ),
            titulo_experiencias=titulo_experiencias,
            competencias=(
                None
                if competencias is None
                else tuple(
                    categoria
                    for nome, tags in competencias
                    if (categoria := CategoriaCompetencia.revisada(nome, tags)) is not None
                )
            ),
            titulo_competencias=titulo_competencias,
        )

    def com_skills_nas_competencias(self) -> RascunhoCurriculoAdaptado:
        """Rascunho novo com as skills das experiências que faltam nas competências, em "Tecnologias".

        A comparação ignora a caixa e a categoria. Sem competências por categoria, nada muda.
        """
        if self.competencias is None:
            return self
        conhecidas = {
            tag.strip().casefold() for categoria in self.competencias for tag in categoria.tags
        }
        ausentes: list[str] = []
        for experiencia in self.experiencias or ():
            for skill in experiencia.skills:
                if skill.strip().casefold() not in conhecidas:
                    conhecidas.add(skill.strip().casefold())
                    ausentes.append(skill)
        if not ausentes:
            return self
        padrao = next((c for c in self.competencias if c.nome == CATEGORIA_PADRAO), None)
        if padrao is None:
            categorias = (*self.competencias, CategoriaCompetencia(CATEGORIA_PADRAO, tuple(ausentes)))
        else:
            ampliada = CategoriaCompetencia(CATEGORIA_PADRAO, (*padrao.tags, *ausentes))
            categorias = tuple(ampliada if c is padrao else c for c in self.competencias)
        return replace(self, competencias=categorias)

    def para_curriculo(self, idioma_alvo: str) -> Curriculo:
        """Converte o rascunho no Curriculo consumido pela geração de PDF.

        O idioma alvo define os rótulos dos blocos de cada experiência; um idioma não suportado
        levanta ValueError, mesmo sem experiências estruturadas.
        """
        rotulo_contexto(idioma_alvo)
        secoes = self.secoes
        if self.experiencias:
            secoes = secoes + (
                SecaoCurriculo(
                    tipo=TipoSecao.EXPERIENCIAS,
                    titulo=self.titulo_experiencias,
                    conteudo="\n\n".join(
                        experiencia.para_texto(idioma_alvo) for experiencia in self.experiencias
                    ),
                ),
            )
        if self.competencias:
            secoes = secoes + (
                SecaoCurriculo(
                    tipo=TipoSecao.TECNOLOGIAS,
                    titulo=self.titulo_competencias,
                    conteudo=categorias_para_texto(self.competencias),
                ),
            )
        return Curriculo(
            nome_completo=self.nome_completo,
            email=self.email,
            linkedin=self.linkedin,
            secoes=secoes,
        )
