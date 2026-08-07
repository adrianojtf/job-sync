"""Entidades de domínio do currículo.

Modelo baseado na estrutura observada no currículo de referência:
Cabeçalho (nome/contato) -> Tecnologias -> Perfil -> Experiências -> Formação acadêmica.

Cada seção é tratada como unidade independente de ajuste, permitindo que o
caso de uso "AdaptarCurriculoParaVaga" processe e reescreva uma seção por vez.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum, auto
from typing import Optional


class TipoSecao(Enum):
    """Tipos de seção reconhecidos no modelo de currículo.

    A ordem dos membros define a ordem de exibição no PDF final.
    """

    TECNOLOGIAS = auto()
    PERFIL = auto()
    EXPERIENCIAS = auto()
    FORMACAO = auto()
    CERTIFICACOES = auto()
    IDIOMAS = auto()


@dataclass(frozen=True)
class SecaoCurriculo:
    """Seção individual do currículo (ex.: Tecnologias, Perfil, Experiências).

    Imutável: qualquer ajuste de conteúdo (ex.: reescrita pela IA para uma
    vaga específica) produz uma nova instância via `com_novo_conteudo`.
    """

    tipo: TipoSecao
    titulo: str
    conteudo: str

    def __post_init__(self) -> None:
        if not self.conteudo or not self.conteudo.strip():
            raise ValueError(f"O conteúdo da seção '{self.titulo}' não pode ser vazio.")
        if not self.titulo or not self.titulo.strip():
            raise ValueError("O título da seção não pode ser vazio.")

    def com_novo_conteudo(self, novo_conteudo: str) -> "SecaoCurriculo":
        return replace(self, conteudo=novo_conteudo)


@dataclass(frozen=True)
class Curriculo:
    """Agregado raiz representando o currículo completo de um candidato."""

    nome_completo: str
    email: str
    linkedin: str
    secoes: tuple[SecaoCurriculo, ...]

    def __post_init__(self) -> None:
        if not self.nome_completo or not self.nome_completo.strip():
            raise ValueError("O nome completo do candidato é obrigatório.")

    def obter_secao(self, tipo: TipoSecao) -> Optional[SecaoCurriculo]:
        for secao in self.secoes:
            if secao.tipo == tipo:
                return secao
        return None

    def substituir_secao(self, nova_secao: SecaoCurriculo) -> "Curriculo":
        """Retorna um novo Curriculo com a seção substituída (ou adicionada, se não existir)."""
        secoes_sem_o_tipo = tuple(s for s in self.secoes if s.tipo != nova_secao.tipo)
        novas_secoes = secoes_sem_o_tipo + (nova_secao,)
        return replace(self, secoes=novas_secoes)
