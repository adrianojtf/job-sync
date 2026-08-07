"""Testes do Domain Service CalcularAtsScore."""

from jobsync.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from jobsync.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from jobsync.ats_score.domain.calcular_ats_score_service import CalcularAtsScore


def _requisito(nome: str, tipo: TipoRequisitoTecnico = TipoRequisitoTecnico.EXPLICITO) -> RequisitoTecnico:
    return RequisitoTecnico(
        nome=nome,
        categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
        tipo=tipo,
        origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
    )


def _curriculo(conteudo_tecnologias: str) -> Curriculo:
    return Curriculo(
        nome_completo="Fulano de Tal",
        email="fulano@example.com",
        linkedin="linkedin.com/in/fulano",
        secoes=(
            SecaoCurriculo(tipo=TipoSecao.TECNOLOGIAS, titulo="Tecnologias", conteudo=conteudo_tecnologias),
        ),
    )


class TestCalcularAtsScore:
    def test_cobertura_total_gera_nota_100_sem_faltantes(self):
        analise = AnaliseVaga(
            requisitos=(_requisito("Python"), _requisito("Docker")),
            ambiguidade=(),
            texto_original="vaga",
        )
        curriculo = _curriculo("Python, Docker, AWS")

        resultado = CalcularAtsScore().executar(curriculo, analise)

        assert resultado.nota == 100
        assert resultado.requisitos_faltantes == ()

    def test_cobertura_parcial_gera_nota_proporcional_e_faltantes_corretos(self):
        docker = _requisito("Docker")
        analise = AnaliseVaga(
            requisitos=(_requisito("Python"), docker),
            ambiguidade=(),
            texto_original="vaga",
        )
        curriculo = _curriculo("Python e AWS")

        resultado = CalcularAtsScore().executar(curriculo, analise)

        assert resultado.nota == 50
        assert resultado.requisitos_faltantes == (docker,)

    def test_sem_requisitos_explicitos_gera_nota_100(self):
        analise = AnaliseVaga(
            requisitos=(_requisito("Django", tipo=TipoRequisitoTecnico.IMPLICITO),),
            ambiguidade=(),
            texto_original="vaga",
        )
        curriculo = _curriculo("Python")

        resultado = CalcularAtsScore().executar(curriculo, analise)

        assert resultado.nota == 100
        assert resultado.requisitos_faltantes == ()

    def test_comparacao_de_nomes_e_case_insensitive(self):
        analise = AnaliseVaga(
            requisitos=(_requisito("Python"),),
            ambiguidade=(),
            texto_original="vaga",
        )
        curriculo = _curriculo("python e django")

        resultado = CalcularAtsScore().executar(curriculo, analise)

        assert resultado.nota == 100
        assert resultado.requisitos_faltantes == ()
