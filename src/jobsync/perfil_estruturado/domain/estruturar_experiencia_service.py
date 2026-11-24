"""Domain Service: leva uma experiência ao padrão de quatro blocos.

Reconhece os blocos que já estão no texto e pede à IA só os que faltam. O que já foi
reconhecido, ou já está nos campos da experiência, nunca é reescrito.
"""
from __future__ import annotations

import logging
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

from jobsync.perfil_estruturado.domain.blocos_experiencia import (
    BlocosExperiencia,
    ExperienciaParaCompletar,
    ReconhecedorBlocosExperiencia,
    sem_repeticao,
)
from jobsync.perfil_estruturado.domain.completador_blocos_experiencia_port import (
    CompletadorBlocosExperienciaPort,
)
from jobsync.perfil_estruturado.domain.exceptions import CompletarBlocosIndisponivel
from jobsync.perfil_estruturado.domain.perfil_estruturado import Conquista, ExperienciaProfissional
from jobsync.shared_kernel.domain.texto_normalizado import normalizar_texto

logger = logging.getLogger(__name__)

_MAXIMO_DE_CHAMADAS_EM_PARALELO = 4


class EstruturarExperienciaService:
    """Reconhece os blocos da experiência e completa os ausentes com a IA, se houver uma."""

    def __init__(
        self,
        completador: CompletadorBlocosExperienciaPort | None,
        reconhecedor: ReconhecedorBlocosExperiencia | None = None,
    ) -> None:
        self._completador = completador
        self._reconhecedor = reconhecedor or ReconhecedorBlocosExperiencia()

    def executar(self, experiencia: ExperienciaProfissional, idioma: str | None = None) -> ExperienciaProfissional:
        reconhecimento = self._reconhecedor.reconhecer(experiencia.descricao)
        atuais = BlocosExperiencia(
            contexto=experiencia.contexto,
            responsabilidades=experiencia.responsabilidades,
            realizacoes=tuple(conquista.texto for conquista in experiencia.conquistas),
            skills=experiencia.skills,
        )
        reconhecidos = atuais.completado_com(reconhecimento.blocos)
        gerados = self._gerar_ausentes(experiencia, reconhecidos, reconhecimento.resto, idioma)
        blocos = reconhecidos if gerados is None else reconhecidos.completado_com(gerados)

        logger.info(
            "Experiencia estruturada (reconhecidos=%d, completados_pela_ia=%d).",
            4 - len(reconhecidos.ausentes),
            0 if gerados is None else len(reconhecidos.ausentes) - len(blocos.ausentes),
        )
        return replace(
            experiencia,
            descricao=reconhecimento.resto if gerados is None else "",
            contexto=blocos.contexto,
            responsabilidades=blocos.responsabilidades,
            conquistas=experiencia.conquistas or self._conquistas(blocos.realizacoes),
            skills=blocos.skills,
        )

    def executar_varias(
        self, experiencias: Sequence[ExperienciaProfissional], idioma: str | None = None
    ) -> tuple[ExperienciaProfissional, ...]:
        """Estrutura as experiências em paralelo (no máximo 4 chamadas de IA ao mesmo tempo), na ordem original."""
        if len(experiencias) <= 1:
            return tuple(self.executar(experiencia, idioma) for experiencia in experiencias)
        with ThreadPoolExecutor(max_workers=_MAXIMO_DE_CHAMADAS_EM_PARALELO) as executor:
            return tuple(executor.map(lambda experiencia: self.executar(experiencia, idioma), experiencias))

    def _gerar_ausentes(
        self,
        experiencia: ExperienciaProfissional,
        reconhecidos: BlocosExperiencia,
        resto: str,
        idioma: str | None,
    ) -> BlocosExperiencia | None:
        if self._completador is None or reconhecidos.completos:
            return None
        pedido = ExperienciaParaCompletar(
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
            resto=resto,
            reconhecidos=reconhecidos,
        )
        try:
            return self._completador.completar(pedido, idioma)
        except CompletarBlocosIndisponivel:
            logger.warning("A IA não completou os blocos da experiência; ficam só os reconhecidos.")
            return None

    @staticmethod
    def _conquistas(realizacoes: tuple[str, ...]) -> tuple[Conquista, ...]:
        return tuple(Conquista(texto=texto) for texto in sem_repeticao(realizacoes, normalizar_texto))
