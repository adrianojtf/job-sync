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
from dataclasses import dataclass

from jobsync.curriculo.domain.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from jobsync.curriculo.domain.equivalencia_tecnologia import AjusteTecnologia
from jobsync.curriculo.domain.experiencia_adaptada import ExperienciaAdaptada
from jobsync.curriculo.domain.rotulos_experiencia import rotulo_contexto

TITULO_EXPERIENCIAS_PADRAO = "Experiências"

ExperienciaEditada = tuple[str, str, str, Iterable[str], str]
"""Experiência como o usuário a editou: cargo, empresa, período, conquistas e contexto."""


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
    ajustes_tecnologia: tuple[AjusteTecnologia, ...] = ()
    """Trocas de tecnologia que a IA fez nas experiências, para o usuário conferir na revisão."""

    def __post_init__(self) -> None:
        if not _preenchido(self.nome_completo):
            raise ValueError("O nome completo do candidato é obrigatório.")
        if not self.secoes and not self.experiencias:
            raise ValueError("O currículo precisa de ao menos uma seção com conteúdo.")
        if self.experiencias is not None and any(
            secao.tipo == TipoSecao.EXPERIENCIAS for secao in self.secoes
        ):
            raise ValueError(
                "As experiências devem vir estruturadas ou como seção de texto, não ambos."
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
        )

    def para_curriculo(self, idioma_alvo: str) -> Curriculo:
        """Converte o rascunho no Curriculo consumido pela geração de PDF.

        O idioma alvo define o rótulo da linha de contexto de cada experiência.
        """
        rotulo = rotulo_contexto(idioma_alvo)
        secoes = self.secoes
        if self.experiencias:
            secoes = secoes + (
                SecaoCurriculo(
                    tipo=TipoSecao.EXPERIENCIAS,
                    titulo=self.titulo_experiencias,
                    conteudo="\n\n".join(
                        experiencia.para_texto(rotulo) for experiencia in self.experiencias
                    ),
                ),
            )
        return Curriculo(
            nome_completo=self.nome_completo,
            email=self.email,
            linkedin=self.linkedin,
            secoes=secoes,
        )
