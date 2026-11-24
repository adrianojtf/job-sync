"""Interpreta o texto de uma seção em blocos (empresa, período, cargo, tópicos, contexto).

Serve às seções de experiências, formação e certificações. O texto chega por dois caminhos:
escrito pela IA no formato do modelo ("Empresa Período", cargo na linha seguinte) ou montado
pelo sistema no formato "Cargo — Empresa (Período)". Nenhuma linha de entrada é descartada.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from jobsync.shared_kernel.domain.rotulos_blocos_experiencia import BlocoExperiencia as TipoBloco
from jobsync.shared_kernel.domain.rotulos_blocos_experiencia import bloco_do_rotulo

_MES = r"(?:jan|fev|feb|mar|abr|apr|mai|may|jun|jul|ago|aug|set|sep|out|oct|nov|dez|dec)[a-zç]*\.?"
_DATA = rf"(?:{_MES}\s+\d{{4}}|\d{{1,2}}/\d{{4}}|\d{{4}})"
_FIM = rf"(?:{_DATA}|presente?|atual|current|hoje)"
_PERIODO = rf"{_DATA}\s*[-–—]\s*{_FIM}"
_PERIODO_NO_FIM = re.compile(
    rf"^(?P<antes>.+?)\s+(?:\(\s*(?P<entre_parenteses>{_PERIODO})\s*\)|(?P<solto>{_PERIODO}))\s*$",
    re.IGNORECASE,
)
_PARENTESES_NO_FIM = re.compile(r"\(([^()]*)\)\s*$")
_PERIODO_OU_DATA = re.compile(rf"^(?:{_PERIODO}|{_DATA})$", re.IGNORECASE)
_SEPARADOR_CARGO_EMPRESA = " — "
_MARCADOR_DE_TOPICO = re.compile(r"^[-•●*]\s*")
_TAMANHO_MAXIMO_DO_CARGO = 80


@dataclass(frozen=True)
class BlocoExperiencia:
    """Uma experiência, formação ou certificação já separada em partes."""

    empresa: str
    periodo: str = ""
    cargo: str = ""
    topicos: tuple[str, ...] = ()
    contexto: str = ""
    descricao: tuple[str, ...] = ()
    responsabilidades: tuple[str, ...] = ()
    realizacoes: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()
    rotulo_responsabilidades: str = ""
    rotulo_realizacoes: str = ""
    rotulo_skills: str = ""

    @property
    def estruturado(self) -> bool:
        """Indica se o texto traz cabeçalhos de bloco (responsabilidades, realizações ou skills)."""
        return bool(self.responsabilidades or self.realizacoes or self.skills)


class InterpretadorExperiencias:
    """Converte o texto de uma seção em uma lista de BlocoExperiencia."""

    def interpretar(self, conteudo: str) -> list[BlocoExperiencia]:
        return [self._interpretar_bloco(linhas) for linhas in self._separar_blocos(conteudo)]

    @staticmethod
    def _separar_blocos(conteudo: str) -> list[list[str]]:
        blocos: list[list[str]] = []
        atual: list[str] = []
        for linha in conteudo.splitlines():
            linha_tratada = linha.strip()
            if linha_tratada:
                atual.append(linha_tratada)
            elif atual:
                blocos.append(atual)
                atual = []
        if atual:
            blocos.append(atual)
        return blocos

    def _interpretar_bloco(self, linhas: list[str]) -> BlocoExperiencia:
        empresa, periodo, cargo = self._ler_cabecalho(linhas[0])
        topicos: list[str] = []
        descricao: list[str] = []
        contexto: list[str] = []
        listas: dict[TipoBloco, list[str]] = {
            TipoBloco.RESPONSABILIDADES: [],
            TipoBloco.REALIZACOES: [],
            TipoBloco.SKILLS: [],
        }
        rotulos: dict[TipoBloco, str] = {}
        bloco_aberto: TipoBloco | None = None
        em_contexto = False

        for indice, linha in enumerate(linhas[1:], start=1):
            cabecalho = None if _MARCADOR_DE_TOPICO.match(linha) else self._ler_cabecalho_de_bloco(linha)
            if _MARCADOR_DE_TOPICO.match(linha):
                texto = _MARCADOR_DE_TOPICO.sub("", linha, count=1).strip()
                if texto:
                    (listas[bloco_aberto] if bloco_aberto in listas else topicos).append(texto)
                em_contexto = False
            elif cabecalho is not None and cabecalho[0] == TipoBloco.CONTEXTO:
                contexto.append(linha)
                em_contexto = True
                bloco_aberto = None
            elif cabecalho is not None:
                bloco, rotulo, resto = cabecalho
                rotulos[bloco] = rotulo
                bloco_aberto = bloco if bloco != TipoBloco.SKILLS else None
                em_contexto = False
                if bloco == TipoBloco.SKILLS:
                    listas[bloco].extend(self._separar_skills(resto))
                elif resto:
                    listas[bloco].append(resto)
            elif em_contexto:
                contexto.append(linha)
            elif indice == 1 and not cargo and self._parece_cargo(linha):
                cargo = linha
            else:
                descricao.append(linha)

        return BlocoExperiencia(
            empresa=empresa,
            periodo=periodo,
            cargo=cargo,
            topicos=tuple(topicos),
            contexto=" ".join(contexto),
            descricao=tuple(descricao),
            responsabilidades=tuple(listas[TipoBloco.RESPONSABILIDADES]),
            realizacoes=tuple(listas[TipoBloco.REALIZACOES]),
            skills=tuple(listas[TipoBloco.SKILLS]),
            rotulo_responsabilidades=rotulos.get(TipoBloco.RESPONSABILIDADES, ""),
            rotulo_realizacoes=rotulos.get(TipoBloco.REALIZACOES, ""),
            rotulo_skills=rotulos.get(TipoBloco.SKILLS, ""),
        )

    @staticmethod
    def _ler_cabecalho_de_bloco(linha: str) -> tuple[TipoBloco, str, str] | None:
        """Devolve (bloco, rótulo como escrito, texto depois dos dois-pontos) se a linha abre um bloco."""
        rotulo, separador, resto = linha.partition(":")
        if not separador:
            return None
        bloco = bloco_do_rotulo(rotulo)
        if bloco is None:
            return None
        return bloco, rotulo.strip(), resto.strip()

    @staticmethod
    def _separar_skills(texto: str) -> list[str]:
        separador = "|" if "|" in texto else ","
        return [skill.strip() for skill in texto.split(separador) if skill.strip()]

    def _ler_cabecalho(self, linha: str) -> tuple[str, str, str]:
        """Devolve (empresa, período, cargo); o cargo só vem do cabeçalho com travessão."""
        if _SEPARADOR_CARGO_EMPRESA in linha:
            esquerda, direita = linha.split(_SEPARADOR_CARGO_EMPRESA, 1)
            empresa, periodo = self._separar_empresa_e_periodo(direita)
            if esquerda.strip() and empresa:
                return empresa, periodo, esquerda.strip()
        empresa, periodo = self._separar_empresa_e_periodo(linha)
        return empresa, periodo, ""

    @staticmethod
    def _separar_empresa_e_periodo(texto: str) -> tuple[str, str]:
        texto = texto.strip()
        entre_parenteses = _PARENTESES_NO_FIM.search(texto)
        if entre_parenteses:
            conteudo = entre_parenteses.group(1).strip()
            if not conteudo or _PERIODO_OU_DATA.match(conteudo):
                return texto[: entre_parenteses.start()].strip(), conteudo
        correspondencia = _PERIODO_NO_FIM.match(texto)
        if correspondencia:
            periodo = correspondencia.group("entre_parenteses") or correspondencia.group("solto")
            return correspondencia.group("antes").strip(), periodo.strip()
        return texto, ""

    @staticmethod
    def _parece_cargo(linha: str) -> bool:
        return len(linha) <= _TAMANHO_MAXIMO_DO_CARGO and not re.search(r"\d{4}", linha)
