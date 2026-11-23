from datetime import datetime, timezone

from jobsync.curriculo import (
    AjusteTecnologia,
    CategoriaCompetencia,
    EquivalenciaTecnologia,
    ExperienciaAdaptada,
    RascunhoCurriculoAdaptado,
    SecaoCurriculo,
    TipoSecao,
)
from jobsync.curriculo_adaptado.domain.curriculo_adaptado import CurriculoAdaptado
from jobsync.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)

AGORA = datetime(2026, 11, 23, 12, 0, tzinfo=timezone.utc)
DEPOIS = datetime(2026, 11, 24, 9, 30, tzinfo=timezone.utc)


def analise_vaga() -> AnaliseVaga:
    return AnaliseVaga(
        requisitos=(
            RequisitoTecnico(
                nome="Java",
                categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
                tipo=TipoRequisitoTecnico.EXPLICITO,
                origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
            ),
            RequisitoTecnico(
                nome="Code review",
                categoria=CategoriaRequisitoTecnico.METODOLOGIA,
                tipo=TipoRequisitoTecnico.IMPLICITO,
                origem=OrigemRequisitoTecnico.INTERPRETACAO,
            ),
        ),
        ambiguidade=("Desejável Kafka",),
        texto_original="Vaga Java com code review.",
    )


def rascunho() -> RascunhoCurriculoAdaptado:
    return RascunhoCurriculoAdaptado(
        nome_completo="Ana Souza",
        email="ana@ex.com",
        linkedin="linkedin.com/in/ana",
        secoes=(
            SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Engenheira backend."),
            SecaoCurriculo(TipoSecao.FORMACAO, "Formação", "ADS — Estácio"),
        ),
        experiencias=(
            ExperienciaAdaptada(
                cargo="Dev",
                empresa="TechCorp",
                periodo="2024 - Atual",
                conquistas=("Criei APIs.", "Reduzi custos em 30%."),
                contexto="Plataforma de pagamentos.",
            ),
        ),
        titulo_experiencias="Experiências",
        competencias=(
            CategoriaCompetencia("Linguagens", ("Java", "Python")),
            CategoriaCompetencia("Bancos de Dados", ("SQL",)),
        ),
        titulo_competencias="Competências",
        ajustes_tecnologia=(
            AjusteTecnologia(0, EquivalenciaTecnologia(original="React", alvo="Angular")),
        ),
    )


def curriculo_adaptado(**sobrescritas) -> CurriculoAdaptado:
    valores = {
        "id": "adaptado-1",
        "perfil_identificador": "ana",
        "nome_referencia": "Ana_Souza_Dev_TechCorp.pdf",
        "cargo_alvo": "Engenheira de Software",
        "empresa_alvo": "TechCorp",
        "idioma_alvo": "pt",
        "descricao_vaga": "Vaga Java com code review.",
        "analise_vaga": analise_vaga(),
        "rascunho": rascunho(),
        "criado_em": AGORA,
        "atualizado_em": AGORA,
    }
    valores.update(sobrescritas)
    return CurriculoAdaptado(**valores)
