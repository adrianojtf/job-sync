"""Agregado RascunhoCurriculoAdaptado: o currículo adaptado em revisão pelo usuário.

A adaptação via IA produz um rascunho em vez de um PDF. O usuário revisa e
edita livremente qualquer parte do rascunho; a confirmação é única e atômica,
e só então o rascunho é convertido no `Curriculo` usado para gerar o PDF.
As seções são partes do mesmo agregado, sem ciclo de vida próprio.

Quando a fonte é o perfil estruturado, as experiências ficam estruturadas
(cargo, empresa, período, descrição); quando a fonte é um PDF, elas ficam
como uma seção de texto em `secoes`.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.curriculo import Curriculo, SecaoCurriculo, TipoSecao

TITULO_EXPERIENCIAS_PADRAO = "Experiências"


def _preenchido(valor: str) -> bool:
    return bool(valor and valor.strip())


@dataclass(frozen=True)
class RascunhoCurriculoAdaptado:
    """Agregado raiz do currículo adaptado em revisão."""

    nome_completo: str
    email: str
    linkedin: str
    secoes: tuple[SecaoCurriculo, ...]
    experiencias: tuple[ExperienciaParaAvaliacao, ...] | None = None
    titulo_experiencias: str = TITULO_EXPERIENCIAS_PADRAO

    def __post_init__(self) -> None:
        if not _preenchido(self.nome_completo):
            raise ValueError("O nome completo do candidato é obrigatório.")
        if not self.secoes and not self.experiencias:
            raise ValueError("O currículo precisa de ao menos uma seção com conteúdo.")
        if self.experiencias is not None:
            self._validar_experiencias_estruturadas()

    def _validar_experiencias_estruturadas(self) -> None:
        if any(secao.tipo == TipoSecao.EXPERIENCIAS for secao in self.secoes):
            raise ValueError(
                "As experiências devem vir estruturadas ou como seção de texto, não ambos."
            )
        for experiencia in self.experiencias or ():
            if not _preenchido(experiencia.cargo):
                raise ValueError("Informe o cargo de cada experiência profissional.")
            if not _preenchido(experiencia.empresa):
                raise ValueError("Informe a empresa de cada experiência profissional.")

    @classmethod
    def revisado(
        cls,
        nome_completo: str,
        email: str,
        linkedin: str,
        secoes: Iterable[tuple[TipoSecao, str, str]],
        experiencias: Iterable[ExperienciaParaAvaliacao] | None,
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
                    for experiencia in experiencias
                    if any(
                        _preenchido(valor)
                        for valor in (
                            experiencia.cargo,
                            experiencia.empresa,
                            experiencia.periodo,
                            experiencia.descricao,
                        )
                    )
                )
            ),
            titulo_experiencias=titulo_experiencias,
        )

    def para_curriculo(self) -> Curriculo:
        """Converte o rascunho no Curriculo consumido pela geração de PDF."""
        secoes = self.secoes
        if self.experiencias:
            secoes = secoes + (self._montar_secao_experiencias(),)
        return Curriculo(
            nome_completo=self.nome_completo,
            email=self.email,
            linkedin=self.linkedin,
            secoes=secoes,
        )

    def _montar_secao_experiencias(self) -> SecaoCurriculo:
        blocos = []
        for experiencia in self.experiencias or ():
            conteudo = "\n".join(
                parte
                for parte in (
                    self._identificar(experiencia),
                    experiencia.descricao.strip(),
                )
                if parte
            )
            if conteudo:
                blocos.append(conteudo)
        return SecaoCurriculo(
            tipo=TipoSecao.EXPERIENCIAS,
            titulo=self.titulo_experiencias,
            conteudo="\n\n".join(blocos),
        )

    @staticmethod
    def _identificar(experiencia: ExperienciaParaAvaliacao) -> str:
        identificacao = " — ".join(
            valor.strip()
            for valor in (experiencia.cargo, experiencia.empresa)
            if _preenchido(valor)
        )
        if not _preenchido(experiencia.periodo):
            return identificacao
        periodo = experiencia.periodo.strip()
        return f"{identificacao} ({periodo})" if identificacao else periodo
