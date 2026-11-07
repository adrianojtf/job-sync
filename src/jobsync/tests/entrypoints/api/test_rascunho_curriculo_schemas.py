"""Testes dos schemas do rascunho do currículo adaptado (JOB-0033)."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from jobsync.curriculo import (
    ExperienciaAdaptada,
    RascunhoCurriculoAdaptado,
    SecaoCurriculo,
    TipoSecao,
)
from jobsync.entrypoints.api.schemas.curriculo import (
    ExperienciaAdaptadaSchema,
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
            experiencias=[ExperienciaAdaptadaSchema()],
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


def _rascunho_schema(**experiencia) -> RascunhoCurriculoAdaptadoSchema:
    return RascunhoCurriculoAdaptadoSchema.model_validate(
        {
            "nome_completo": "Ana Souza",
            "secoes": [],
            "experiencias": [{"cargo": "Dev", "empresa": "TechCorp", **experiencia}],
        }
    )


class TestExperienciaDoRascunhoComConquistasEContexto:
    def test_from_domain_expoe_conquistas_e_contexto_em_campos_separados(self):
        rascunho = RascunhoCurriculoAdaptado(
            nome_completo="Ana Souza",
            email="",
            linkedin="",
            secoes=(),
            experiencias=(
                ExperienciaAdaptada(
                    cargo="Dev",
                    empresa="TechCorp",
                    periodo="2024",
                    conquistas=("Criei APIs.", "Reduzi custos."),
                    contexto="Empresa de pagamentos.",
                ),
            ),
        )

        experiencia = RascunhoCurriculoAdaptadoSchema.from_domain(rascunho).experiencias[0]

        assert experiencia.conquistas == ["Criei APIs.", "Reduzi custos."]
        assert experiencia.contexto == "Empresa de pagamentos."
        assert "descricao" not in experiencia.model_dump()

    def test_ida_e_volta_preserva_conquistas_e_contexto(self):
        rascunho = RascunhoCurriculoAdaptado(
            nome_completo="Ana Souza",
            email="",
            linkedin="",
            secoes=(),
            experiencias=(
                ExperienciaAdaptada(
                    cargo="Dev",
                    empresa="TechCorp",
                    periodo="2024",
                    conquistas=("Criei APIs.",),
                    contexto="Empresa de pagamentos.",
                ),
            ),
        )

        assert RascunhoCurriculoAdaptadoSchema.from_domain(rascunho).to_domain() == rascunho

    def test_to_domain_usa_conquistas_e_contexto_editados_e_descarta_conquistas_em_branco(self):
        rascunho = _rascunho_schema(
            conquistas=["  Criei APIs. ", "", "  "], contexto=" Empresa de pagamentos. "
        ).to_domain()

        assert rascunho.experiencias == (
            ExperienciaAdaptada(
                cargo="Dev",
                empresa="TechCorp",
                periodo="",
                conquistas=("Criei APIs.",),
                contexto="Empresa de pagamentos.",
            ),
        )

    def test_to_domain_aceita_experiencia_so_com_contexto(self):
        rascunho = _rascunho_schema(contexto="Empresa de pagamentos.").to_domain()

        assert rascunho.experiencias[0].conquistas == ()
        assert rascunho.experiencias[0].contexto == "Empresa de pagamentos."

    def test_descricao_legada_e_rejeitada_em_vez_de_ignorada(self):
        with pytest.raises(ValidationError, match="descricao"):
            _rascunho_schema(descricao="- Criei APIs.")


class TestExperienciaAdaptadaSchema:
    def test_to_domain_apara_e_descarta_conquistas_em_branco(self):
        schema = ExperienciaAdaptadaSchema(
            cargo=" Dev ", empresa="TechCorp", periodo="2024", conquistas=[" A. ", " "], contexto=" C. "
        )

        assert schema.to_domain() == ExperienciaAdaptada(
            cargo="Dev", empresa="TechCorp", periodo="2024", conquistas=("A.",), contexto="C."
        )

    def test_to_domain_sem_nenhum_conteudo_gera_erro(self):
        with pytest.raises(ValueError, match="conquista ou o contexto"):
            ExperienciaAdaptadaSchema(cargo="Dev", empresa="TechCorp").to_domain()

    def test_to_domain_sem_empresa_gera_erro(self):
        with pytest.raises(ValueError, match="empresa"):
            ExperienciaAdaptadaSchema(cargo="Dev", empresa="", conquistas=["A."]).to_domain()

    def test_from_domain_copia_todos_os_campos(self):
        experiencia = ExperienciaAdaptada(
            cargo="Dev", empresa="TechCorp", periodo="2024", conquistas=("A.", "B."), contexto="C."
        )

        schema = ExperienciaAdaptadaSchema.from_domain(experiencia)

        assert schema.model_dump() == {
            "cargo": "Dev",
            "empresa": "TechCorp",
            "periodo": "2024",
            "conquistas": ["A.", "B."],
            "contexto": "C.",
        }

    def test_campo_desconhecido_e_rejeitado(self):
        with pytest.raises(ValidationError, match="descricao"):
            ExperienciaAdaptadaSchema.model_validate(
                {"cargo": "Dev", "empresa": "TechCorp", "descricao": "texto antigo"}
            )
