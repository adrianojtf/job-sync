"""Testes do caso de uso AdaptarCurriculoParaVaga.

Usa dublês de teste (fakes) para as portas, mantendo o teste isolado de
qualquer infraestrutura real (PDF, LLM, etc.), conforme Hexagonal Architecture.
"""
import pytest

from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga import (
    AdaptarCurriculoParaVaga,
    AdaptarCurriculoParaVagaInputDto,
)
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.dtos import (
    StatusAvaliacaoAutomatica,
)
from jobsync.curriculo import (
    AvaliacaoExperiencia,
    Curriculo,
    ExperienciaParaAvaliacao,
    SecaoCurriculo,
    TipoSecao,
)
from jobsync.curriculo.domain.ajustador_experiencia_port import AjustadorExperienciaPort
from jobsync.curriculo.domain.ajustador_texto_port import AjustadorTextoPort
from jobsync.curriculo.domain.avaliador_experiencia_port import AvaliadorExperienciaPort
from jobsync.curriculo.domain.extrator_curriculo_port import ExtratorCurriculoPort
from jobsync.shared_kernel.domain.score_avaliacao import ResultadoDimensaoAvaliacao
from jobsync.vaga import (
    AnaliseVaga,
    AvaliacaoDescricaoVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from jobsync.vaga.domain.avaliador_descricao_vaga_port import AvaliadorDescricaoVagaPort
from jobsync.vaga.domain.job_description_analyzer_port import JobDescriptionAnalyzerPort


class ExtratorFake(ExtratorCurriculoPort):
    def __init__(self, curriculo_a_retornar: Curriculo):
        self._curriculo = curriculo_a_retornar
        self.recebeu_pdf: bytes | None = None

    def extrair(self, conteudo_pdf: bytes) -> Curriculo:
        self.recebeu_pdf = conteudo_pdf
        return self._curriculo


class AjustadorTextoFake(AjustadorTextoPort):
    def __init__(self, eventos: list[str] | None = None):
        self.chamadas: list[tuple[TipoSecao, str, str, AnaliseVaga]] = []
        self._eventos = eventos

    def ajustar_secao(
        self,
        secao: SecaoCurriculo,
        descricao_vaga: str,
        idioma_alvo: str,
        analise_vaga: AnaliseVaga,
    ) -> SecaoCurriculo:
        self.chamadas.append((secao.tipo, descricao_vaga, idioma_alvo, analise_vaga))
        if self._eventos is not None:
            self._eventos.append("ajustar_secao")
        return secao.com_novo_conteudo(f"[AJUSTADO-{idioma_alvo}] {secao.conteudo}")


class JobDescriptionAnalyzerFake(JobDescriptionAnalyzerPort):
    def __init__(self, analise: AnaliseVaga):
        self.analise = analise
        self.recebeu_descricao: str | None = None

    def analisar(self, descricao_vaga: str) -> AnaliseVaga:
        self.recebeu_descricao = descricao_vaga
        return self.analise


class AvaliadorDescricaoVagaFake(AvaliadorDescricaoVagaPort):
    def __init__(
        self,
        avaliacao: AvaliacaoDescricaoVaga,
        erro: Exception | None = None,
        eventos: list[str] | None = None,
    ):
        self._avaliacao = avaliacao
        self._erro = erro
        self._eventos = eventos
        self.chamadas: list[str] = []

    def avaliar(self, descricao_vaga: str) -> AvaliacaoDescricaoVaga:
        self.chamadas.append(descricao_vaga)
        if self._eventos is not None:
            self._eventos.append("avaliar_vaga")
        if self._erro is not None:
            raise self._erro
        return self._avaliacao


class AjustadorExperienciaFake(AjustadorExperienciaPort):
    def __init__(self, eventos: list[str] | None = None):
        self.recebidas: list[ExperienciaParaAvaliacao] = []
        self._eventos = eventos

    def ajustar(
        self,
        experiencia: ExperienciaParaAvaliacao,
        descricao_vaga: str,
        idioma_alvo: str,
        analise_vaga: AnaliseVaga,
    ) -> ExperienciaParaAvaliacao:
        self.recebidas.append(experiencia)
        if self._eventos is not None:
            self._eventos.append("ajustar_experiencia")
        return ExperienciaParaAvaliacao(
            descricao=f"[AJUSTADA] {experiencia.descricao}",
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
        )


class AvaliadorExperienciaFake(AvaliadorExperienciaPort):
    def __init__(
        self,
        avaliacao: AvaliacaoExperiencia,
        erro: Exception | None = None,
        eventos: list[str] | None = None,
    ):
        self._avaliacao = avaliacao
        self._erro = erro
        self._eventos = eventos
        self.recebidas: list[ExperienciaParaAvaliacao] = []

    def avaliar(
        self,
        experiencia: ExperienciaParaAvaliacao,
        descricao_vaga: str,
    ) -> AvaliacaoExperiencia:
        self.recebidas.append(experiencia)
        if self._eventos is not None:
            self._eventos.append("avaliar_experiencia")
        if self._erro is not None:
            raise self._erro
        return self._avaliacao


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
    def test_extrai_e_ajusta_todas_as_secoes_em_um_rascunho(self):
        curriculo = _curriculo_exemplo()
        extrator = ExtratorFake(curriculo)
        analisador_vaga = JobDescriptionAnalyzerFake(
            AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="Vaga para Engenheiro de Software Python Sênior")
        )
        ajustador = AjustadorTextoFake()
        caso_de_uso = AdaptarCurriculoParaVaga(
            extrator,
            analisador_vaga,
            ajustador,
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
        assert resultado.rascunho.nome_completo == "Adriano João Teixeira Filho"
        assert resultado.rascunho.email == "adriano@example.com"
        assert len(resultado.rascunho.secoes) == 4
        assert resultado.rascunho.experiencias is None
        assert resultado.curriculo_adaptado == resultado.rascunho.para_curriculo("pt")

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
        caso_de_uso = AdaptarCurriculoParaVaga(
            extrator,
            analisador_vaga,
            ajustador,
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
        assert resultado.rascunho.nome_completo == "Adriano João Teixeira Filho"
        assert resultado.analise_vaga is analise

    def test_cada_secao_ajustada_compoe_o_rascunho(self):
        curriculo = _curriculo_exemplo()
        extrator = ExtratorFake(curriculo)
        analisador_vaga = JobDescriptionAnalyzerFake(
            AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga qualquer")
        )
        ajustador = AjustadorTextoFake()
        caso_de_uso = AdaptarCurriculoParaVaga(
            extrator,
            analisador_vaga,
            ajustador,
        )

        input_dto = AdaptarCurriculoParaVagaInputDto(
            pdf_curriculo=b"pdf",
            descricao_vaga="vaga qualquer",
            idioma_alvo="en",
            cargo_alvo="Software Engineer",
            empresa_alvo="TechCorp",
        )

        resultado = caso_de_uso.executar(input_dto)

        secao_perfil = resultado.rascunho.para_curriculo("en").obter_secao(TipoSecao.PERFIL)
        assert secao_perfil.conteudo == "[AJUSTADO-en] Engenheiro backend."

    def test_idioma_invalido_gera_erro(self):
        extrator = ExtratorFake(_curriculo_exemplo())
        analisador_vaga = JobDescriptionAnalyzerFake(
            AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga")
        )
        caso_de_uso = AdaptarCurriculoParaVaga(
            extrator,
            analisador_vaga,
            AjustadorTextoFake(),
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
        assert resultado.rascunho.nome_completo == "Adriano João Teixeira Filho"

    def test_sem_pdf_e_sem_curriculo_pre_montado_gera_erro(self):
        caso_de_uso = AdaptarCurriculoParaVaga(
            ExtratorFake(_curriculo_exemplo()),
            JobDescriptionAnalyzerFake(AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga")),
            AjustadorTextoFake(),
        )

        input_dto = AdaptarCurriculoParaVagaInputDto(
            descricao_vaga="vaga", idioma_alvo="pt", cargo_alvo="Cargo", empresa_alvo="Empresa"
        )

        with pytest.raises(ValueError, match="PDF"):
            caso_de_uso.executar(input_dto)


def _dimensao(score: int) -> ResultadoDimensaoAvaliacao:
    return ResultadoDimensaoAvaliacao(score=score, nivel="adequado", confianca=0.8)


def _avaliacao_vaga(score: int = 80) -> AvaliacaoDescricaoVaga:
    return AvaliacaoDescricaoVaga(
        completude=_dimensao(score),
        clareza=_dimensao(score),
        relevancia=_dimensao(score),
        inclusao=_dimensao(score),
    )


def _avaliacao_experiencia(score: int = 75) -> AvaliacaoExperiencia:
    return AvaliacaoExperiencia(
        clareza_escrita=_dimensao(score),
        qualidade_detalhe=_dimensao(score),
        aderencia_vaga=_dimensao(score),
        consistencia_textual=_dimensao(score),
    )


def _experiencias_exemplo() -> tuple[ExperienciaParaAvaliacao, ...]:
    return (
        ExperienciaParaAvaliacao(
            cargo="Engenheira de Software",
            empresa="Starian",
            periodo="2021-2024",
            descricao="Desenvolvi APIs em Python.",
        ),
        ExperienciaParaAvaliacao(
            cargo="Desenvolvedora Backend",
            empresa="TechCorp",
            periodo="2019-2021",
            descricao="Mantive serviços em Go.",
        ),
    )


def _input_estruturado() -> AdaptarCurriculoParaVagaInputDto:
    return AdaptarCurriculoParaVagaInputDto(
        curriculo_pre_montado=_curriculo_exemplo(),
        experiencias_profissionais=_experiencias_exemplo(),
        descricao_vaga="Vaga para Engenheiro de Software Python Sênior",
        idioma_alvo="pt",
        cargo_alvo="Engenheiro de Software Sênior",
        empresa_alvo="TechCorp",
    )


class TestAdaptarCurriculoParaVagaComAvaliacoes:
    def test_avalia_descricao_da_vaga_antes_da_adaptacao(self):
        eventos: list[str] = []
        caso_de_uso = AdaptarCurriculoParaVaga(
            ExtratorFake(_curriculo_exemplo()),
            JobDescriptionAnalyzerFake(
                AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga")
            ),
            AjustadorTextoFake(eventos=eventos),
            avaliador_descricao_vaga=AvaliadorDescricaoVagaFake(
                _avaliacao_vaga(), eventos=eventos
            ),
        )
        input_dto = AdaptarCurriculoParaVagaInputDto(
            pdf_curriculo=b"pdf",
            descricao_vaga="vaga",
            idioma_alvo="pt",
            cargo_alvo="Cargo",
            empresa_alvo="Empresa",
        )

        resultado = caso_de_uso.executar(input_dto)

        assert eventos[0] == "avaliar_vaga"
        assert eventos[1:] == ["ajustar_secao"] * 4
        assert resultado.status_avaliacao_vaga == StatusAvaliacaoAutomatica.AVALIADA
        assert resultado.avaliacao_vaga.score == 80

    def test_score_baixo_da_vaga_nao_bloqueia_adaptacao(self):
        ajustador = AjustadorTextoFake()
        caso_de_uso = AdaptarCurriculoParaVaga(
            ExtratorFake(_curriculo_exemplo()),
            JobDescriptionAnalyzerFake(
                AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga")
            ),
            ajustador,
            avaliador_descricao_vaga=AvaliadorDescricaoVagaFake(_avaliacao_vaga(20)),
        )
        input_dto = AdaptarCurriculoParaVagaInputDto(
            pdf_curriculo=b"pdf",
            descricao_vaga="vaga",
            idioma_alvo="pt",
            cargo_alvo="Cargo",
            empresa_alvo="Empresa",
        )

        resultado = caso_de_uso.executar(input_dto)

        assert resultado.rascunho.nome_completo == "Adriano João Teixeira Filho"
        assert resultado.avaliacao_vaga.score == 20
        assert len(ajustador.chamadas) == 4

    def test_jev_indisponivel_na_vaga_prossegue_parcialmente(self):
        caso_de_uso = AdaptarCurriculoParaVaga(
            ExtratorFake(_curriculo_exemplo()),
            JobDescriptionAnalyzerFake(
                AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga")
            ),
            AjustadorTextoFake(),
            avaliador_descricao_vaga=AvaliadorDescricaoVagaFake(
                _avaliacao_vaga(), erro=RuntimeError("Jev indisponível")
            ),
        )
        input_dto = AdaptarCurriculoParaVagaInputDto(
            pdf_curriculo=b"pdf",
            descricao_vaga="vaga",
            idioma_alvo="pt",
            cargo_alvo="Cargo",
            empresa_alvo="Empresa",
        )

        resultado = caso_de_uso.executar(input_dto)

        assert resultado.rascunho.nome_completo == "Adriano João Teixeira Filho"
        assert resultado.avaliacao_vaga is None
        assert resultado.status_avaliacao_vaga == StatusAvaliacaoAutomatica.INDISPONIVEL

    def test_experiencias_sao_adaptadas_e_avaliadas_individualmente(self):
        ajustador_texto = AjustadorTextoFake()
        ajustador_experiencia = AjustadorExperienciaFake()
        avaliador_experiencia = AvaliadorExperienciaFake(_avaliacao_experiencia())
        caso_de_uso = AdaptarCurriculoParaVaga(
            ExtratorFake(_curriculo_exemplo()),
            JobDescriptionAnalyzerFake(
                AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga")
            ),
            ajustador_texto,
            avaliador_descricao_vaga=AvaliadorDescricaoVagaFake(_avaliacao_vaga()),
            ajustador_experiencia=ajustador_experiencia,
            avaliador_experiencia=avaliador_experiencia,
        )

        resultado = caso_de_uso.executar(_input_estruturado())

        assert TipoSecao.EXPERIENCIAS not in [
            chamada[0] for chamada in ajustador_texto.chamadas
        ]
        assert ajustador_experiencia.recebidas == list(_experiencias_exemplo())
        assert len(avaliador_experiencia.recebidas) == 2
        assert all(
            experiencia.descricao.startswith("- [AJUSTADA]")
            for experiencia in avaliador_experiencia.recebidas
        )

        assert len(resultado.avaliacoes_experiencias) == 2
        original = _experiencias_exemplo()
        for resultado_experiencia, esperada in zip(
            resultado.avaliacoes_experiencias, original
        ):
            assert resultado_experiencia.status == StatusAvaliacaoAutomatica.AVALIADA
            assert resultado_experiencia.avaliacao.score == 75
            assert resultado_experiencia.experiencia.cargo == esperada.cargo
            assert resultado_experiencia.experiencia.empresa == esperada.empresa
            assert resultado_experiencia.experiencia.periodo == esperada.periodo

        assert TipoSecao.EXPERIENCIAS not in [
            secao.tipo for secao in resultado.rascunho.secoes
        ]
        assert [
            (experiencia.cargo, experiencia.empresa)
            for experiencia in resultado.rascunho.experiencias
        ] == [("Engenheira de Software", "Starian"), ("Desenvolvedora Backend", "TechCorp")]
        secao = resultado.rascunho.para_curriculo("pt").obter_secao(TipoSecao.EXPERIENCIAS)
        assert secao.titulo == "Experiências"
        assert "Engenheira de Software — Starian (2021-2024)" in secao.conteudo
        assert "Desenvolvedora Backend — TechCorp (2019-2021)" in secao.conteudo
        assert "[AJUSTADA] Desenvolvi APIs em Python." in secao.conteudo
        assert "[AJUSTADA] Mantive serviços em Go." in secao.conteudo

    def test_jev_indisponivel_nas_experiencias_marca_cada_resultado(self):
        avaliador_experiencia = AvaliadorExperienciaFake(
            _avaliacao_experiencia(), erro=RuntimeError("Jev indisponível")
        )
        caso_de_uso = AdaptarCurriculoParaVaga(
            ExtratorFake(_curriculo_exemplo()),
            JobDescriptionAnalyzerFake(
                AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga")
            ),
            AjustadorTextoFake(),
            avaliador_descricao_vaga=AvaliadorDescricaoVagaFake(_avaliacao_vaga()),
            ajustador_experiencia=AjustadorExperienciaFake(),
            avaliador_experiencia=avaliador_experiencia,
        )

        resultado = caso_de_uso.executar(_input_estruturado())

        assert resultado.rascunho.nome_completo == "Adriano João Teixeira Filho"
        assert len(resultado.avaliacoes_experiencias) == 2
        assert all(
            item.status == StatusAvaliacaoAutomatica.INDISPONIVEL
            for item in resultado.avaliacoes_experiencias
        )
        assert all(
            item.avaliacao is None for item in resultado.avaliacoes_experiencias
        )

    def test_fluxo_pdf_avalia_vaga_mas_nao_experiencias(self):
        avaliador_experiencia = AvaliadorExperienciaFake(_avaliacao_experiencia())
        ajustador_texto = AjustadorTextoFake()
        caso_de_uso = AdaptarCurriculoParaVaga(
            ExtratorFake(_curriculo_exemplo()),
            JobDescriptionAnalyzerFake(
                AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga")
            ),
            ajustador_texto,
            avaliador_descricao_vaga=AvaliadorDescricaoVagaFake(_avaliacao_vaga()),
            ajustador_experiencia=AjustadorExperienciaFake(),
            avaliador_experiencia=avaliador_experiencia,
        )
        input_dto = AdaptarCurriculoParaVagaInputDto(
            pdf_curriculo=b"pdf",
            descricao_vaga="vaga",
            idioma_alvo="pt",
            cargo_alvo="Cargo",
            empresa_alvo="Empresa",
        )

        resultado = caso_de_uso.executar(input_dto)

        assert resultado.status_avaliacao_vaga == StatusAvaliacaoAutomatica.AVALIADA
        assert resultado.avaliacoes_experiencias == ()
        assert avaliador_experiencia.recebidas == []
        assert len(ajustador_texto.chamadas) == 4
