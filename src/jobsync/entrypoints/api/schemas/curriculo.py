"""Schemas Pydantic para endpoints do domínio de currículo."""

from __future__ import annotations

import base64
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from jobsync.curriculo import (
    AvaliacaoExperiencia,
    Curriculo,
    ExperienciaParaAvaliacao,
)
from jobsync.curriculo.service_layer.avaliar_experiencia.dtos import (
    AvaliarExperienciaInputDto,
)
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.dtos import (
    AvaliacaoExperienciaAdaptadaDto,
    AdaptarCurriculoParaVagaInputDto,
    AdaptarCurriculoParaVagaOutputDto,
    StatusAvaliacaoAutomatica,
)
from jobsync.curriculo.service_layer.analisar_ats_vaga.dtos import (
    AnalisarAtsVagaInputDto,
    AnalisarAtsVagaOutputDto,
)
from jobsync.curriculo_salvo import CurriculoSalvo
from jobsync.curriculo_salvo.service_layer.salvar_curriculo.dtos import (
    SalvarCurriculoInputDto,
)
from jobsync.entrypoints.api.schemas.avaliacao import (
    ResultadoDimensaoAvaliacaoResponse,
)
from jobsync.entrypoints.api.schemas.vaga import AvaliacaoDescricaoVagaResponse


class CurriculoSalvarRequest(BaseModel):
    """Payload para salvar um currículo PDF na biblioteca de um perfil."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "perfil_identificador": "matheus",
                "nome_referencia": "Curriculo.pdf",
                "pdf_base64": "JVBERi0xLjQgdGVzdA==",
            }
        }
    )

    perfil_identificador: str = Field(description="Identificador único do perfil dono do currículo.")
    nome_referencia: str = Field(description="Nome amigável para o currículo salvo.")
    pdf_base64: str = Field(description="Conteúdo do PDF codificado em base64.")

    def to_dto(self) -> SalvarCurriculoInputDto:
        return SalvarCurriculoInputDto(
            perfil_identificador=self.perfil_identificador,
            nome_referencia=self.nome_referencia,
            pdf_bytes=base64.b64decode(self.pdf_base64.encode()),
        )


class CurriculoSalvoResponse(BaseModel):
    """Representação de um currículo salvo na biblioteca."""

    id: str = Field(description="Identificador único do currículo salvo.")
    perfil_identificador: str = Field(description="Identificador do perfil dono do currículo.")
    nome_referencia: str = Field(description="Nome amigável do currículo salvo.")
    data_upload: datetime = Field(description="Data e hora do upload do currículo.")

    @classmethod
    def from_dto(cls, dto: CurriculoSalvo) -> CurriculoSalvoResponse:
        return cls(
            id=dto.id,
            perfil_identificador=dto.perfil_identificador,
            nome_referencia=dto.nome_referencia,
            data_upload=dto.data_upload,
        )


class CurriculosListagemResponse(BaseModel):
    """Resposta da listagem de currículos salvos de um perfil."""

    items: list[CurriculoSalvoResponse] = Field(description="Currículos salvos.")
    total: int = Field(description="Total de currículos retornados.")

    @classmethod
    def from_dto(cls, curriculos: tuple[CurriculoSalvo, ...]) -> CurriculosListagemResponse:
        return cls(
            items=[CurriculoSalvoResponse.from_dto(c) for c in curriculos],
            total=len(curriculos),
        )


class CurriculoSalvoConteudoResponse(BaseModel):
    """Resposta com o conteúdo PDF de um currículo salvo."""

    id: str = Field(description="Identificador do currículo salvo.")
    nome_referencia: str = Field(description="Nome de referência do currículo.")
    pdf_base64: str = Field(description="Conteúdo do PDF codificado em base64.")

    @classmethod
    def from_dto(cls, dto: CurriculoSalvo) -> CurriculoSalvoConteudoResponse:
        return cls(
            id=dto.id,
            nome_referencia=dto.nome_referencia,
            pdf_base64=base64.b64encode(dto.pdf_bytes).decode(),
        )


class AdaptarCurriculoRequest(BaseModel):
    """Payload para adaptar um currículo a uma vaga específica."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "descricao_vaga": "Desenvolvedor Python com experiência em FastAPI.",
                "idioma_alvo": "pt",
                "cargo_alvo": "Engenheiro de Software",
                "empresa_alvo": "TechCorp",
                "pdf_base64": "JVBERi0xLjQgdGVzdA==",
            }
        }
    )

    descricao_vaga: str = Field(description="Texto completo da descrição da vaga.")
    idioma_alvo: str = Field(description="Idioma de destino do currículo adaptado.")
    cargo_alvo: str = Field(description="Cargo alvo do currículo.")
    empresa_alvo: str = Field(description="Empresa alvo do currículo.")
    pdf_base64: str | None = Field(
        default=None,
        description="Conteúdo do PDF do currículo codificado em base64.",
    )
    perfil_identificador: str | None = Field(
        default=None,
        description="Identificador do perfil estruturado a usar como currículo (alternativa ao PDF).",
    )
    data_referencia: date | None = Field(
        default=None,
        description="Data de referência para composição do nome do arquivo.",
    )

    def to_dto(
        self,
        curriculo_pre_montado=None,
        experiencias_profissionais: tuple[ExperienciaParaAvaliacao, ...] | None = None,
    ) -> AdaptarCurriculoParaVagaInputDto:
        if curriculo_pre_montado is not None:
            pdf_curriculo = None
        elif self.pdf_base64:
            pdf_curriculo = base64.b64decode(self.pdf_base64.encode())
        else:
            raise ValueError("Informe pdf_base64 ou perfil_identificador.")
        return AdaptarCurriculoParaVagaInputDto(
            descricao_vaga=self.descricao_vaga,
            idioma_alvo=self.idioma_alvo,
            cargo_alvo=self.cargo_alvo,
            empresa_alvo=self.empresa_alvo,
            pdf_curriculo=pdf_curriculo,
            curriculo_pre_montado=curriculo_pre_montado,
            data_referencia=self.data_referencia,
            experiencias_profissionais=experiencias_profissionais,
        )


class AvaliacaoExperienciaResponse(BaseModel):
    """Score geral e resultados categóricos de uma experiência."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "score": 74,
                "clareza_escrita": {"score": 80, "nivel": "clara", "confianca": 0.84},
                "qualidade_detalhe": {"score": 75, "nivel": "detalhada", "confianca": 0.79},
                "aderencia_vaga": {"score": 70, "nivel": "boa aderencia", "confianca": 0.81},
                "consistencia_textual": {
                    "score": 70,
                    "nivel": "consistente",
                    "confianca": 0.73,
                },
            }
        }
    )

    score: int = Field(
        ge=0,
        le=100,
        description="Média aritmética das quatro dimensões, normalizada de 0 a 100.",
        examples=[74],
    )
    clareza_escrita: ResultadoDimensaoAvaliacaoResponse = Field(
        description="Avaliação da clareza, organização e legibilidade."
    )
    qualidade_detalhe: ResultadoDimensaoAvaliacaoResponse = Field(
        description="Avaliação do nível de detalhe das responsabilidades e resultados descritos."
    )
    aderencia_vaga: ResultadoDimensaoAvaliacaoResponse = Field(
        description="Avaliação da relevância para a vaga-alvo."
    )
    consistencia_textual: ResultadoDimensaoAvaliacaoResponse = Field(
        description="Avaliação da coerência e sustentação das afirmações pelo próprio texto."
    )

    @classmethod
    def from_domain(
        cls,
        avaliacao: AvaliacaoExperiencia,
    ) -> "AvaliacaoExperienciaResponse":
        return cls(
            score=avaliacao.score,
            clareza_escrita=ResultadoDimensaoAvaliacaoResponse.from_domain(
                avaliacao.clareza_escrita
            ),
            qualidade_detalhe=ResultadoDimensaoAvaliacaoResponse.from_domain(
                avaliacao.qualidade_detalhe
            ),
            aderencia_vaga=ResultadoDimensaoAvaliacaoResponse.from_domain(
                avaliacao.aderencia_vaga
            ),
            consistencia_textual=ResultadoDimensaoAvaliacaoResponse.from_domain(
                avaliacao.consistencia_textual
            ),
        )


class ExperienciaParaAvaliacaoResponse(BaseModel):
    """Experiência adaptada associada a um resultado Jev."""

    cargo: str = Field(description="Cargo original da experiência.")
    empresa: str = Field(description="Empresa original da experiência.")
    periodo: str = Field(description="Período original da experiência.")
    descricao: str = Field(description="Descrição da experiência após adaptação.")

    @classmethod
    def from_domain(cls, dto: ExperienciaParaAvaliacao) -> "ExperienciaParaAvaliacaoResponse":
        return cls(
            cargo=dto.cargo,
            empresa=dto.empresa,
            periodo=dto.periodo,
            descricao=dto.descricao,
        )


class AvaliacaoExperienciaAdaptadaResponse(BaseModel):
    """Status e resultado opcional de avaliação de uma experiência adaptada."""

    experiencia: ExperienciaParaAvaliacaoResponse = Field(
        description="Experiência individual à qual o resultado se refere."
    )
    status: Literal["avaliada", "indisponivel"] = Field(
        description="Indica se a avaliação Jev foi concluída.",
        examples=["avaliada"],
    )
    avaliacao: AvaliacaoExperienciaResponse | None = Field(
        description="Resultado Jev; nulo quando o provedor esteve indisponível.",
    )

    @classmethod
    def from_dto(
        cls, dto: AvaliacaoExperienciaAdaptadaDto
    ) -> "AvaliacaoExperienciaAdaptadaResponse":
        return cls(
            experiencia=ExperienciaParaAvaliacaoResponse.from_domain(dto.experiencia),
            status=dto.status.value,
            avaliacao=(
                AvaliacaoExperienciaResponse.from_domain(dto.avaliacao)
                if dto.avaliacao is not None
                else None
            ),
        )


class AdaptarCurriculoResponse(BaseModel):
    """Resultado da adaptação de um currículo para uma vaga."""

    nome_arquivo: str = Field(description="Nome padronizado do PDF gerado.")
    pdf_base64: str = Field(description="PDF do currículo adaptado codificado em base64.")
    nome_completo: str = Field(description="Nome completo do candidato extraído do currículo.")
    avaliacao_vaga: AvaliacaoDescricaoVagaResponse | None = Field(
        default=None,
        description="Avaliação automática da vaga; nula se o Jev estiver indisponível.",
    )
    status_avaliacao_vaga: Literal["avaliada", "indisponivel"] | None = Field(
        default=None,
        description="Status da avaliação automática da descrição de vaga.",
    )
    avaliacoes_experiencias: list[AvaliacaoExperienciaAdaptadaResponse] = Field(
        default_factory=list,
        description="Avaliação Jev de cada experiência de um perfil estruturado.",
    )

    @classmethod
    def from_dto(cls, dto: AdaptarCurriculoParaVagaOutputDto) -> AdaptarCurriculoResponse:
        return cls(
            nome_arquivo=dto.nome_arquivo.valor,
            pdf_base64=base64.b64encode(dto.pdf_bytes).decode(),
            nome_completo=dto.curriculo_adaptado.nome_completo,
            avaliacao_vaga=(
                AvaliacaoDescricaoVagaResponse.from_domain(dto.avaliacao_vaga)
                if dto.avaliacao_vaga is not None
                else None
            ),
            status_avaliacao_vaga=(
                dto.status_avaliacao_vaga.value
                if dto.status_avaliacao_vaga is not None
                else None
            ),
            avaliacoes_experiencias=[
                AvaliacaoExperienciaAdaptadaResponse.from_dto(resultado)
                for resultado in dto.avaliacoes_experiencias
            ],
        )


class AnalisarAtsRequest(BaseModel):
    """Payload para análise de aderência ATS de um currículo a uma vaga."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "descricao_vaga": "Desenvolvedor Python com experiência em FastAPI.",
                "pdf_base64": "JVBERi0xLjQgdGVzdA==",
            }
        }
    )

    descricao_vaga: str = Field(description="Texto completo da descrição da vaga.")
    pdf_base64: str | None = Field(
        default=None,
        description="Conteúdo do PDF do currículo codificado em base64.",
    )
    perfil_identificador: str | None = Field(
        default=None,
        description="Identificador do perfil estruturado a usar como currículo (alternativa ao PDF).",
    )

    def to_dto(self, curriculo_pre_montado=None) -> AnalisarAtsVagaInputDto:
        if curriculo_pre_montado is not None:
            pdf_curriculo = None
        elif self.pdf_base64:
            pdf_curriculo = base64.b64decode(self.pdf_base64.encode())
        else:
            raise ValueError("Informe pdf_base64 ou perfil_identificador.")
        return AnalisarAtsVagaInputDto(
            descricao_vaga=self.descricao_vaga,
            pdf_curriculo=pdf_curriculo,
            curriculo_pre_montado=curriculo_pre_montado,
        )


class RequisitoFaltanteResponse(BaseModel):
    """Requisito técnico não coberto pelo currículo."""

    nome: str = Field(description="Nome do requisito técnico faltante.")
    categoria: str = Field(description="Categoria do requisito técnico.")
    tipo: str = Field(description="Tipo do requisito técnico (explícito, implícito ou ambíguo).")


class GerarCartaApresentacaoRequest(AdaptarCurriculoRequest):
    """Payload para gerar carta de apresentação."""


class CartaApresentacaoResponse(BaseModel):
    """Texto da carta de apresentação gerada."""

    carta: str = Field(description="Texto da carta de apresentação.")


class AnalisarAtsResponse(BaseModel):
    """Resultado da análise de aderência ATS."""

    nome_completo: str = Field(description="Nome completo do candidato.")
    nota: int = Field(description="Nota de aderência (0 a 100).")
    requisitos_faltantes: list[RequisitoFaltanteResponse] = Field(
        default_factory=list,
        description="Requisitos técnicos explícitos não cobertos pelo currículo.",
    )
    sugestoes: list[str] = Field(
        default_factory=list,
        description="Sugestões de melhoria para aumentar a aderência.",
    )

    @classmethod
    def from_dto(cls, dto: AnalisarAtsVagaOutputDto) -> AnalisarAtsResponse:
        return cls(
            nome_completo=dto.curriculo.nome_completo,
            nota=dto.resultado_ats.nota,
            requisitos_faltantes=[
                RequisitoFaltanteResponse(
                    nome=req.nome,
                    categoria=req.categoria.name,
                    tipo=req.tipo.name,
                )
                for req in dto.resultado_ats.requisitos_faltantes
            ],
            sugestoes=list(dto.sugestoes),
        )


class ExperienciaParaAvaliacaoRequest(BaseModel):
    """Dados de uma experiência profissional para avaliação sob demanda."""

    cargo: str = Field(
        default="",
        description="Cargo associado à experiência, quando disponível.",
        examples=["Pessoa desenvolvedora backend"],
    )
    empresa: str = Field(
        default="",
        description="Empresa associada à experiência, quando disponível.",
        examples=["TechCorp"],
    )
    periodo: str = Field(
        default="",
        description="Período da experiência, quando disponível.",
        examples=["2022-2025"],
    )
    descricao: str = Field(
        min_length=1,
        description="Texto individual da experiência profissional.",
        examples=["Desenvolvi APIs internas e reduzi o tempo de processamento."],
    )

    @field_validator("descricao")
    @classmethod
    def validar_descricao_nao_vazia(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("O texto da experiência profissional é obrigatório.")
        return valor

    def to_domain(self) -> ExperienciaParaAvaliacao:
        return ExperienciaParaAvaliacao(
            descricao=self.descricao,
            cargo=self.cargo,
            empresa=self.empresa,
            periodo=self.periodo,
        )


class AvaliarExperienciaRequest(BaseModel):
    """Payload para avaliar uma experiência em relação a uma vaga-alvo."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "experiencia": {
                    "cargo": "Pessoa desenvolvedora backend",
                    "empresa": "TechCorp",
                    "periodo": "2022-2025",
                    "descricao": "Desenvolvi APIs internas e reduzi o tempo de processamento.",
                },
                "descricao_vaga": "Vaga para pessoa desenvolvedora Python com FastAPI.",
            }
        }
    )

    experiencia: ExperienciaParaAvaliacaoRequest = Field(
        description="Experiência profissional individual a ser avaliada."
    )
    descricao_vaga: str = Field(
        min_length=1,
        description="Descrição da vaga usada como contexto para avaliar aderência.",
        examples=["Vaga para pessoa desenvolvedora Python com FastAPI."],
    )

    @field_validator("descricao_vaga")
    @classmethod
    def validar_vaga_nao_vazia(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("A descrição da vaga-alvo é obrigatória.")
        return valor

    def to_dto(self) -> AvaliarExperienciaInputDto:
        return AvaliarExperienciaInputDto(
            experiencia=self.experiencia.to_domain(),
            descricao_vaga=self.descricao_vaga,
        )
