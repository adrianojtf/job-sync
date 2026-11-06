"""Testes do schema AnaliseVagaSchema (ida e volta do domínio)."""

from jobsync.entrypoints.api.schemas.vaga import AnaliseVagaSchema
from jobsync.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)


def _analise() -> AnaliseVaga:
    return AnaliseVaga(
        requisitos=(
            RequisitoTecnico(
                nome="Java",
                categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
                tipo=TipoRequisitoTecnico.EXPLICITO,
                origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
            ),
            RequisitoTecnico(
                nome="Comunicação",
                categoria=CategoriaRequisitoTecnico.HABILIDADE,
                tipo=TipoRequisitoTecnico.IMPLICITO,
                origem=OrigemRequisitoTecnico.INTERPRETACAO,
            ),
        ),
        ambiguidade=("Desejável Kafka",),
        texto_original="Vaga Java com Kafka",
    )


class TestAnaliseVagaSchema:
    def test_from_domain_usa_os_nomes_dos_enums(self):
        schema = AnaliseVagaSchema.from_domain(_analise())

        assert schema.requisitos[0].model_dump() == {
            "nome": "Java",
            "categoria": "TECNOLOGIA",
            "tipo": "EXPLICITO",
            "origem": "DESCRICAO_VAGA",
        }
        assert schema.ambiguidade == ["Desejável Kafka"]
        assert schema.texto_original == "Vaga Java com Kafka"

    def test_ida_e_volta_preserva_a_analise(self):
        analise = _analise()

        assert AnaliseVagaSchema.from_domain(analise).to_domain() == analise

    def test_origem_e_ambiguidade_sao_opcionais_na_entrada(self):
        schema = AnaliseVagaSchema.model_validate(
            {
                "requisitos": [{"nome": "Go", "categoria": "TECNOLOGIA", "tipo": "EXPLICITO"}],
                "texto_original": "Vaga Go",
            }
        )

        analise = schema.to_domain()

        assert analise.requisitos[0].origem == OrigemRequisitoTecnico.DESCONHECIDA
        assert analise.ambiguidade == ()
