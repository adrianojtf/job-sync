"""Testes do caso de uso ImportarPerfilDePdf."""

import pytest

from jobsync.perfil_estruturado import DadosPerfilExtraidos, ExperienciaProfissional
from jobsync.perfil_estruturado.domain.estruturar_experiencia_service import EstruturarExperienciaService
from jobsync.perfil_estruturado.domain.extrator_perfil_estruturado_port import ExtratorPerfilEstruturadoPort
from jobsync.perfil_estruturado.service_layer.importar_perfil_de_pdf import (
    ImportarPerfilDePdf,
    ImportarPerfilDePdfInputDto,
)


class ExtratorFake(ExtratorPerfilEstruturadoPort):
    def __init__(self, dados: DadosPerfilExtraidos):
        self._dados = dados
        self.recebeu_pdf: bytes | None = None

    def extrair(self, pdf_bytes: bytes) -> DadosPerfilExtraidos:
        self.recebeu_pdf = pdf_bytes
        return self._dados


def _dados_extraidos() -> DadosPerfilExtraidos:
    return DadosPerfilExtraidos(
        nome_completo="Fulano de Tal",
        email="fulano@example.com",
        linkedin="linkedin.com/in/fulano",
        resumo_profissional="Resumo.",
        experiencias=(),
        formacoes=(),
        certificacoes=(),
        idiomas=(),
        tecnologias=(),
    )


class TestImportarPerfilDePdf:
    def test_repassa_resultado_do_extrator(self):
        dados = _dados_extraidos()
        extrator = ExtratorFake(dados)
        use_case = ImportarPerfilDePdf(extrator=extrator)

        resultado = use_case.executar(ImportarPerfilDePdfInputDto(pdf_curriculo=b"conteudo-pdf"))

        assert resultado == dados
        assert extrator.recebeu_pdf == b"conteudo-pdf"

    def test_pdf_vazio_gera_erro(self):
        use_case = ImportarPerfilDePdf(extrator=ExtratorFake(_dados_extraidos()))

        with pytest.raises(ValueError, match="PDF"):
            use_case.executar(ImportarPerfilDePdfInputDto(pdf_curriculo=b""))


class TestImportarPerfilDePdfComBlocos:
    def test_estrutura_cada_experiencia_na_ordem_original(self):
        dados = DadosPerfilExtraidos(
            nome_completo="Fulano",
            email="fulano@example.com",
            linkedin="",
            resumo_profissional="",
            experiencias=tuple(
                ExperienciaProfissional(
                    empresa=f"Empresa {n}", cargo="Dev", periodo="2024", descricao=f"Technologies: Tec{n}"
                )
                for n in range(6)
            ),
            formacoes=(),
            certificacoes=(),
            idiomas=(),
            tecnologias=(),
        )
        use_case = ImportarPerfilDePdf(extrator=ExtratorFake(dados), estruturador=EstruturarExperienciaService(None))

        resultado = use_case.executar(ImportarPerfilDePdfInputDto(pdf_curriculo=b"pdf"))

        assert [e.empresa for e in resultado.experiencias] == [f"Empresa {n}" for n in range(6)]
        assert [e.skills for e in resultado.experiencias] == [(f"Tec{n}",) for n in range(6)]
        assert all(e.descricao == "" for e in resultado.experiencias)

    def test_sem_estruturador_devolve_as_experiencias_como_extraidas(self):
        dados = _dados_extraidos()
        use_case = ImportarPerfilDePdf(extrator=ExtratorFake(dados))

        assert use_case.executar(ImportarPerfilDePdfInputDto(pdf_curriculo=b"pdf")) == dados
