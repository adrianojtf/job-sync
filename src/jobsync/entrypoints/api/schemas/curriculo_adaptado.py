"""Schemas Pydantic de /curriculos-adaptados: o currículo adaptado salvo para edição e reuso."""
from __future__ import annotations

import base64
from datetime import date, datetime

from pydantic import BaseModel, Field

from jobsync.curriculo_adaptado.domain.curriculo_adaptado import CurriculoAdaptado
from jobsync.curriculo_adaptado.service_layer.atualizar_curriculo_adaptado import (
    AtualizarCurriculoAdaptadoInputDto,
)
from jobsync.curriculo_adaptado.service_layer.resultado_com_pdf import CurriculoAdaptadoComPdf
from jobsync.curriculo_adaptado.service_layer.salvar_curriculo_adaptado import (
    SalvarCurriculoAdaptadoInputDto,
)
from jobsync.entrypoints.api.schemas.curriculo import RascunhoCurriculoAdaptadoSchema
from jobsync.entrypoints.api.schemas.vaga import AnaliseVagaSchema


class CurriculoAdaptadoSalvarRequest(BaseModel):
    """Rascunho confirmado na revisão e a vaga usada na adaptação."""

    perfil_identificador: str = Field(description="Perfil dono do currículo.")
    rascunho: RascunhoCurriculoAdaptadoSchema = Field(
        description="Rascunho no estado em que o usuário confirmou."
    )
    idioma_alvo: str = Field(description="Idioma de destino do currículo.")
    cargo_alvo: str = Field(description="Cargo alvo (usado no nome do arquivo).")
    empresa_alvo: str = Field(description="Empresa alvo (usada no nome do arquivo).")
    descricao_vaga: str = Field(description="Descrição da vaga usada na adaptação.")
    analise_vaga: AnaliseVagaSchema = Field(
        description="Análise da vaga devolvida na adaptação; guardada para as sugestões de IA."
    )
    data_referencia: date | None = Field(
        default=None, description="Data de referência para o nome do arquivo."
    )

    def to_dto(self) -> SalvarCurriculoAdaptadoInputDto:
        """Converte para o DTO; levanta ValueError se o rascunho ou a análise forem inválidos."""
        return SalvarCurriculoAdaptadoInputDto(
            perfil_identificador=self.perfil_identificador,
            rascunho=self.rascunho.to_domain(),
            idioma_alvo=self.idioma_alvo,
            cargo_alvo=self.cargo_alvo,
            empresa_alvo=self.empresa_alvo,
            descricao_vaga=self.descricao_vaga,
            analise_vaga=self.analise_vaga.to_domain(),
            data_referencia=self.data_referencia,
        )


class CurriculoAdaptadoAtualizarRequest(BaseModel):
    """Rascunho editado de um currículo adaptado já salvo."""

    perfil_identificador: str = Field(description="Perfil dono do currículo.")
    rascunho: RascunhoCurriculoAdaptadoSchema = Field(
        description="Rascunho no estado em que o usuário confirmou a edição."
    )
    data_referencia: date | None = Field(
        default=None, description="Data de referência para o nome do arquivo."
    )

    def to_dto(self, curriculo_id: str) -> AtualizarCurriculoAdaptadoInputDto:
        """Converte para o DTO; levanta ValueError se o rascunho for inválido."""
        return AtualizarCurriculoAdaptadoInputDto(
            curriculo_id=curriculo_id,
            perfil_identificador=self.perfil_identificador,
            rascunho=self.rascunho.to_domain(),
            data_referencia=self.data_referencia,
        )


class CurriculoAdaptadoPdfResponse(BaseModel):
    """Currículo adaptado salvo e o PDF gerado a partir dele."""

    id: str = Field(description="Identificador do currículo adaptado.")
    nome_arquivo: str = Field(description="Nome padronizado do PDF gerado.")
    pdf_base64: str = Field(description="PDF codificado em base64.")
    atualizado_em: datetime = Field(description="Instante da última gravação, em UTC.")

    @classmethod
    def from_dto(cls, dto: CurriculoAdaptadoComPdf) -> CurriculoAdaptadoPdfResponse:
        return cls(
            id=dto.curriculo.id,
            nome_arquivo=dto.nome_arquivo.valor,
            pdf_base64=base64.b64encode(dto.pdf_bytes).decode(),
            atualizado_em=dto.curriculo.atualizado_em,
        )


class CurriculoAdaptadoResumoResponse(BaseModel):
    """Currículo adaptado na listagem, sem o conteúdo."""

    id: str = Field(description="Identificador do currículo adaptado.")
    nome_referencia: str = Field(description="Nome de referência (nome do arquivo gerado).")
    cargo_alvo: str = Field(description="Cargo da vaga usada na adaptação.")
    empresa_alvo: str = Field(description="Empresa da vaga usada na adaptação.")
    idioma_alvo: str = Field(description="Idioma do currículo.")
    curriculo_salvo_id: str | None = Field(
        description="Currículo salvo (PDF) gerado a partir deste, quando já houve candidatura."
    )
    criado_em: datetime = Field(description="Instante da criação, em UTC.")
    atualizado_em: datetime = Field(description="Instante da última edição, em UTC.")

    @classmethod
    def from_domain(cls, curriculo: CurriculoAdaptado) -> CurriculoAdaptadoResumoResponse:
        return cls(
            id=curriculo.id,
            nome_referencia=curriculo.nome_referencia,
            cargo_alvo=curriculo.cargo_alvo,
            empresa_alvo=curriculo.empresa_alvo,
            idioma_alvo=curriculo.idioma_alvo,
            curriculo_salvo_id=curriculo.curriculo_salvo_id,
            criado_em=curriculo.criado_em,
            atualizado_em=curriculo.atualizado_em,
        )


class CurriculosAdaptadosListagemResponse(BaseModel):
    items: list[CurriculoAdaptadoResumoResponse] = Field(description="Currículos adaptados do perfil.")
    total: int = Field(description="Total de currículos retornados.")

    @classmethod
    def from_domain(
        cls, curriculos: tuple[CurriculoAdaptado, ...]
    ) -> CurriculosAdaptadosListagemResponse:
        return cls(
            items=[CurriculoAdaptadoResumoResponse.from_domain(c) for c in curriculos],
            total=len(curriculos),
        )


class CurriculoAdaptadoResponse(CurriculoAdaptadoResumoResponse):
    """Currículo adaptado completo: o conteúdo para a revisão e a vaga para as sugestões de IA."""

    descricao_vaga: str = Field(description="Descrição da vaga usada na adaptação.")
    analise_vaga: AnaliseVagaSchema = Field(description="Análise da vaga usada na adaptação.")
    rascunho: RascunhoCurriculoAdaptadoSchema = Field(description="Conteúdo salvo, para a revisão.")

    @classmethod
    def from_domain(cls, curriculo: CurriculoAdaptado) -> CurriculoAdaptadoResponse:
        return cls(
            **CurriculoAdaptadoResumoResponse.from_domain(curriculo).model_dump(),
            descricao_vaga=curriculo.descricao_vaga,
            analise_vaga=AnaliseVagaSchema.from_domain(curriculo.analise_vaga),
            rascunho=RascunhoCurriculoAdaptadoSchema.from_domain(curriculo.rascunho),
        )
