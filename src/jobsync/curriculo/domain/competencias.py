"""Value Objects: competências do currículo, agrupadas em categorias com tags (JOB-0041).

Cada categoria tem um nome livre (ex.: "Linguagens") e uma lista de tags (ex.: "Java", "Python").
O texto "Rótulo: a, b", uma categoria por linha, é o formato que a IA devolve e que o gerador
de PDF reconhece; as funções deste módulo convertem entre o texto e as categorias.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

CATEGORIA_PADRAO = "Tecnologias"
_MARCADORES = "-•* "


def _preenchido(valor: str) -> bool:
    return bool(valor and valor.strip())


@dataclass(frozen=True)
class CategoriaCompetencia:
    nome: str
    tags: tuple[str, ...]

    def __post_init__(self) -> None:
        if not _preenchido(self.nome):
            raise ValueError("Informe o nome da categoria de competências.")
        if not self.tags or not all(_preenchido(tag) for tag in self.tags):
            raise ValueError(f"A categoria '{self.nome}' precisa de ao menos uma tag com texto.")

    @classmethod
    def revisada(cls, nome: str, tags: Iterable[str]) -> CategoriaCompetencia | None:
        """Monta a categoria editada pelo usuário; devolve None se ficou sem nome ou sem tags."""
        tags_revisadas = _tags_sem_repeticao(tags)
        if not _preenchido(nome) or not tags_revisadas:
            return None
        return cls(nome=nome.strip(), tags=tags_revisadas)

    def para_linha(self) -> str:
        return f"{self.nome}: {', '.join(self.tags)}"


def _tags_sem_repeticao(tags: Iterable[str]) -> tuple[str, ...]:
    vistas: set[str] = set()
    resultado: list[str] = []
    for tag in tags:
        if not _preenchido(tag):
            continue
        limpa = tag.strip()
        if limpa.casefold() not in vistas:
            vistas.add(limpa.casefold())
            resultado.append(limpa)
    return tuple(resultado)


def categorias_de_texto(conteudo: str) -> tuple[CategoriaCompetencia, ...]:
    """Lê linhas "Rótulo: a, b"; linhas sem rótulo formam a categoria padrão."""
    categorias: list[CategoriaCompetencia] = []
    sem_rotulo: list[str] = []
    for linha in conteudo.splitlines():
        texto = linha.strip().lstrip(_MARCADORES).strip()
        if not texto:
            continue
        rotulo, separador, resto = texto.partition(":")
        if separador and _preenchido(rotulo):
            categoria = CategoriaCompetencia.revisada(rotulo, _separar_tags(resto))
            if categoria is not None:
                categorias.append(categoria)
        else:
            sem_rotulo.extend(_separar_tags(texto))
    padrao = CategoriaCompetencia.revisada(CATEGORIA_PADRAO, sem_rotulo)
    if padrao is not None:
        categorias.append(padrao)
    return tuple(categorias)


def categorias_para_texto(categorias: Iterable[CategoriaCompetencia]) -> str:
    return "\n".join(categoria.para_linha() for categoria in categorias)


def _separar_tags(texto: str) -> list[str]:
    """Separa por vírgula, ignorando as que estão dentro de parênteses."""
    tags: list[str] = []
    atual: list[str] = []
    profundidade = 0
    for caractere in texto:
        if caractere == "(":
            profundidade += 1
        elif caractere == ")" and profundidade:
            profundidade -= 1
        if caractere == "," and profundidade == 0:
            tags.append("".join(atual))
            atual = []
        else:
            atual.append(caractere)
    tags.append("".join(atual))
    return tags
