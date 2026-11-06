"""Testes dos schemas do rascunho do currículo adaptado (JOB-0033)."""

from __future__ import annotations

from datetime import date

import pytest

from jobsync.curriculo import (
    ExperienciaAdaptada,
    RascunhoCurriculoAdaptado,
    SecaoCurriculo,
    TipoSecao,
)
from jobsync.entrypoints.api.schemas.curriculo import (
    ExperienciaRascunhoSchema,
    GerarPdfCurriculoRevisadoRequest,
    RascunhoCurriculoAdaptadoSchema,
    SecaoRascunhoSchema,
)


def _rascunho_dominio() -> RascunhoCurriculoAdaptado:
    return RascunhoCurriculoAdaptado(
        nome_completo="Ana Souza",
        email="ana@ex.com",
        linkedin="linkedin.com/in/ana",
        secoes=(SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Resumo."),),
        experiencias=(
            ExperienciaAdaptada(
                cargo="Dev", empresa="TechCorp", periodo="2024", conquistas=("APIs.",)
            ),
        ),
        titulo_experiencias="Experience",
    )


class TestRascunhoCurriculoAdaptadoSchema:
    def test_ida_e_volta_preserva_o_rascunho(self):
        rascunho = _rascunho_dominio()

        schema = RascunhoCurriculoAdaptadoSchema.from_domain(rascunho)

        assert schema.secoes[0].tipo == "PERFIL"
        assert schema.to_domain() == rascunho

    def test_descricao_da_experiencia_mostra_uma_conquista_por_linha_sem_marcadores(self):
        rascunho = RascunhoCurriculoAdaptado(
            nome_completo="Ana Souza",
            email="",
            linkedin="",
            secoes=(),
            experiencias=(
                ExperienciaAdaptada(
                    cargo="Dev",
                    empresa="TechCorp",
                    periodo="",
                    conquistas=("Criei APIs.", "Reduzi custos."),
                ),
            ),
        )

        schema = RascunhoCurriculoAdaptadoSchema.from_domain(rascunho)

        assert schema.experiencias[0].descricao == "Criei APIs.\nReduzi custos."
        assert schema.to_domain() == rascunho

    def test_rascunho_de_fonte_pdf_tem_experiencias_nulas(self):
        rascunho = RascunhoCurriculoAdaptado(
            nome_completo="Ana Souza",
            email="",
            linkedin="",
            secoes=(SecaoCurriculo(TipoSecao.EXPERIENCIAS, "Experiências", "Texto livre."),),
        )

        schema = RascunhoCurriculoAdaptadoSchema.from_domain(rascunho)

        assert schema.experiencias is None
        assert schema.to_domain() == rascunho

    def test_to_domain_descarta_secoes_e_experiencias_em_branco(self):
        schema = RascunhoCurriculoAdaptadoSchema(
            nome_completo="Ana Souza",
            secoes=[
                SecaoRascunhoSchema(tipo="PERFIL", titulo="Perfil", conteudo="Resumo."),
                SecaoRascunhoSchema(tipo="IDIOMAS", titulo="Idiomas", conteudo="  "),
            ],
            experiencias=[ExperienciaRascunhoSchema()],
        )

        rascunho = schema.to_domain()

        assert [secao.tipo for secao in rascunho.secoes] == [TipoSecao.PERFIL]
        assert rascunho.experiencias == ()

    def test_to_domain_com_rascunho_invalido_gera_erro(self):
        schema = RascunhoCurriculoAdaptadoSchema(
            nome_completo="",
            secoes=[SecaoRascunhoSchema(tipo="PERFIL", titulo="Perfil", conteudo="Resumo.")],
        )

        with pytest.raises(ValueError, match="nome completo"):
            schema.to_domain()


class TestGerarPdfCurriculoRevisadoRequest:
    def test_to_dto_converte_rascunho_e_dados_da_vaga(self):
        request = GerarPdfCurriculoRevisadoRequest(
            rascunho=RascunhoCurriculoAdaptadoSchema.from_domain(_rascunho_dominio()),
            idioma_alvo="en",
            cargo_alvo="Engenheiro",
            empresa_alvo="TechCorp",
            data_referencia=date(2026, 11, 6),
        )

        dto = request.to_dto()

        assert dto.rascunho == _rascunho_dominio()
        assert dto.idioma_alvo == "en"
        assert dto.cargo_alvo == "Engenheiro"
        assert dto.empresa_alvo == "TechCorp"
        assert dto.data_referencia == date(2026, 11, 6)
