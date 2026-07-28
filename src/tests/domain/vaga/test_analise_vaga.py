"""Testes de domínio para a análise de descrição de vaga."""

import pytest

from domain.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)


def test_requisito_tecnico_e_analise_vaga_podem_ser_instanciados_e_sao_imutaveis() -> None:
    requisito = RequisitoTecnico(
        nome="Python",
        categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
        tipo=TipoRequisitoTecnico.EXPLICITO,
        origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
    )

    analise = AnaliseVaga(
        requisitos=(requisito,),
        ambiguidade=("Necessário experiência com docker ou kubernetes",),
        texto_original="Vaga para engenheiro de software com experiência em Python e Docker.",
    )

    assert analise.texto_original.startswith("Vaga para engenheiro")
    assert analise.requisitos[0].nome == "Python"
    assert analise.ambiguidade[0].startswith("Necessário experiência")

    with pytest.raises(Exception):
        analise.texto_original = "modificado"

    with pytest.raises(Exception):
        requisito.nome = "Java"


def test_analise_vaga_ja_nao_aceita_texto_original_vazio() -> None:
    requisito = RequisitoTecnico(
        nome="Python",
        categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
        tipo=TipoRequisitoTecnico.EXPLICITO,
        origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
    )

    with pytest.raises(ValueError, match="texto original"):
        AnaliseVaga(requisitos=(requisito,), ambiguidade=(), texto_original="   ")


def test_requisito_tecnico_nao_aceita_nome_vazio() -> None:
    with pytest.raises(ValueError, match="nome do requisito técnico"):
        RequisitoTecnico(
            nome="",
            categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
            tipo=TipoRequisitoTecnico.EXPLICITO,
            origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
        )
