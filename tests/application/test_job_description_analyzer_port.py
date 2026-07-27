"""Testes de porta para o analisador de descrição de vaga."""

from application.ports.job_description_analyzer_port import JobDescriptionAnalyzerPort
from domain.analise_vaga import AnaliseVaga, RequisitoTecnico, TipoRequisitoTecnico, CategoriaRequisitoTecnico, OrigemRequisitoTecnico


class JobDescriptionAnalyzerFake(JobDescriptionAnalyzerPort):
    def analisar(self, descricao_vaga: str) -> AnaliseVaga:
        requisito = RequisitoTecnico(
            nome="Python",
            categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
            tipo=TipoRequisitoTecnico.EXPLICITO,
            origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
        )
        return AnaliseVaga(
            requisitos=(requisito,),
            ambiguidade=(),
            texto_original=descricao_vaga,
        )


def test_job_description_analyzer_port_eh_interface_pura() -> None:
    fake = JobDescriptionAnalyzerFake()
    analise = fake.analisar("Vaga com Python e Docker.")

    assert isinstance(analise, AnaliseVaga)
    assert analise.texto_original == "Vaga com Python e Docker."
