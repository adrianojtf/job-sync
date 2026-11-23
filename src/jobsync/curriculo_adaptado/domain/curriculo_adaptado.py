"""Agregado CurriculoAdaptado: o currículo adaptado para uma vaga, salvo para edição e reuso (JOB-0041).

Guarda o conteúdo estruturado (o rascunho revisado) e o contexto da vaga usado na adaptação, para
reabrir a revisão e pedir sugestões de IA sem nova análise. O PDF não é guardado aqui: é gerado
a partir do rascunho sempre que o conteúdo é salvo.

Distinto de `CurriculoSalvo` (o PDF bruto da biblioteca) e do domínio `curriculo` (a geração).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, replace
from datetime import datetime

from jobsync.curriculo import RascunhoCurriculoAdaptado
from jobsync.vaga import AnaliseVaga


def _preenchido(valor: str) -> bool:
    return bool(valor and valor.strip())


@dataclass(frozen=True)
class CurriculoAdaptado:
    id: str
    perfil_identificador: str
    nome_referencia: str
    cargo_alvo: str
    empresa_alvo: str
    idioma_alvo: str
    descricao_vaga: str
    analise_vaga: AnaliseVaga
    rascunho: RascunhoCurriculoAdaptado
    criado_em: datetime
    atualizado_em: datetime
    curriculo_salvo_id: str | None = None

    def __post_init__(self) -> None:
        obrigatorios = (
            (self.id, "O id do currículo adaptado não pode ser vazio."),
            (self.perfil_identificador, "O identificador do perfil não pode ser vazio."),
            (self.nome_referencia, "O nome de referência do currículo adaptado não pode ser vazio."),
            (self.cargo_alvo, "O cargo alvo do currículo adaptado não pode ser vazio."),
            (self.empresa_alvo, "A empresa alvo do currículo adaptado não pode ser vazia."),
            (self.idioma_alvo, "O idioma alvo do currículo adaptado não pode ser vazio."),
            (self.descricao_vaga, "A descrição da vaga do currículo adaptado não pode ser vazia."),
        )
        for valor, mensagem in obrigatorios:
            if not _preenchido(valor):
                raise ValueError(mensagem)

    @classmethod
    def novo(
        cls,
        perfil_identificador: str,
        nome_referencia: str,
        cargo_alvo: str,
        empresa_alvo: str,
        idioma_alvo: str,
        descricao_vaga: str,
        analise_vaga: AnaliseVaga,
        rascunho: RascunhoCurriculoAdaptado,
        agora: datetime,
    ) -> CurriculoAdaptado:
        return cls(
            id=str(uuid.uuid4()),
            perfil_identificador=perfil_identificador,
            nome_referencia=nome_referencia,
            cargo_alvo=cargo_alvo,
            empresa_alvo=empresa_alvo,
            idioma_alvo=idioma_alvo,
            descricao_vaga=descricao_vaga,
            analise_vaga=analise_vaga,
            rascunho=rascunho,
            criado_em=agora,
            atualizado_em=agora,
        )

    def com_rascunho_revisado(
        self, rascunho: RascunhoCurriculoAdaptado, agora: datetime
    ) -> CurriculoAdaptado:
        return replace(self, rascunho=rascunho, atualizado_em=agora)

    def com_curriculo_salvo(self, curriculo_salvo_id: str) -> CurriculoAdaptado:
        return replace(self, curriculo_salvo_id=curriculo_salvo_id)
