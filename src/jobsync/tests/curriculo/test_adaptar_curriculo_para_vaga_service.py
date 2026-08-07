"""Testes do caso de uso AdaptarCurriculoParaVaga.

Usa dublês de teste (fakes) para as portas, mantendo o teste isolado de
qualquer infraestrutura real (PDF, LLM, etc.), conforme Hexagonal Architecture.
"""
import pytest

from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga import (
    AdaptarCurriculoParaVaga,
    AdaptarCurriculoParaVagaInputDto,
)
from jobsync.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from jobsync.curriculo.domain.ajustador_texto_port import AjustadorTextoPort
from jobsync.curriculo.domain.extrator_curriculo_port import ExtratorCurriculoPort
from jobsync.curriculo.domain.gerador_pdf_port import GeradorPdfPort
from jobsync.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from jobsync.vaga.domain.job_description_analyzer_port import JobDescriptionAnalyzerPort


class ExtratorFake(ExtratorCurriculoPort):
    def __init__(self, curriculo_a_retornar: Curriculo):
        self._curriculo = curriculo_a_retornar
        self.recebeu_pdf: bytes | None = None

    def extrair(self, conteudo_pdf: bytes) -> Curriculo:
        self.recebeu_pdf = conteudo_pdf
        return self._curriculo


class AjustadorTextoFake(AjustadorTextoPort):
    def __init__(self):
        self.chamadas: list[tuple[TipoSecao, str, str, AnaliseVaga]] = []

    def ajustar_secao(
        self,
        secao: SecaoCurriculo,
        descricao_vaga: str,
        idioma_alvo: str,
        analise_vaga: AnaliseVaga,
    ) -> SecaoCurriculo:
        self.chamadas.append((secao.tipo, descricao_vaga, idioma_alvo, analise_vaga))
        return secao.com_novo_conteudo(f"[AJUSTADO-{idioma_alvo}] {secao.conteudo}")


class JobDescriptionAnalyzerFake(JobDescriptionAnalyzerPort):
    def __init__(self, analise: AnaliseVaga):
        self.analise = analise
        self.recebeu_descricao: str | None = None

    def analisar(self, descricao_vaga: str) -> AnaliseVaga:
        self.recebeu_descricao = descricao_vaga
        return self.analise


class GeradorPdfFake(GeradorPdfPort):
    def __init__(self):
        self.curriculo_recebido: Curriculo | None = None
        self.idioma_recebido: str | None = None

    def gerar(self, curriculo: Curriculo, idioma_alvo: str) -> bytes:
        self.curriculo_recebido = curriculo
        self.idioma_recebido = idioma_alvo
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
        analisador_vaga = JobDescriptionAnalyzerFake(
            AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="Vaga para Engenheiro de Software Python Sênior")
        )
        ajustador = AjustadorTextoFake()
        gerador_pdf = GeradorPdfFake()
        caso_de_uso = AdaptarCurriculoParaVaga(
            extrator,
            analisador_vaga,
            ajustador,
            gerador_pdf,
        )

        input_dto = AdaptarCurriculoParaVagaInputDto(
            pdf_curriculo=b"conteudo-pdf-original",
            descricao_vaga="Vaga para Engenheiro de Software Python Sênior",
            idioma_alvo="pt",
            cargo_alvo="Engenheiro de Software Sênior",
            empresa_alvo="TechCorp",
        )

        resultado = caso_de_uso.executar(input_dto)

        assert extrator.recebeu_pdf == b"conteudo-pdf-original"
        assert len(ajustador.chamadas) == 4
        assert all(chamada[1] == "Vaga para Engenheiro de Software Python Sênior" for chamada in ajustador.chamadas)
        assert all(chamada[2] == "pt" for chamada in ajustador.chamadas)
        assert resultado.pdf_bytes == b"%PDF-FAKE-CONTENT"
        assert gerador_pdf.idioma_recebido == "pt"
        assert resultado.nome_arquivo.valor.startswith("AdrianoJoaoTeixeiraFilho-")
        assert resultado.nome_arquivo.valor.endswith("-EngenheiroDeSoftwareSenior-Techcorp.pdf")

    def test_analisa_vaga_e_repassa_analise_para_ajustador_texto(self):
        curriculo = _curriculo_exemplo()
        extrator = ExtratorFake(curriculo)
        analise = AnaliseVaga(
            requisitos=(
                RequisitoTecnico(
                    nome="Python",
                    categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
                    tipo=TipoRequisitoTecnico.EXPLICITO,
                    origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
                ),
            ),
            ambiguidade=("Desejável conhecimento em Django",),
            texto_original="Vaga para Engenheiro de Software Python Sênior",
        )
        analisador_vaga = JobDescriptionAnalyzerFake(analise)
        ajustador = AjustadorTextoFake()
        gerador_pdf = GeradorPdfFake()
        caso_de_uso = AdaptarCurriculoParaVaga(
            extrator,
            analisador_vaga,
            ajustador,
            gerador_pdf,
        )

        input_dto = AdaptarCurriculoParaVagaInputDto(
            pdf_curriculo=b"conteudo-pdf-original",
            descricao_vaga="Vaga para Engenheiro de Software Python Sênior",
            idioma_alvo="pt",
            cargo_alvo="Engenheiro de Software Sênior",
            empresa_alvo="TechCorp",
        )

        resultado = caso_de_uso.executar(input_dto)

        assert analisador_vaga.recebeu_descricao == input_dto.descricao_vaga
        assert len(ajustador.chamadas) == 4
        assert all(chamada[3] is analise for chamada in ajustador.chamadas)
        assert resultado.pdf_bytes == b"%PDF-FAKE-CONTENT"
        assert resultado.analise_vaga is analise

    def test_cada_secao_ajustada_e_repassada_ao_gerador_de_pdf(self):
        curriculo = _curriculo_exemplo()
        extrator = ExtratorFake(curriculo)
        analisador_vaga = JobDescriptionAnalyzerFake(
            AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga qualquer")
        )
        ajustador = AjustadorTextoFake()
        gerador_pdf = GeradorPdfFake()
        caso_de_uso = AdaptarCurriculoParaVaga(
            extrator,
            analisador_vaga,
            ajustador,
            gerador_pdf,
        )

        input_dto = AdaptarCurriculoParaVagaInputDto(
            pdf_curriculo=b"pdf",
            descricao_vaga="vaga qualquer",
            idioma_alvo="en",
            cargo_alvo="Software Engineer",
            empresa_alvo="TechCorp",
        )

        caso_de_uso.executar(input_dto)

        curriculo_gerado = gerador_pdf.curriculo_recebido
        secao_perfil = curriculo_gerado.obter_secao(TipoSecao.PERFIL)
        assert secao_perfil.conteudo == "[AJUSTADO-en] Engenheiro backend."
        assert gerador_pdf.idioma_recebido == "en"

    def test_idioma_invalido_gera_erro(self):
        extrator = ExtratorFake(_curriculo_exemplo())
        analisador_vaga = JobDescriptionAnalyzerFake(
            AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga")
        )
        caso_de_uso = AdaptarCurriculoParaVaga(
            extrator,
            analisador_vaga,
            AjustadorTextoFake(),
            GeradorPdfFake(),
        )

        input_dto = AdaptarCurriculoParaVagaInputDto(
            pdf_curriculo=b"pdf",
            descricao_vaga="vaga",
            idioma_alvo="fr",
            cargo_alvo="Cargo",
            empresa_alvo="Empresa",
        )

        with pytest.raises(ValueError, match="idioma"):
            caso_de_uso.executar(input_dto)

    def test_descricao_vaga_vazia_gera_erro(self):
        extrator = ExtratorFake(_curriculo_exemplo())
        analisador_vaga = JobDescriptionAnalyzerFake(
            AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga")
        )
        caso_de_uso = AdaptarCurriculoParaVaga(
            extrator,
            analisador_vaga,
            AjustadorTextoFake(),
            GeradorPdfFake(),
        )

        input_dto = AdaptarCurriculoParaVagaInputDto(
            pdf_curriculo=b"pdf",
            descricao_vaga="   ",
            idioma_alvo="pt",
            cargo_alvo="Cargo",
            empresa_alvo="Empresa",
        )

        with pytest.raises(ValueError, match="descrição da vaga"):
            caso_de_uso.executar(input_dto)

    def test_curriculo_pre_montado_pula_extracao_via_ia(self):
        curriculo = _curriculo_exemplo()
        extrator = ExtratorFake(curriculo)
        analisador_vaga = JobDescriptionAnalyzerFake(
            AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga qualquer")
        )
        caso_de_uso = AdaptarCurriculoParaVaga(
            extrator,
            analisador_vaga,
            AjustadorTextoFake(),
            GeradorPdfFake(),
        )

        input_dto = AdaptarCurriculoParaVagaInputDto(
            curriculo_pre_montado=curriculo,
            descricao_vaga="vaga qualquer",
            idioma_alvo="pt",
            cargo_alvo="Cargo",
            empresa_alvo="Empresa",
        )

        resultado = caso_de_uso.executar(input_dto)

        assert extrator.recebeu_pdf is None
        assert resultado.pdf_bytes == b"%PDF-FAKE-CONTENT"

    def test_sem_pdf_e_sem_curriculo_pre_montado_gera_erro(self):
        caso_de_uso = AdaptarCurriculoParaVaga(
            ExtratorFake(_curriculo_exemplo()),
            JobDescriptionAnalyzerFake(AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga")),
            AjustadorTextoFake(),
            GeradorPdfFake(),
        )

        input_dto = AdaptarCurriculoParaVagaInputDto(
            descricao_vaga="vaga", idioma_alvo="pt", cargo_alvo="Cargo", empresa_alvo="Empresa"
        )

        with pytest.raises(ValueError, match="PDF"):
            caso_de_uso.executar(input_dto)
