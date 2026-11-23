"""Serviço de domínio: o que entra na seção Competências e o corte pelo teto (JOB-0044).

A decisão é do domínio, não da IA: entra o que o candidato tem (itens do perfil), o que as suas
experiências citam e as tecnologias equivalentes aplicadas (JOB-0037). A tecnologia ou ferramenta
da vaga sem evidência vira lacuna. Requisitos que não são tecnologia nem ferramenta (habilidades,
metodologias, domínios) nunca entram. A IA só agrupa e ordena o que é permitido.
"""
from __future__ import annotations

from collections.abc import Collection, Sequence
from dataclasses import dataclass

from jobsync.curriculo.domain.competencias import CategoriaCompetencia
from jobsync.curriculo.domain.equivalencia_tecnologia import EquivalenciaTecnologia, menciona_tecnologia
from jobsync.vaga import CategoriaRequisitoTecnico, RequisitoTecnico

TETO_DE_COMPETENCIAS = 45

_CATEGORIAS_CONSIDERADAS = (CategoriaRequisitoTecnico.TECNOLOGIA, CategoriaRequisitoTecnico.FERRAMENTA)


@dataclass(frozen=True)
class ResultadoDaSelecao:
    permitidos: tuple[str, ...]
    """Itens que podem aparecer em Competências, na ordem do candidato."""
    lacunas: tuple[str, ...]
    """Tecnologias e ferramentas da vaga sem evidência, na ordem em que a vaga as cita."""
    relevantes: tuple[str, ...] = ()
    """Os permitidos que a vaga pede; sobrevivem ao corte pelo teto."""


def _chave(texto: str) -> str:
    return texto.strip().casefold()


class SelecaoDeCompetencias:
    def selecionar(
        self,
        itens_do_candidato: Sequence[str],
        textos_das_experiencias: Sequence[str],
        requisitos_da_vaga: Sequence[RequisitoTecnico],
        equivalencias: Sequence[EquivalenciaTecnologia],
    ) -> ResultadoDaSelecao:
        permitidos: dict[str, str] = {}
        for item in itens_do_candidato:
            if item.strip():
                permitidos.setdefault(_chave(item), item.strip())
        itens = tuple(permitidos.values())

        nomes_da_vaga = self._nomes_considerados(requisitos_da_vaga)
        for nome in nomes_da_vaga:
            if any(menciona_tecnologia(texto, nome) for texto in textos_das_experiencias):
                permitidos.setdefault(_chave(nome), nome)
        for equivalencia in equivalencias:
            permitidos.setdefault(_chave(equivalencia.alvo), equivalencia.alvo)

        lacunas = tuple(
            nome
            for nome in nomes_da_vaga
            if _chave(nome) not in permitidos
            and not any(menciona_tecnologia(item, nome) for item in itens)
        )
        lista = tuple(permitidos.values())
        relevantes = tuple(
            item
            for item in lista
            if any(menciona_tecnologia(item, nome) or menciona_tecnologia(nome, item) for nome in nomes_da_vaga)
        )
        return ResultadoDaSelecao(permitidos=lista, lacunas=lacunas, relevantes=relevantes)

    @staticmethod
    def _nomes_considerados(requisitos: Sequence[RequisitoTecnico]) -> tuple[str, ...]:
        nomes: dict[str, str] = {}
        for requisito in requisitos:
            if requisito.categoria in _CATEGORIAS_CONSIDERADAS:
                nomes.setdefault(_chave(requisito.nome), requisito.nome.strip())
        return tuple(nomes.values())


def restringir_aos_permitidos(
    categorias: Sequence[CategoriaCompetencia], permitidos: Collection[str]
) -> tuple[CategoriaCompetencia, ...]:
    """Descarta o que a IA acrescentou fora do conjunto permitido; categoria sem item some."""
    chaves = {_chave(item) for item in permitidos}
    resultado = []
    for categoria in categorias:
        restantes = tuple(tag for tag in categoria.tags if _chave(tag) in chaves)
        if restantes:
            resultado.append(CategoriaCompetencia(categoria.nome, restantes))
    return tuple(resultado)


def limitar_ao_teto(
    categorias: Sequence[CategoriaCompetencia],
    relevantes: Collection[str],
    teto: int = TETO_DE_COMPETENCIAS,
) -> tuple[CategoriaCompetencia, ...]:
    """Corta a lista ao teto: sai primeiro, do fim para o começo, o que a vaga não pede."""
    chaves_relevantes = {_chave(nome) for nome in relevantes}
    posicoes = [
        (indice_categoria, indice_tag)
        for indice_categoria, categoria in enumerate(categorias)
        for indice_tag in range(len(categoria.tags))
    ]
    excesso = len(posicoes) - teto
    removidas: set[tuple[int, int]] = set()
    if excesso > 0:
        for relevante in (False, True):
            for posicao in reversed(posicoes):
                if len(removidas) >= excesso:
                    break
                tag = categorias[posicao[0]].tags[posicao[1]]
                if posicao not in removidas and (_chave(tag) in chaves_relevantes) == relevante:
                    removidas.add(posicao)
    resultado = []
    for indice_categoria, categoria in enumerate(categorias):
        restantes = tuple(
            tag for indice_tag, tag in enumerate(categoria.tags) if (indice_categoria, indice_tag) not in removidas
        )
        if restantes:
            resultado.append(CategoriaCompetencia(categoria.nome, restantes))
    return tuple(resultado)
