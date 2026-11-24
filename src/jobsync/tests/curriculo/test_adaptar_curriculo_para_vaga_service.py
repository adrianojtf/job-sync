"""Testes do caso de uso AdaptarCurriculoParaVaga.

Usa dublês de teste (fakes) para as portas, mantendo o teste isolado de
qualquer infraestrutura real (PDF, LLM, etc.), conforme Hexagonal Architecture.
"""
import pytest
from dataclasses import replace

from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga import (
    AdaptarCurriculoParaVaga,
    AdaptarCurriculoParaVagaInputDto,
)
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.dtos import (
    StatusAvaliacaoAutomatica,
)
from jobsync.curriculo import (
    AjusteTecnologia,
    CategoriaCompetencia,
    AvaliacaoExperiencia,
    ContextoVaga,
    DiretrizesExperiencia,
    EquivalenciaTecnologia,
    IdentificadorEquivalenciasPort,
    ExperienciaAdaptada,
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
        self.chamadas: list[tuple[TipoSecao, ContextoVaga]] = []
        self.ajustes: list[tuple[EquivalenciaTecnologia, ...]] = []
        self.permitidos: dict[TipoSecao, tuple[str, ...] | None] = {}
        self._eventos = eventos

    def ajustar_secao(
        self, secao: SecaoCurriculo, contexto: ContextoVaga, ajustes=(), itens_permitidos=None
    ) -> SecaoCurriculo:
        self.chamadas.append((secao.tipo, contexto))
        self.permitidos[secao.tipo] = itens_permitidos
        self.ajustes.append(tuple(ajustes))
        if self._eventos is not None:
            self._eventos.append("ajustar_secao")
        return secao.com_novo_conteudo(f"[AJUSTADO-{contexto.idioma_alvo}] {secao.conteudo}")

    def refinar_secao(self, secao: SecaoCurriculo, contexto: ContextoVaga, refino) -> SecaoCurriculo:
        return secao


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
        self.contextos: list[ContextoVaga] = []
        self.diretrizes: list[DiretrizesExperiencia] = []
        self._eventos = eventos

    def ajustar(
        self,
        experiencia: ExperienciaParaAvaliacao,
        contexto: ContextoVaga,
        diretrizes: DiretrizesExperiencia,
    ) -> ExperienciaAdaptada:
        self.recebidas.append(experiencia)
        self.contextos.append(contexto)
        self.diretrizes.append(diretrizes)
        if self._eventos is not None:
            self._eventos.append("ajustar_experiencia")
        return ExperienciaAdaptada(
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
            conquistas=(f"[AJUSTADA] {experiencia.descricao}",),
            contexto=f"Contexto de {experiencia.empresa}.",
        )

    def refinar(self, experiencia: ExperienciaAdaptada, contexto: ContextoVaga, refino) -> ExperienciaAdaptada:
        return experiencia


class IdentificadorEquivalenciasFake(IdentificadorEquivalenciasPort):
    def __init__(
        self,
        equivalencias: tuple[EquivalenciaTecnologia, ...] = (),
        erro: Exception | None = None,
    ):
        self._equivalencias = equivalencias
        self._erro = erro
        self.chamadas: list[tuple[tuple[ExperienciaParaAvaliacao, ...], ContextoVaga]] = []

    def identificar(self, experiencias, contexto: ContextoVaga) -> tuple[EquivalenciaTecnologia, ...]:
        self.chamadas.append((tuple(experiencias), contexto))
        if self._erro is not None:
            raise self._erro
        return self._equivalencias


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
        assert all(
            chamada[1].descricao_vaga == "Vaga para Engenheiro de Software Python Sênior"
            for chamada in ajustador.chamadas
        )
        assert all(chamada[1].idioma_alvo == "pt" for chamada in ajustador.chamadas)
        assert all(chamada[1].cargo_alvo == "Engenheiro de Software Sênior" for chamada in ajustador.chamadas)
        assert resultado.rascunho.nome_completo == "Adriano João Teixeira Filho"
        assert resultado.rascunho.email == "adriano@example.com"
        assert len(resultado.rascunho.secoes) == 3
        assert resultado.rascunho.competencias is not None
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
        assert all(chamada[1].analise_vaga is analise for chamada in ajustador.chamadas)
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
        assert all(
            contexto.cargo_alvo == "Engenheiro de Software Sênior"
            and contexto.descricao_vaga == "Vaga para Engenheiro de Software Python Sênior"
            for contexto in ajustador_experiencia.contextos
        )
        assert len(avaliador_experiencia.recebidas) == 2
        assert [experiencia.descricao for experiencia in avaliador_experiencia.recebidas] == [
            "- [AJUSTADA] Desenvolvi APIs em Python.\nContexto de Starian.",
            "- [AJUSTADA] Mantive serviços em Go.\nContexto de TechCorp.",
        ]

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
            (experiencia.cargo, experiencia.empresa, experiencia.conquistas, experiencia.contexto)
            for experiencia in resultado.rascunho.experiencias
        ] == [
            (
                "Engenheira de Software",
                "Starian",
                ("[AJUSTADA] Desenvolvi APIs em Python.",),
                "Contexto de Starian.",
            ),
            (
                "Desenvolvedora Backend",
                "TechCorp",
                ("[AJUSTADA] Mantive serviços em Go.",),
                "Contexto de TechCorp.",
            ),
        ]
        secao = resultado.rascunho.para_curriculo("pt").obter_secao(TipoSecao.EXPERIENCIAS)
        assert secao.titulo == "Experiências"
        assert "Engenheira de Software — Starian (2021-2024)" in secao.conteudo
        assert "Desenvolvedora Backend — TechCorp (2019-2021)" in secao.conteudo
        assert "[AJUSTADA] Desenvolvi APIs em Python." in secao.conteudo
        assert "[AJUSTADA] Mantive serviços em Go." in secao.conteudo
        assert "\nContexto: Contexto de Starian." in secao.conteudo
        assert "\nContexto: Contexto de TechCorp." in secao.conteudo

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


PYTHON_KOTLIN = EquivalenciaTecnologia(original="Python", alvo="Kotlin")


def _caso_com_identificador(
    identificador: IdentificadorEquivalenciasFake | None,
) -> tuple[AdaptarCurriculoParaVaga, AjustadorTextoFake, AjustadorExperienciaFake]:
    ajustador_texto = AjustadorTextoFake()
    ajustador_experiencia = AjustadorExperienciaFake()
    caso_de_uso = AdaptarCurriculoParaVaga(
        ExtratorFake(_curriculo_exemplo()),
        JobDescriptionAnalyzerFake(AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga")),
        ajustador_texto,
        ajustador_experiencia=ajustador_experiencia,
        identificador_equivalencias=identificador,
    )
    return caso_de_uso, ajustador_texto, ajustador_experiencia


class TestAdaptarCurriculoParaVagaPlanoDeTecnologias:
    def test_plano_orienta_cada_experiencia_as_secoes_e_o_rascunho(self):
        identificador = IdentificadorEquivalenciasFake((PYTHON_KOTLIN,))
        caso_de_uso, ajustador_texto, ajustador_experiencia = _caso_com_identificador(identificador)

        resultado = caso_de_uso.executar(_input_estruturado())

        experiencias_recebidas, contexto_recebido = identificador.chamadas[0]
        assert experiencias_recebidas == _experiencias_exemplo()
        assert contexto_recebido.cargo_alvo == "Engenheiro de Software Sênior"
        assert ajustador_experiencia.diretrizes == [
            DiretrizesExperiencia(trocar=(PYTHON_KOTLIN,)),
            DiretrizesExperiencia(),
        ]
        assert all(ajustes == (PYTHON_KOTLIN,) for ajustes in ajustador_texto.ajustes)
        assert resultado.rascunho.ajustes_tecnologia == (AjusteTecnologia(0, PYTHON_KOTLIN),)

    def test_falha_do_identificador_segue_com_plano_vazio(self):
        identificador = IdentificadorEquivalenciasFake(erro=ValueError("formato"))
        caso_de_uso, ajustador_texto, ajustador_experiencia = _caso_com_identificador(identificador)

        resultado = caso_de_uso.executar(_input_estruturado())

        assert ajustador_experiencia.diretrizes == [DiretrizesExperiencia(), DiretrizesExperiencia()]
        assert all(ajustes == () for ajustes in ajustador_texto.ajustes)
        assert resultado.rascunho.ajustes_tecnologia == ()

    def test_sem_identificador_adapta_sem_trocas(self):
        caso_de_uso, _, ajustador_experiencia = _caso_com_identificador(None)

        resultado = caso_de_uso.executar(_input_estruturado())

        assert ajustador_experiencia.diretrizes == [DiretrizesExperiencia(), DiretrizesExperiencia()]
        assert resultado.rascunho.ajustes_tecnologia == ()

    def test_fonte_pdf_nao_identifica_equivalencias(self):
        identificador = IdentificadorEquivalenciasFake((PYTHON_KOTLIN,))
        caso_de_uso, ajustador_texto, _ = _caso_com_identificador(identificador)

        caso_de_uso.executar(
            AdaptarCurriculoParaVagaInputDto(
                pdf_curriculo=b"%PDF",
                descricao_vaga="vaga",
                idioma_alvo="pt",
                cargo_alvo="Cargo",
                empresa_alvo="Empresa",
            )
        )

        assert identificador.chamadas == []
        assert all(ajustes == () for ajustes in ajustador_texto.ajustes)


class TestAdaptarCurriculoParaVagaComBancoDeConquistas:
    def test_entrega_as_conquistas_de_cada_experiencia_ao_ajustador(self):
        caso_de_uso, _, ajustador_experiencia = _caso_com_identificador(None)
        experiencias = (
            ExperienciaParaAvaliacao(
                cargo="Engenheira de Software", empresa="Starian", periodo="2021-2024",
                descricao="Desenvolvi APIs em Python.", conquistas=("Reduzi o tempo de deploy.",),
            ),
            ExperienciaParaAvaliacao(
                cargo="Desenvolvedora Backend", empresa="TechCorp", periodo="2019-2021",
                descricao="Mantive serviços em Go.",
            ),
        )
        entrada = replace(_input_estruturado(), experiencias_profissionais=experiencias)

        caso_de_uso.executar(entrada)

        assert [e.conquistas for e in ajustador_experiencia.recebidas] == [("Reduzi o tempo de deploy.",), ()]

    def test_registra_no_log_quantas_experiencias_tem_banco_sem_o_texto_das_conquistas(self, caplog):
        caso_de_uso, _, _ = _caso_com_identificador(None)
        experiencias = (
            ExperienciaParaAvaliacao(
                cargo="Engenheira", empresa="Starian", periodo="2021-2024", descricao="APIs.",
                conquistas=("Segredo de negócio A.", "Segredo de negócio B."),
            ),
        )
        entrada = replace(_input_estruturado(), experiencias_profissionais=experiencias)

        with caplog.at_level("INFO"):
            caso_de_uso.executar(entrada)

        mensagens = " ".join(registro.getMessage() for registro in caplog.records)
        assert "experiencias_com_banco=1" in mensagens
        assert "conquistas=2" in mensagens
        assert "Segredo de negócio" not in mensagens

    def test_sem_banco_de_conquistas_nao_registra_o_log_do_banco(self, caplog):
        caso_de_uso, _, _ = _caso_com_identificador(None)

        with caplog.at_level("INFO"):
            caso_de_uso.executar(_input_estruturado())

        assert "experiencias_com_banco" not in " ".join(r.getMessage() for r in caplog.records)


class AjustadorTextoDeTecnologiasFake(AjustadorTextoFake):
    def __init__(self, conteudo_tecnologias: str):
        super().__init__()
        self._conteudo_tecnologias = conteudo_tecnologias

    def ajustar_secao(
        self, secao: SecaoCurriculo, contexto: ContextoVaga, ajustes=(), itens_permitidos=None
    ) -> SecaoCurriculo:
        if secao.tipo == TipoSecao.TECNOLOGIAS:
            return secao.com_novo_conteudo(self._conteudo_tecnologias)
        return super().ajustar_secao(secao, contexto, ajustes)


def _adaptar(curriculo: Curriculo, ajustador: AjustadorTextoPort):
    caso_de_uso = AdaptarCurriculoParaVaga(
        ExtratorFake(curriculo),
        JobDescriptionAnalyzerFake(AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="Vaga")),
        ajustador,
    )
    return caso_de_uso.executar(
        AdaptarCurriculoParaVagaInputDto(
            pdf_curriculo=b"pdf",
            descricao_vaga="Vaga",
            idioma_alvo="pt",
            cargo_alvo="Engenheiro",
            empresa_alvo="TechCorp",
        )
    )


class TestAdaptarCurriculoComCompetencias:
    def test_secao_de_tecnologias_da_ia_vira_competencias_por_categoria(self):
        ajustador = AjustadorTextoDeTecnologiasFake("Linguagens: Java, Python\nOutros: Go")

        rascunho = _adaptar(_curriculo_exemplo(), ajustador).rascunho

        assert rascunho.competencias == (
            CategoriaCompetencia("Linguagens", ("Java", "Python")),
            CategoriaCompetencia("Outros", ("Go",)),
        )

    def test_a_secao_de_tecnologias_em_texto_sai_das_secoes(self):
        ajustador = AjustadorTextoDeTecnologiasFake("Linguagens: Java")

        rascunho = _adaptar(_curriculo_exemplo(), ajustador).rascunho

        assert all(secao.tipo != TipoSecao.TECNOLOGIAS for secao in rascunho.secoes)

    def test_o_titulo_da_secao_de_tecnologias_vira_o_titulo_das_competencias(self):
        ajustador = AjustadorTextoDeTecnologiasFake("Linguagens: Java")

        rascunho = _adaptar(_curriculo_exemplo(), ajustador).rascunho

        assert rascunho.titulo_competencias == "Tecnologias"

    def test_texto_sem_rotulo_vira_a_categoria_padrao(self):
        ajustador = AjustadorTextoDeTecnologiasFake("Java, Go, Python")

        rascunho = _adaptar(_curriculo_exemplo(), ajustador).rascunho

        assert rascunho.competencias == (CategoriaCompetencia("Tecnologias", ("Java", "Go", "Python")),)

    def test_o_curriculo_adaptado_mantem_a_secao_de_tecnologias_em_texto(self):
        ajustador = AjustadorTextoDeTecnologiasFake("Linguagens: Java, Python")

        resultado = _adaptar(_curriculo_exemplo(), ajustador)

        secao = resultado.curriculo_adaptado.obter_secao(TipoSecao.TECNOLOGIAS)
        assert secao.conteudo == "Linguagens: Java, Python"

    def test_sem_secao_de_tecnologias_nao_ha_competencias(self):
        curriculo = Curriculo(
            nome_completo="Ana Souza",
            email="ana@ex.com",
            linkedin="",
            secoes=(SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Engenheira."),),
        )

        rascunho = _adaptar(curriculo, AjustadorTextoFake()).rascunho

        assert rascunho.competencias is None


def _requisito(nome, categoria=CategoriaRequisitoTecnico.TECNOLOGIA):
    return RequisitoTecnico(
        nome=nome,
        categoria=categoria,
        tipo=TipoRequisitoTecnico.EXPLICITO,
        origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
    )


def _adaptar_vaga(curriculo, ajustador, requisitos=(), experiencias=None, **servicos):
    analise = AnaliseVaga(requisitos=tuple(requisitos), ambiguidade=(), texto_original="Vaga")
    caso_de_uso = AdaptarCurriculoParaVaga(
        ExtratorFake(curriculo), JobDescriptionAnalyzerFake(analise), ajustador, **servicos
    )
    return caso_de_uso.executar(
        AdaptarCurriculoParaVagaInputDto(
            pdf_curriculo=b"pdf",
            descricao_vaga="Vaga",
            idioma_alvo="pt",
            cargo_alvo="Engenheiro",
            empresa_alvo="TechCorp",
            experiencias_profissionais=experiencias,
        )
    )


def _curriculo_com_tecnologias(conteudo: str) -> Curriculo:
    return Curriculo(
        nome_completo="Ana Souza",
        email="ana@ex.com",
        linkedin="",
        secoes=(
            SecaoCurriculo(TipoSecao.TECNOLOGIAS, "Tecnologias", conteudo),
            SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Engenheira."),
        ),
    )


def _tags(rascunho) -> list[str]:
    return [tag for categoria in rascunho.competencias or () for tag in categoria.tags]


class TestCompetenciasPorEvidencia:
    def test_a_ia_recebe_so_os_itens_do_candidato_como_permitidos(self):
        ajustador = AjustadorTextoFake()

        _adaptar_vaga(_curriculo_com_tecnologias("Java, Python"), ajustador, requisitos=(_requisito("Kafka"),))

        assert ajustador.permitidos[TipoSecao.TECNOLOGIAS] == ("Java", "Python")

    def test_as_outras_secoes_nao_recebem_itens_permitidos(self):
        ajustador = AjustadorTextoFake()

        _adaptar_vaga(_curriculo_com_tecnologias("Java"), ajustador)

        assert ajustador.permitidos[TipoSecao.PERFIL] is None

    def test_item_que_a_ia_acrescenta_fora_dos_permitidos_e_descartado(self):
        ajustador = AjustadorTextoDeTecnologiasFake("Linguagens: Java, Python\nMensageria: Kafka")

        rascunho = _adaptar_vaga(
            _curriculo_com_tecnologias("Java, Python"), ajustador, requisitos=(_requisito("Kafka"),)
        ).rascunho

        assert _tags(rascunho) == ["Java", "Python"]

    def test_tecnologia_da_vaga_sem_evidencia_vira_lacuna(self):
        rascunho = _adaptar_vaga(
            _curriculo_com_tecnologias("Java"), AjustadorTextoFake(), requisitos=(_requisito("Kafka"),)
        ).rascunho

        assert rascunho.lacunas_tecnologia == ("Kafka",)

    def test_requisito_que_nao_e_tecnologia_nao_vira_lacuna_nem_entra(self):
        rascunho = _adaptar_vaga(
            _curriculo_com_tecnologias("Java"),
            AjustadorTextoFake(),
            requisitos=(_requisito("aprovação humana", CategoriaRequisitoTecnico.HABILIDADE),),
        ).rascunho

        assert rascunho.lacunas_tecnologia == ()

    def test_tecnologia_citada_numa_experiencia_tem_evidencia_e_pode_entrar(self):
        ajustador = AjustadorTextoFake()
        experiencias = (
            ExperienciaParaAvaliacao(
                cargo="Dev", empresa="Acme", periodo="2024", descricao="Mensageria com RabbitMQ."
            ),
        )

        rascunho = _adaptar_vaga(
            _curriculo_com_tecnologias("Java"),
            ajustador,
            requisitos=(_requisito("RabbitMQ"),),
            experiencias=experiencias,
            ajustador_experiencia=AjustadorExperienciaFake(),
        ).rascunho

        assert ajustador.permitidos[TipoSecao.TECNOLOGIAS] == ("Java", "RabbitMQ")
        assert rascunho.lacunas_tecnologia == ()

    def test_equivalencia_aplicada_entra_nos_permitidos(self):
        ajustador = AjustadorTextoFake()
        experiencias = (
            ExperienciaParaAvaliacao(cargo="Dev", empresa="Acme", periodo="2024", descricao="Telas em React."),
        )

        rascunho = _adaptar_vaga(
            _curriculo_com_tecnologias("React"),
            ajustador,
            requisitos=(_requisito("Angular"),),
            experiencias=experiencias,
            ajustador_experiencia=AjustadorExperienciaFake(),
            identificador_equivalencias=IdentificadorEquivalenciasFake(
                (EquivalenciaTecnologia(original="React", alvo="Angular"),)
            ),
        ).rascunho

        assert ajustador.permitidos[TipoSecao.TECNOLOGIAS] == ("React", "Angular")
        assert rascunho.lacunas_tecnologia == ()

    def test_acima_do_teto_a_lista_e_cortada_e_os_relevantes_ficam(self):
        itens = ", ".join(f"Tec{numero}" for numero in range(60))
        conteudo_da_ia = "Tudo: " + itens
        ajustador = AjustadorTextoDeTecnologiasFake(conteudo_da_ia)

        rascunho = _adaptar_vaga(
            _curriculo_com_tecnologias(itens), ajustador, requisitos=(_requisito("Tec59"),)
        ).rascunho

        assert len(_tags(rascunho)) == 45
        assert "Tec59" in _tags(rascunho)
        assert "Tec0" in _tags(rascunho)

    def test_se_a_ia_devolve_so_itens_fora_dos_permitidos_nao_ha_competencias(self):
        ajustador = AjustadorTextoDeTecnologiasFake("Mensageria: Kafka")

        rascunho = _adaptar_vaga(_curriculo_com_tecnologias("Java"), ajustador).rascunho

        assert rascunho.competencias is None
        assert all(secao.tipo != TipoSecao.TECNOLOGIAS for secao in rascunho.secoes)

    def test_sem_secao_de_tecnologias_nao_ha_competencias_e_a_vaga_gera_lacunas(self):
        curriculo = Curriculo(
            nome_completo="Ana Souza",
            email="ana@ex.com",
            linkedin="",
            secoes=(SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Engenheira."),),
        )

        rascunho = _adaptar_vaga(curriculo, AjustadorTextoFake(), requisitos=(_requisito("Kafka"),)).rascunho

        assert rascunho.competencias is None
        assert rascunho.lacunas_tecnologia == ("Kafka",)

    def test_o_curriculo_adaptado_do_resultado_traz_so_as_competencias_filtradas(self):
        ajustador = AjustadorTextoDeTecnologiasFake("Linguagens: Java\nMensageria: Kafka")

        resultado = _adaptar_vaga(_curriculo_com_tecnologias("Java"), ajustador)

        assert resultado.curriculo_adaptado.obter_secao(TipoSecao.TECNOLOGIAS).conteudo == "Linguagens: Java"


class TestConquistasDoHistorico:
    def _experiencias(self) -> tuple[ExperienciaParaAvaliacao, ...]:
        return (
            ExperienciaParaAvaliacao(
                cargo="Dev", empresa="Acme", periodo="2024", descricao="Backend.",
                conquistas=("Atuei junto ao cliente na entrega de um MVP.", "Reduzi o tempo de deploy."),
            ),
            ExperienciaParaAvaliacao(
                cargo="Dev", empresa="Beta", periodo="2020", descricao="Serviços.",
                conquistas=("Mentorei duas pessoas juniores.",),
            ),
        )

    def test_o_contexto_das_secoes_leva_as_conquistas_das_experiencias_em_ordem(self):
        ajustador = AjustadorTextoFake()

        _adaptar_vaga(
            _curriculo_com_tecnologias("Java"),
            ajustador,
            experiencias=self._experiencias(),
            ajustador_experiencia=AjustadorExperienciaFake(),
        )

        contexto = ajustador.chamadas[0][1]
        assert contexto.conquistas_do_historico == (
            "Atuei junto ao cliente na entrega de um MVP.",
            "Reduzi o tempo de deploy.",
            "Mentorei duas pessoas juniores.",
        )

    def test_sem_conquistas_o_contexto_vai_sem_elas(self):
        ajustador = AjustadorTextoFake()

        _adaptar_vaga(_curriculo_com_tecnologias("Java"), ajustador)

        assert ajustador.chamadas[0][1].conquistas_do_historico == ()

    def test_tecnologia_citada_numa_conquista_aprovada_tem_evidencia_e_pode_entrar(self):
        ajustador = AjustadorTextoFake()
        experiencias = (
            ExperienciaParaAvaliacao(
                cargo="Dev", empresa="Acme", periodo="2024", descricao="Backend.",
                conquistas=("Construí um MVP de pagamentos em Python junto ao cliente.",),
            ),
        )

        rascunho = _adaptar_vaga(
            _curriculo_com_tecnologias("Java"),
            ajustador,
            requisitos=(_requisito("Python"),),
            experiencias=experiencias,
            ajustador_experiencia=AjustadorExperienciaFake(),
        ).rascunho

        assert ajustador.permitidos[TipoSecao.TECNOLOGIAS] == ("Java", "Python")
        assert rascunho.lacunas_tecnologia == ()

    def test_sem_a_conquista_a_mesma_tecnologia_continua_lacuna(self):
        experiencias = (
            ExperienciaParaAvaliacao(cargo="Dev", empresa="Acme", periodo="2024", descricao="Backend."),
        )

        rascunho = _adaptar_vaga(
            _curriculo_com_tecnologias("Java"),
            AjustadorTextoFake(),
            requisitos=(_requisito("Python"),),
            experiencias=experiencias,
            ajustador_experiencia=AjustadorExperienciaFake(),
        ).rascunho

        assert rascunho.lacunas_tecnologia == ("Python",)


class AjustadorExperienciaComSkillsFake(AjustadorExperienciaFake):
    def ajustar(self, experiencia, contexto, diretrizes):
        base = super().ajustar(experiencia, contexto, diretrizes)
        return ExperienciaAdaptada(
            cargo=base.cargo,
            empresa=base.empresa,
            periodo=base.periodo,
            conquistas=base.conquistas,
            contexto=base.contexto,
            responsabilidades=("Projetar telas.",),
            skills=("Java", "Flyway"),
        )


class TestAdaptarCurriculoComSkillsDasExperiencias:
    def test_skills_das_experiencias_ausentes_nas_competencias_entram_em_tecnologias(self):
        ajustador_texto = AjustadorTextoDeTecnologiasFake("Linguagens: Java")

        rascunho = _adaptar_vaga(
            _curriculo_com_tecnologias("Linguagens: Java"),
            ajustador_texto,
            experiencias=_experiencias_exemplo(),
            ajustador_experiencia=AjustadorExperienciaComSkillsFake(),
        ).rascunho

        assert rascunho.competencias == (
            CategoriaCompetencia("Linguagens", ("Java",)),
            CategoriaCompetencia("Tecnologias", ("Flyway",)),
        )
        assert rascunho.experiencias[0].responsabilidades == ("Projetar telas.",)
