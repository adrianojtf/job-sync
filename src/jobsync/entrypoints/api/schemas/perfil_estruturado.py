"""Schemas Pydantic para endpoints do domínio de perfil estruturado."""

from __future__ import annotations

import base64

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from jobsync.perfil_estruturado.domain.perfil_estruturado import (
    Certificacao,
    Conquista,
    DadosPerfilExtraidos,
    ExperienciaProfissional,
    FormacaoAcademica,
    Idioma,
    NivelIdioma,
    OrigemConquista,
    PerfilEstruturado,
)
from jobsync.perfil_estruturado.service_layer.importar_perfil_de_pdf.dtos import (
    ImportarPerfilDePdfInputDto,
)
from jobsync.perfil_estruturado.service_layer.salvar_perfil_estruturado.dtos import (
    SalvarPerfilEstruturadoInputDto,
)
from jobsync.perfil_estruturado.service_layer.verificar_conquistas_parecidas.dtos import (
    VerificarConquistasParecidasInputDto,
)


OrigemConquistaSchema = Literal["MANUAL", "RESPOSTA_PERGUNTA"]


class ConquistaRequest(BaseModel):
    """Uma conquista guardada no banco de conquistas da experiência."""

    texto: str = Field(description="Texto da conquista, escrito ou aprovado pelo usuário.")
    origem: OrigemConquistaSchema = Field(
        default="MANUAL",
        description="Origem da conquista: cadastro manual ou resposta às perguntas sobre a vaga.",
    )


class ConquistaResponse(BaseModel):
    """Uma conquista do banco de conquistas na resposta da API."""

    texto: str = Field(description="Texto da conquista.")
    origem: OrigemConquistaSchema = Field(description="Origem da conquista.")


class ConquistasParecidasRequest(BaseModel):
    """Texto de uma conquista nova e as conquistas que a tela já tem na experiência."""

    texto: str = Field(description="Texto da conquista nova.")
    conquistas: list[str] = Field(default_factory=list, description="Conquistas já presentes na experiência.")

    def to_dto(self) -> VerificarConquistasParecidasInputDto:
        return VerificarConquistasParecidasInputDto(texto=self.texto, conquistas=tuple(self.conquistas))


class ConquistaAprovadaRequest(BaseModel):
    """Conquista aprovada pelo candidato a partir de uma pergunta sobre a vaga (JOB-0043)."""

    texto: str = Field(description="Texto da conquista, já revisado pelo candidato.")


class ConquistasParecidasResponse(BaseModel):
    """Conquistas existentes que se parecem com a conquista nova."""

    parecidas: list[str] = Field(description="Textos das conquistas parecidas, vazio quando não há.")


class ExperienciaProfissionalRequest(BaseModel):
    """Uma experiência profissional para criação/edição do perfil."""

    empresa: str = Field(description="Nome da empresa onde o profissional trabalhou.")
    cargo: str = Field(description="Cargo ou função exercida na empresa.")
    periodo: str = Field(description="Período de atuação (texto livre, ex: 'Jan 2020 - Dez 2022').")
    descricao: str = Field(
        default="",
        description="Descrição em texto livre (legada); os blocos abaixo a substituem.",
    )
    contexto: str = Field(default="", description="Contexto: a empresa, a área e o papel (opcional).")
    responsabilidades: list[str] = Field(
        default_factory=list,
        description="Principais responsabilidades da experiência (opcional).",
    )
    conquistas: list[ConquistaRequest] = Field(
        default_factory=list,
        description="Principais realizações: o banco de conquistas da experiência (opcional).",
    )
    skills: list[str] = Field(
        default_factory=list,
        description="Skills e tecnologias usadas na experiência (opcional).",
    )


class FormacaoAcademicaRequest(BaseModel):
    """Uma formação acadêmica para criação/edição do perfil."""

    instituicao: str = Field(description="Nome da instituição de ensino.")
    curso: str = Field(description="Nome do curso ou formação.")
    periodo: str = Field(description="Período de conclusão ou duração do curso.")


class CertificacaoRequest(BaseModel):
    """Uma certificação profissional para criação/edição do perfil."""

    nome: str = Field(description="Nome da certificação ou credencial.")
    instituicao: str = Field(description="Instituição ou organização emissora.")
    ano: str = Field(description="Ano de obtenção da certificação.")


class IdiomaRequest(BaseModel):
    """Um idioma e nível de proficiência para criação/edição do perfil."""

    idioma: str = Field(description="Nome do idioma (ex: 'Inglês', 'Espanhol').")
    nivel: str = Field(description="Nível de proficiência: BASICO, INTERMEDIARIO, AVANCADO, FLUENTE ou NATIVO.")


class PerfilEstruturadoRequest(BaseModel):
    """Payload para salvar ou atualizar o perfil estruturado de um usuário."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "perfil_identificador": "adriano.filho",
                "nome_completo": "Adriano Filho",
                "email": "adriano@email.com",
                "linkedin": "https://linkedin.com/in/adrianofilho",
                "resumo_profissional": "Desenvolvedor Python com foco em APIs e arquitetura limpa.",
                "experiencias": [
                    {
                        "empresa": "TechCorp",
                        "cargo": "Desenvolvedor Python",
                        "periodo": "Jan 2022 - Atual",
                        "descricao": "Desenvolvimento de APIs com FastAPI e integrações.",
                    }
                ],
                "formacoes": [
                    {
                        "instituicao": "Universidade Exemplo",
                        "curso": "Ciência da Computação",
                        "periodo": "2016 - 2020",
                    }
                ],
                "certificacoes": [
                    {
                        "nome": "AWS Certified Developer",
                        "instituicao": "Amazon Web Services",
                        "ano": "2023",
                    }
                ],
                "idiomas": [
                    {"idioma": "Inglês", "nivel": "FLUENTE"},
                    {"idioma": "Espanhol", "nivel": "INTERMEDIARIO"},
                ],
                "tecnologias": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            }
        }
    )

    perfil_identificador: str = Field(description="Identificador único do perfil de login.")
    nome_completo: str = Field(description="Nome completo do usuário.")
    email: str = Field(description="Endereço de e-mail do usuário.")
    linkedin: str = Field(description="URL do perfil no LinkedIn.")
    resumo_profissional: str = Field(description="Resumo livre da trajetória profissional.")
    experiencias: list[ExperienciaProfissionalRequest] = Field(
        default_factory=list,
        description="Lista de experiências profissionais.",
    )
    formacoes: list[FormacaoAcademicaRequest] = Field(
        default_factory=list,
        description="Lista de formações acadêmicas.",
    )
    certificacoes: list[CertificacaoRequest] = Field(
        default_factory=list,
        description="Lista de certificações.",
    )
    idiomas: list[IdiomaRequest] = Field(
        default_factory=list,
        description="Lista de idiomas e níveis de proficiência.",
    )
    tecnologias: list[str] = Field(
        default_factory=list,
        description="Lista de tecnologias dominadas pelo usuário.",
    )



    def to_dto(self) -> SalvarPerfilEstruturadoInputDto:
        return SalvarPerfilEstruturadoInputDto(
            perfil_identificador=self.perfil_identificador,
            nome_completo=self.nome_completo,
            email=self.email,
            linkedin=self.linkedin,
            resumo_profissional=self.resumo_profissional,
            experiencias=tuple(
                ExperienciaProfissional(
                    empresa=exp.empresa,
                    cargo=exp.cargo,
                    periodo=exp.periodo,
                    descricao=exp.descricao,
                    conquistas=tuple(
                        Conquista(texto=c.texto, origem=OrigemConquista[c.origem]) for c in exp.conquistas
                    ),
                    contexto=exp.contexto,
                    responsabilidades=tuple(exp.responsabilidades),
                    skills=tuple(exp.skills),
                )
                for exp in self.experiencias
            ),
            formacoes=tuple(
                FormacaoAcademica(
                    instituicao=form.instituicao,
                    curso=form.curso,
                    periodo=form.periodo,
                )
                for form in self.formacoes
            ),
            certificacoes=tuple(
                Certificacao(
                    nome=cert.nome,
                    instituicao=cert.instituicao,
                    ano=cert.ano,
                )
                for cert in self.certificacoes
            ),
            idiomas=tuple(
                Idioma(
                    idioma=idi.idioma,
                    nivel=NivelIdioma[idi.nivel.upper()],
                )
                for idi in self.idiomas
            ),
            tecnologias=tuple(self.tecnologias),
        )


class PerfilImportarPdfRequest(BaseModel):
    """Payload para importar um rascunho de perfil a partir de um PDF."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pdf_base64": "JVBERi0xLjQgdGVzdA==",
            }
        }
    )

    pdf_base64: str = Field(description="Conteúdo do PDF do currículo codificado em base64.")

    def to_dto(self) -> ImportarPerfilDePdfInputDto:
        return ImportarPerfilDePdfInputDto(
            pdf_curriculo=base64.b64decode(self.pdf_base64.encode()),
        )


class ExperienciaProfissionalResponse(BaseModel):
    """Representação de uma experiência profissional na resposta da API."""

    empresa: str = Field(description="Nome da empresa onde o profissional trabalhou.")
    cargo: str = Field(description="Cargo ou função exercida na empresa.")
    periodo: str = Field(description="Período de atuação (texto livre).")
    descricao: str = Field(description="Descrição em texto livre (legada).")
    contexto: str = Field(default="", description="Contexto: a empresa, a área e o papel.")
    responsabilidades: list[str] = Field(default_factory=list, description="Principais responsabilidades.")
    conquistas: list[ConquistaResponse] = Field(
        default_factory=list,
        description="Principais realizações: o banco de conquistas da experiência.",
    )
    skills: list[str] = Field(default_factory=list, description="Skills e tecnologias da experiência.")


class FormacaoAcademicaResponse(BaseModel):
    """Representação de uma formação acadêmica na resposta da API."""

    instituicao: str = Field(description="Nome da instituição de ensino.")
    curso: str = Field(description="Nome do curso ou formação.")
    periodo: str = Field(description="Período de conclusão ou duração do curso.")


class CertificacaoResponse(BaseModel):
    """Representação de uma certificação profissional na resposta da API."""

    nome: str = Field(description="Nome da certificação ou credencial.")
    instituicao: str = Field(description="Instituição ou organização emissora.")
    ano: str = Field(description="Ano de obtenção da certificação.")


class IdiomaResponse(BaseModel):
    """Representação de um idioma na resposta da API."""

    idioma: str = Field(description="Nome do idioma.")
    nivel: str = Field(description="Nível de proficiência (BASICO, INTERMEDIARIO, AVANCADO, FLUENTE, NATIVO).")


class PerfilEstruturadoResponse(BaseModel):
    """Representação do perfil estruturado na resposta da API."""

    perfil_identificador: str | None = Field(
        default=None,
        description="Identificador único do perfil de login (None para rascunho importado).",
    )
    nome_completo: str = Field(description="Nome completo do usuário.")
    email: str = Field(description="Endereço de e-mail do usuário.")
    linkedin: str = Field(description="URL do perfil no LinkedIn.")
    resumo_profissional: str = Field(description="Resumo livre da trajetória profissional.")
    experiencias: list[ExperienciaProfissionalResponse] = Field(
        description="Lista de experiências profissionais.",
    )
    formacoes: list[FormacaoAcademicaResponse] = Field(
        description="Lista de formações acadêmicas.",
    )
    certificacoes: list[CertificacaoResponse] = Field(
        description="Lista de certificações.",
    )
    idiomas: list[IdiomaResponse] = Field(
        description="Lista de idiomas e níveis de proficiência.",
    )
    tecnologias: list[str] = Field(
        description="Lista de tecnologias dominadas pelo usuário.",
    )
    tecnologias_incluidas: list[str] = Field(
        default_factory=list,
        description="Tecnologias que as skills das experiências acrescentaram às gerais ao salvar.",
    )

    @classmethod
    def from_dto(
        cls,
        dto: PerfilEstruturado | DadosPerfilExtraidos,
        tecnologias_incluidas: tuple[str, ...] = (),
    ) -> PerfilEstruturadoResponse:
        return cls(
            perfil_identificador=getattr(dto, "perfil_identificador", None),
            nome_completo=dto.nome_completo,
            email=dto.email,
            linkedin=dto.linkedin,
            resumo_profissional=dto.resumo_profissional,
            experiencias=[
                ExperienciaProfissionalResponse(
                    empresa=exp.empresa,
                    cargo=exp.cargo,
                    periodo=exp.periodo,
                    descricao=exp.descricao,
                    contexto=exp.contexto,
                    responsabilidades=list(exp.responsabilidades),
                    conquistas=[
                        ConquistaResponse(texto=c.texto, origem=c.origem.name) for c in exp.conquistas
                    ],
                    skills=list(exp.skills),
                )
                for exp in dto.experiencias
            ],
            formacoes=[
                FormacaoAcademicaResponse(
                    instituicao=form.instituicao,
                    curso=form.curso,
                    periodo=form.periodo,
                )
                for form in dto.formacoes
            ],
            certificacoes=[
                CertificacaoResponse(
                    nome=cert.nome,
                    instituicao=cert.instituicao,
                    ano=cert.ano,
                )
                for cert in dto.certificacoes
            ],
            idiomas=[
                IdiomaResponse(
                    idioma=idi.idioma,
                    nivel=idi.nivel.name,
                )
                for idi in dto.idiomas
            ],
            tecnologias=list(dto.tecnologias),
            tecnologias_incluidas=list(tecnologias_incluidas),
        )
