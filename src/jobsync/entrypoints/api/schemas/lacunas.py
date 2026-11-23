"""Schemas Pydantic das perguntas de elucidação sobre as lacunas da vaga (JOB-0043)."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from jobsync.curriculo.domain.lacuna_da_vaga import LacunaDaVaga


class LacunasRequest(BaseModel):
    """Vaga a comparar com o perfil estruturado do usuário."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "perfil_identificador": "adriano",
                "descricao_vaga": "Atuar junto ao cliente e construir MVPs.",
                "cargo_alvo": "Forward Deployed Engineer",
                "idioma_alvo": "pt",
            }
        }
    )

    perfil_identificador: str = Field(min_length=1, description="Identificador do perfil estruturado a comparar com a vaga.")
    descricao_vaga: str = Field(description="Texto completo da descrição da vaga.")
    cargo_alvo: str = Field(default="", description="Título da vaga (cargo-alvo).")
    idioma_alvo: str = Field(default="pt", description="Idioma de destino do currículo adaptado.")


class LacunaResponse(BaseModel):
    """Um tema da vaga que o perfil não sustenta e a pergunta feita ao candidato."""

    tema: str = Field(description="Tema da vaga sem sustentação no perfil.")
    pergunta: str = Field(description="Pergunta fechada que o candidato responde com Sim ou Não.")


class LacunasResponse(BaseModel):
    """Até 5 lacunas, do tema mais central ao menos central; vazio quando não há o que perguntar."""

    lacunas: list[LacunaResponse] = Field(description="Lacunas identificadas, vazio quando não há.")

    @classmethod
    def from_dto(cls, lacunas: tuple[LacunaDaVaga, ...]) -> LacunasResponse:
        return cls(lacunas=[LacunaResponse(tema=lacuna.tema, pergunta=lacuna.pergunta) for lacuna in lacunas])


class ConquistaRascunhoRequest(BaseModel):
    """Resposta "Sim" do candidato a uma pergunta: o caso e a experiência em que aconteceu."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "perfil_identificador": "adriano",
                "tema": "Construção de MVPs",
                "pergunta": "Você já construiu um MVP do zero?",
                "caso": "Montei o MVP de pagamentos em 6 semanas junto ao cliente.",
                "experiencia_indice": 0,
                "idioma_alvo": "pt",
            }
        }
    )

    perfil_identificador: str = Field(min_length=1, description="Identificador do perfil estruturado.")
    tema: str = Field(description="Tema da lacuna respondida.")
    pergunta: str = Field(description="Pergunta que o candidato respondeu com Sim.")
    caso: str = Field(description="O que o candidato fez, para quem e o resultado, se houver.")
    experiencia_indice: int = Field(ge=0, description="Posição da experiência do perfil em que isso aconteceu.")
    idioma_alvo: str = Field(default="pt", description="Idioma em que a conquista deve ser escrita.")


class ConquistaRascunhoResponse(BaseModel):
    """Conquista redigida pela IA, para o candidato revisar antes de salvar no banco."""

    texto: str = Field(description="Texto da conquista redigida; nada foi salvo.")
