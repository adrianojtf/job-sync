"""Blocos de uma experiência (contexto, responsabilidades, realizações e skills) e seu reconhecimento.

O texto de uma experiência pode trazer os blocos com rótulos ("Key Achievements:", "Tecnologias:").
`ReconhecedorBlocosExperiencia` os separa sem reescrever nada; o que sobra sem rótulo é o `resto`,
que a IA usa como fonte para completar só os blocos ausentes.
"""
from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace

from jobsync.shared_kernel.domain.rotulos_blocos_experiencia import BlocoExperiencia, bloco_do_rotulo

_MARCADOR_DE_ITEM = re.compile(r"^[-•●*]\s*")


def chave_de_tecnologia(texto: str) -> str:
    """Chave de comparação de uma tecnologia: sem caixa e com espaços simples (mantém `C#` e `C++`)."""
    return " ".join(texto.split()).casefold()


def sem_repeticao(itens: Iterable[str], chave: Callable[[str], str] = chave_de_tecnologia) -> tuple[str, ...]:
    vistas: set[str] = set()
    resultado: list[str] = []
    for item in itens:
        limpo = item.strip()
        if limpo and chave(limpo) not in vistas:
            vistas.add(chave(limpo))
            resultado.append(limpo)
    return tuple(resultado)


@dataclass(frozen=True)
class BlocosExperiencia:
    """Os quatro blocos de uma experiência; um bloco vazio é um bloco ausente."""

    contexto: str = ""
    responsabilidades: tuple[str, ...] = ()
    realizacoes: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()

    @property
    def ausentes(self) -> tuple[BlocoExperiencia, ...]:
        presentes = {
            BlocoExperiencia.CONTEXTO: bool(self.contexto.strip()),
            BlocoExperiencia.RESPONSABILIDADES: bool(self.responsabilidades),
            BlocoExperiencia.REALIZACOES: bool(self.realizacoes),
            BlocoExperiencia.SKILLS: bool(self.skills),
        }
        return tuple(bloco for bloco in BlocoExperiencia if not presentes[bloco])

    @property
    def completos(self) -> bool:
        return not self.ausentes

    def completado_com(self, outros: BlocosExperiencia) -> BlocosExperiencia:
        """Blocos novos: os presentes aqui prevalecem; só os ausentes vêm de `outros`."""
        ausentes = self.ausentes
        return replace(
            self,
            contexto=outros.contexto if BlocoExperiencia.CONTEXTO in ausentes else self.contexto,
            responsabilidades=(
                outros.responsabilidades
                if BlocoExperiencia.RESPONSABILIDADES in ausentes
                else self.responsabilidades
            ),
            realizacoes=outros.realizacoes if BlocoExperiencia.REALIZACOES in ausentes else self.realizacoes,
            skills=outros.skills if BlocoExperiencia.SKILLS in ausentes else self.skills,
        )


@dataclass(frozen=True)
class ExperienciaParaCompletar:
    """O que a IA recebe para completar uma experiência: o texto sem rótulo e o que já foi reconhecido."""

    cargo: str
    empresa: str
    periodo: str
    resto: str
    reconhecidos: BlocosExperiencia


@dataclass(frozen=True)
class ResultadoReconhecimento:
    blocos: BlocosExperiencia
    resto: str


class ReconhecedorBlocosExperiencia:
    """Separa o texto de uma experiência nos blocos que têm rótulo, sem reescrever o conteúdo."""

    def reconhecer(self, texto: str) -> ResultadoReconhecimento:
        contexto: list[str] = []
        listas: dict[BlocoExperiencia, list[str]] = {
            BlocoExperiencia.RESPONSABILIDADES: [],
            BlocoExperiencia.REALIZACOES: [],
            BlocoExperiencia.SKILLS: [],
        }
        resto: list[str] = []
        aberto: BlocoExperiencia | None = None

        for linha in (linha.strip() for linha in texto.splitlines()):
            if not linha:
                continue
            e_item = bool(_MARCADOR_DE_ITEM.match(linha))
            cabecalho = None if e_item else self._ler_cabecalho(linha)
            if cabecalho is not None:
                aberto, conteudo = cabecalho
                self._receber(aberto, conteudo, contexto, listas, e_item=False)
            elif aberto is None or self._encerra_o_bloco(aberto, linha, e_item):
                aberto = None
                resto.append(linha)
            else:
                conteudo = _MARCADOR_DE_ITEM.sub("", linha, count=1).strip() if e_item else linha
                self._receber(aberto, conteudo, contexto, listas, e_item=e_item)

        blocos = BlocosExperiencia(
            contexto=" ".join(contexto).strip(),
            responsabilidades=sem_repeticao(listas[BlocoExperiencia.RESPONSABILIDADES], _chave_de_frase),
            realizacoes=sem_repeticao(listas[BlocoExperiencia.REALIZACOES], _chave_de_frase),
            skills=sem_repeticao(listas[BlocoExperiencia.SKILLS]),
        )
        return ResultadoReconhecimento(blocos=blocos, resto="\n".join(resto))

    @staticmethod
    def _encerra_o_bloco(aberto: BlocoExperiencia, linha: str, e_item: bool) -> bool:
        """Contexto não tem itens, e as skills só seguem em item ou em linha que continua a lista."""
        if aberto == BlocoExperiencia.CONTEXTO:
            return e_item
        if aberto == BlocoExperiencia.SKILLS:
            return not (e_item or linha.startswith(("|", ",")))
        return False

    @staticmethod
    def _ler_cabecalho(linha: str) -> tuple[BlocoExperiencia, str] | None:
        rotulo, separador, resto = linha.partition(":")
        if not separador:
            return None
        bloco = bloco_do_rotulo(rotulo)
        return None if bloco is None else (bloco, resto.strip())

    @staticmethod
    def _receber(
        bloco: BlocoExperiencia,
        conteudo: str,
        contexto: list[str],
        listas: dict[BlocoExperiencia, list[str]],
        e_item: bool,
    ) -> None:
        if not conteudo:
            return
        if bloco == BlocoExperiencia.CONTEXTO:
            contexto.append(conteudo)
        elif bloco == BlocoExperiencia.SKILLS:
            separador = "|" if "|" in conteudo else ","
            listas[bloco].extend(skill.strip() for skill in conteudo.split(separador))
        elif e_item or not listas[bloco]:
            listas[bloco].append(conteudo)
        else:
            listas[bloco][-1] = f"{listas[bloco][-1]} {conteudo}"


def _chave_de_frase(texto: str) -> str:
    return " ".join(texto.split()).casefold().rstrip(".")
