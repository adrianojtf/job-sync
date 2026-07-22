"""Testes do caso de uso AdaptarCurriculoParaVaga.

Usa dublês de teste (fakes) para as portas, mantendo o teste isolado de
qualquer infraestrutura real (PDF, LLM, etc.), conforme Hexagonal Architecture.
"""
import pytest

from application.ports.ajustador_texto_port import AjustadorTextoPort
from application.ports.extrator_curriculo_port import ExtratorCurriculoPort
from application.ports.gerador_pdf_port import GeradorPdfPort
from application.use_cases.adaptar_curriculo_para_vaga import (
    AdaptarCurriculoParaVaga,
    SolicitacaoAdaptacao,
)
from domain.curriculo import Curriculo, SecaoCurriculo, TipoSecao


class ExtratorFake(ExtratorCurriculoPort):
    def __init__(self, curriculo_a_retornar: Curriculo):
        self._curriculo = curriculo_a_retornar
        self.recebeu_pdf: bytes | None = None

    def extrair(self, conteudo_pdf: bytes) -> Curriculo:
        self.recebeu_pdf = conteudo_pdf
        return self._curriculo


class AjustadorTextoFake(AjustadorTextoPort):
    def __init__(self):
        self.chamadas: list[tuple[TipoSecao, str, str]] = []

    def ajustar_secao(self, secao: SecaoCurriculo, descricao_vaga: str, idioma_alvo: str) -> SecaoCurriculo:
        self.chamadas.append((secao.tipo, descricao_vaga, idioma_alvo))
        return secao.com_novo_conteudo(f"[AJUSTADO-{idioma_alvo}] {secao.conteudo}")


class GeradorPdfFake(GeradorPdfPort):
    def __init__(self):
        self.curriculo_recebido: Curriculo | None = None

    def gerar(self, curriculo: Curriculo) -> bytes:
        self.curriculo_recebido = curriculo
        return b"%PDF-FAKE-CONTENT"


def _curriculo_exemplo() -> Curriculo:
    return Curriculo(
        nome_completo="Adriano João Teixeira Filho",
        email="adriano@example.com",
        linkedin="linkedin.com/in/adriano",
        secoes=(
            SecaoCurriculo(TipoSecao.TECNOLOGIAS, "Tecnologias", "Java, Go, Python"),
            SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Engenheiro backend."),
            SecaoCurriculo(TipoSecao.EXPERIENCIAS, "Experiências", "Starian - Eng. Software"),
            SecaoCurriculo(TipoSecao.FORMACAO, "Formação acadêmica", "Estácio - ADS"),
        ),
    )


class TestAdaptarCurriculoParaVaga:
    def test_extrai_ajusta_todas_as_secoes_e_gera_pdf(self):
        curriculo = _curriculo_exemplo()
        extrator = ExtratorFake(curriculo)
        ajustador = AjustadorTextoFake()
        gerador_pdf = GeradorPdfFake()
        caso_de_uso = AdaptarCurriculoParaVaga(extrator, ajustador, gerador_pdf)

        solicitacao = SolicitacaoAdaptacao(
            pdf_curriculo=b"conteudo-pdf-original",
            descricao_vaga="Vaga para Engenheiro de Software Python Sênior",
            idioma_alvo="pt",
            cargo_alvo="Engenheiro de Software Sênior",
            empresa_alvo="TechCorp",
        )

        resultado = caso_de_uso.executar(solicitacao)

        assert extrator.recebeu_pdf == b"conteudo-pdf-original"
        assert len(ajustador.chamadas) == 4
        assert all(chamada[1] == "Vaga para Engenheiro de Software Python Sênior" for chamada in ajustador.chamadas)
        assert all(chamada[2] == "pt" for chamada in ajustador.chamadas)
        assert resultado.pdf_bytes == b"%PDF-FAKE-CONTENT"
        assert resultado.nome_arquivo.valor.startswith("AdrianoJoaoTeixeiraFilho-")
        assert resultado.nome_arquivo.valor.endswith("-EngenheiroDeSoftwareSenior-Techcorp.pdf")

    def test_cada_secao_ajustada_e_repassada_ao_gerador_de_pdf(self):
        curriculo = _curriculo_exemplo()
        extrator = ExtratorFake(curriculo)
        ajustador = AjustadorTextoFake()
        gerador_pdf = GeradorPdfFake()
        caso_de_uso = AdaptarCurriculoParaVaga(extrator, ajustador, gerador_pdf)

        solicitacao = SolicitacaoAdaptacao(
            pdf_curriculo=b"pdf",
            descricao_vaga="vaga qualquer",
            idioma_alvo="en",
            cargo_alvo="Software Engineer",
            empresa_alvo="TechCorp",
        )

        caso_de_uso.executar(solicitacao)

        curriculo_gerado = gerador_pdf.curriculo_recebido
        secao_perfil = curriculo_gerado.obter_secao(TipoSecao.PERFIL)
        assert secao_perfil.conteudo == "[AJUSTADO-en] Engenheiro backend."

    def test_idioma_invalido_gera_erro(self):
        extrator = ExtratorFake(_curriculo_exemplo())
        caso_de_uso = AdaptarCurriculoParaVaga(extrator, AjustadorTextoFake(), GeradorPdfFake())

        solicitacao = SolicitacaoAdaptacao(
            pdf_curriculo=b"pdf",
            descricao_vaga="vaga",
            idioma_alvo="fr",
            cargo_alvo="Cargo",
            empresa_alvo="Empresa",
        )

        with pytest.raises(ValueError, match="idioma"):
            caso_de_uso.executar(solicitacao)

    def test_descricao_vaga_vazia_gera_erro(self):
        extrator = ExtratorFake(_curriculo_exemplo())
        caso_de_uso = AdaptarCurriculoParaVaga(extrator, AjustadorTextoFake(), GeradorPdfFake())

        solicitacao = SolicitacaoAdaptacao(
            pdf_curriculo=b"pdf",
            descricao_vaga="   ",
            idioma_alvo="pt",
            cargo_alvo="Cargo",
            empresa_alvo="Empresa",
        )

        with pytest.raises(ValueError, match="descrição da vaga"):
            caso_de_uso.executar(solicitacao)
