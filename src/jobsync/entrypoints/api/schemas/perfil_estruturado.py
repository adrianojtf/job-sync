"""Schemas Pydantic para endpoints do domínio de perfil estruturado."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from jobsync.perfil_estruturado.domain.perfil_estruturado import (
    Certificacao,
    ExperienciaProfissional,
    FormacaoAcademica,
    Idioma,
    NivelIdioma,
    PerfilEstruturado,
)
from jobsync.perfil_estruturado.service_layer.salvar_perfil_estruturado.dtos import (
    SalvarPerfilEstruturadoInputDto,
)


class ExperienciaProfissionalRequest(BaseModel):
    """Uma experiência profissional para criação/edição do perfil."""

    empresa: str = Field(description="Nome da empresa onde o profissional trabalhou.")
    cargo: str = Field(description="Cargo ou função exercida na empresa.")
    periodo: str = Field(description="Período de atuação (texto livre, ex: 'Jan 2020 - Dez 2022').")
    descricao: str = Field(description="Descrição das atividades e responsabilidades do cargo.")


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


class ExperienciaProfissionalResponse(BaseModel):
    """Representação de uma experiência profissional na resposta da API."""

    empresa: str = Field(description="Nome da empresa onde o profissional trabalhou.")
    cargo: str = Field(description="Cargo ou função exercida na empresa.")
    periodo: str = Field(description="Período de atuação (texto livre).")
    descricao: str = Field(description="Descrição das atividades e responsabilidades do cargo.")


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

    perfil_identificador: str = Field(description="Identificador único do perfil de login.")
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

    @classmethod
    def from_dto(cls, dto: PerfilEstruturado) -> PerfilEstruturadoResponse:
        return cls(
            perfil_identificador=dto.perfil_identificador,
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
        )
