"""Value Object: plano de adaptação das tecnologias entre as experiências do perfil.

Regra de negócio (JOB-0037), determinística e sem IA:

1. Descarta a equivalência cujo alvo já aparece no perfil: o candidato já tem a tecnologia.
2. Usa só a primeira equivalência de cada tecnologia original.
3. Considera as experiências com descrição que citam a original (no cargo ou na descrição).
4. Uma ocorrência: troca nela. Duas ou mais: troca em todas, menos na última da ordem
   recebida, que mantém a original para o histórico continuar plausível.
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.equivalencia_tecnologia import (
    AjusteTecnologia,
    DiretrizesExperiencia,
    EquivalenciaTecnologia,
    ManutencaoTecnologia,
    menciona_tecnologia,
)


@dataclass(frozen=True)
class PlanoAdaptacao:
    ajustes: tuple[AjusteTecnologia, ...] = ()
    manutencoes: tuple[ManutencaoTecnologia, ...] = ()

    @classmethod
    def vazio(cls) -> "PlanoAdaptacao":
        return cls()

    @classmethod
    def distribuir(
        cls,
        experiencias: Sequence[ExperienciaParaAvaliacao],
        equivalencias: Iterable[EquivalenciaTecnologia],
    ) -> "PlanoAdaptacao":
        textos = [f"{experiencia.cargo}\n{experiencia.descricao}" for experiencia in experiencias]
        com_descricao = [
            indice for indice, experiencia in enumerate(experiencias) if experiencia.descricao.strip()
        ]
        ajustes: list[AjusteTecnologia] = []
        manutencoes: list[ManutencaoTecnologia] = []

        for equivalencia in cls._uma_por_original(equivalencias):
            if any(menciona_tecnologia(texto, equivalencia.alvo) for texto in textos):
                continue
            ocorrencias = [
                indice for indice in com_descricao if menciona_tecnologia(textos[indice], equivalencia.original)
            ]
            if not ocorrencias:
                continue
            trocadas = ocorrencias[:-1] or ocorrencias
            ajustes.extend(AjusteTecnologia(indice, equivalencia) for indice in trocadas)
            if len(ocorrencias) > 1:
                manutencoes.append(ManutencaoTecnologia(ocorrencias[-1], equivalencia.original))

        return cls(ajustes=tuple(ajustes), manutencoes=tuple(manutencoes))

    @property
    def equivalencias_aplicadas(self) -> tuple[EquivalenciaTecnologia, ...]:
        """Equivalências trocadas em ao menos uma experiência, uma vez cada, na ordem do plano."""
        return tuple(dict.fromkeys(ajuste.equivalencia for ajuste in self.ajustes))

    def diretrizes(self, indice_experiencia: int) -> DiretrizesExperiencia:
        return DiretrizesExperiencia(
            trocar=tuple(
                ajuste.equivalencia for ajuste in self.ajustes if ajuste.indice_experiencia == indice_experiencia
            ),
            manter=tuple(
                manutencao.tecnologia
                for manutencao in self.manutencoes
                if manutencao.indice_experiencia == indice_experiencia
            ),
        )

    @staticmethod
    def _uma_por_original(
        equivalencias: Iterable[EquivalenciaTecnologia],
    ) -> list[EquivalenciaTecnologia]:
        vistas: set[str] = set()
        unicas = []
        for equivalencia in equivalencias:
            chave = equivalencia.original.casefold()
            if chave not in vistas:
                vistas.add(chave)
                unicas.append(equivalencia)
        return unicas
