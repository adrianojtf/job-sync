"""Testes dos casos de uso do currículo adaptado, com repositório fake e gerador de PDF falso."""
import logging
from datetime import date
from unittest.mock import Mock

import pytest

from jobsync.curriculo import Curriculo, GeradorPdfPort, RascunhoCurriculoAdaptado, TipoSecao
from jobsync.curriculo_adaptado.adapters import CurriculoAdaptadoRepositoryFake
from jobsync.curriculo_adaptado.domain.exceptions import CurriculoAdaptadoNaoEncontrado
from jobsync.curriculo_adaptado.service_layer.atualizar_curriculo_adaptado import (
    AtualizarCurriculoAdaptado,
    AtualizarCurriculoAdaptadoInputDto,
)
from jobsync.curriculo_adaptado.service_layer.buscar_curriculo_adaptado import BuscarCurriculoAdaptado
from jobsync.curriculo_adaptado.service_layer.listar_curriculos_adaptados import (
    ListarCurriculosAdaptados,
)
from jobsync.curriculo_adaptado.service_layer.salvar_curriculo_adaptado import (
    SalvarCurriculoAdaptado,
    SalvarCurriculoAdaptadoInputDto,
)
from jobsync.curriculo_salvo import CurriculoSalvo
from jobsync.curriculo_salvo.adapters import CurriculoSalvoRepositoryFake
from jobsync.tests.curriculo_adaptado.exemplos import (
    AGORA,
    DEPOIS,
    analise_vaga,
    curriculo_adaptado,
    rascunho,
)

DATA = date(2026, 11, 23)


@pytest.fixture
def repositorio():
    return CurriculoAdaptadoRepositoryFake()


@pytest.fixture
def gerador_pdf():
    gerador = Mock(spec=GeradorPdfPort)
    gerador.gerar.return_value = b"%PDF-gerado"
    return gerador


def _dto_de_salvar(**sobrescritas) -> SalvarCurriculoAdaptadoInputDto:
    valores = {
        "perfil_identificador": "ana",
        "rascunho": rascunho(),
        "idioma_alvo": "pt",
        "cargo_alvo": "Engenheira de Software",
        "empresa_alvo": "TechCorp",
        "descricao_vaga": "Vaga Java com code review.",
        "analise_vaga": analise_vaga(),
        "data_referencia": DATA,
    }
    valores.update(sobrescritas)
    return SalvarCurriculoAdaptadoInputDto(**valores)


def _revisado(*competencias) -> RascunhoCurriculoAdaptado:
    return RascunhoCurriculoAdaptado.revisado(
        nome_completo="Ana Souza",
        email="ana@ex.com",
        linkedin="",
        secoes=((TipoSecao.PERFIL, "Perfil", "Texto revisado."),),
        experiencias=None,
        competencias=competencias,
    )


class TestSalvarCurriculoAdaptado:
    def test_salva_o_curriculo_no_perfil_com_o_contexto_da_vaga(self, repositorio, gerador_pdf):
        servico = SalvarCurriculoAdaptado(repositorio, gerador_pdf, relogio=lambda: AGORA)

        resultado = servico.executar(_dto_de_salvar())

        salvo = repositorio.buscar(resultado.curriculo.id, "ana")
        assert salvo == resultado.curriculo
        assert salvo.cargo_alvo == "Engenheira de Software"
        assert salvo.empresa_alvo == "TechCorp"
        assert salvo.idioma_alvo == "pt"
        assert salvo.descricao_vaga == "Vaga Java com code review."
        assert salvo.analise_vaga == analise_vaga()
        assert salvo.rascunho == rascunho()
        assert salvo.criado_em == AGORA

    def test_gera_o_pdf_do_rascunho_no_idioma_alvo_e_devolve_o_nome_do_arquivo(
        self, repositorio, gerador_pdf
    ):
        servico = SalvarCurriculoAdaptado(repositorio, gerador_pdf, relogio=lambda: AGORA)

        resultado = servico.executar(_dto_de_salvar())

        curriculo, idioma = gerador_pdf.gerar.call_args.args
        assert isinstance(curriculo, Curriculo)
        assert curriculo == rascunho().para_curriculo("pt")
        assert idioma == "pt"
        assert resultado.pdf_bytes == b"%PDF-gerado"
        assert resultado.nome_arquivo.valor == "AnaSouza-2026-11-23-EngenheiraDeSoftware-Techcorp.pdf"

    def test_o_nome_de_referencia_e_o_nome_do_arquivo(self, repositorio, gerador_pdf):
        servico = SalvarCurriculoAdaptado(repositorio, gerador_pdf, relogio=lambda: AGORA)

        resultado = servico.executar(_dto_de_salvar())

        assert resultado.curriculo.nome_referencia == resultado.nome_arquivo.valor

    @pytest.mark.parametrize(
        "campo, valor",
        [
            ("idioma_alvo", "fr"),
            ("cargo_alvo", " "),
            ("empresa_alvo", ""),
            ("descricao_vaga", " "),
            ("perfil_identificador", " "),
        ],
    )
    def test_dados_invalidos_geram_erro_sem_salvar_nem_gerar_pdf(
        self, repositorio, gerador_pdf, campo, valor
    ):
        servico = SalvarCurriculoAdaptado(repositorio, gerador_pdf, relogio=lambda: AGORA)

        with pytest.raises(ValueError):
            servico.executar(_dto_de_salvar(**{campo: valor}))

        assert repositorio.listar_por_perfil("ana") == ()
        gerador_pdf.gerar.assert_not_called()

    def test_falha_ao_gerar_o_pdf_nao_deixa_o_curriculo_salvo(self, repositorio, gerador_pdf):
        gerador_pdf.gerar.side_effect = RuntimeError("falhou")
        servico = SalvarCurriculoAdaptado(repositorio, gerador_pdf, relogio=lambda: AGORA)

        with pytest.raises(RuntimeError):
            servico.executar(_dto_de_salvar())

        assert repositorio.listar_por_perfil("ana") == ()


class TestAtualizarCurriculoAdaptado:
    def _servico(self, repositorio, gerador_pdf):
        return AtualizarCurriculoAdaptado(repositorio, gerador_pdf, relogio=lambda: DEPOIS)

    def test_substitui_o_rascunho_e_regenera_o_pdf(self, repositorio, gerador_pdf):
        repositorio.salvar(curriculo_adaptado())
        revisado = _revisado(("Linguagens", ("Go",)))

        resultado = self._servico(repositorio, gerador_pdf).executar(
            AtualizarCurriculoAdaptadoInputDto("adaptado-1", "ana", revisado, DATA)
        )

        salvo = repositorio.buscar("adaptado-1", "ana")
        assert salvo.rascunho == revisado
        assert salvo.atualizado_em == DEPOIS
        assert salvo.criado_em == AGORA
        assert gerador_pdf.gerar.call_args.args == (revisado.para_curriculo("pt"), "pt")
        assert resultado.pdf_bytes == b"%PDF-gerado"
        assert resultado.nome_arquivo.valor == "AnaSouza-2026-11-23-EngenheiraDeSoftware-Techcorp.pdf"

    def test_mantem_a_vaga_e_o_vinculo_do_curriculo_salvo(self, repositorio, gerador_pdf):
        repositorio.salvar(curriculo_adaptado().com_curriculo_salvo("salvo-9"))

        self._servico(repositorio, gerador_pdf).executar(
            AtualizarCurriculoAdaptadoInputDto("adaptado-1", "ana", _revisado(("A", ("b",))), DATA)
        )

        salvo = repositorio.buscar("adaptado-1", "ana")
        assert salvo.curriculo_salvo_id == "salvo-9"
        assert salvo.descricao_vaga == "Vaga Java com code review."
        assert salvo.analise_vaga == analise_vaga()

    def test_curriculo_inexistente_gera_erro_sem_gerar_pdf(self, repositorio, gerador_pdf):
        with pytest.raises(CurriculoAdaptadoNaoEncontrado):
            self._servico(repositorio, gerador_pdf).executar(
                AtualizarCurriculoAdaptadoInputDto("nao-existe", "ana", _revisado(("A", ("b",))), DATA)
            )

        gerador_pdf.gerar.assert_not_called()

    def test_curriculo_de_outro_perfil_gera_erro_e_nao_e_alterado(self, repositorio, gerador_pdf):
        original = curriculo_adaptado()
        repositorio.salvar(original)

        with pytest.raises(CurriculoAdaptadoNaoEncontrado):
            self._servico(repositorio, gerador_pdf).executar(
                AtualizarCurriculoAdaptadoInputDto(
                    "adaptado-1", "outra-pessoa", _revisado(("A", ("b",))), DATA
                )
            )

        assert repositorio.buscar("adaptado-1", "ana") == original

    def test_falha_ao_gerar_o_pdf_nao_altera_o_curriculo_salvo(self, repositorio, gerador_pdf):
        original = curriculo_adaptado()
        repositorio.salvar(original)
        gerador_pdf.gerar.side_effect = RuntimeError("falhou")

        with pytest.raises(RuntimeError):
            self._servico(repositorio, gerador_pdf).executar(
                AtualizarCurriculoAdaptadoInputDto("adaptado-1", "ana", _revisado(("A", ("b",))), DATA)
            )

        assert repositorio.buscar("adaptado-1", "ana") == original


class TestBuscarCurriculoAdaptado:
    def test_devolve_o_curriculo_do_perfil(self, repositorio):
        repositorio.salvar(curriculo_adaptado())

        assert BuscarCurriculoAdaptado(repositorio).executar("adaptado-1", "ana") == curriculo_adaptado()

    def test_curriculo_de_outro_perfil_gera_erro(self, repositorio):
        repositorio.salvar(curriculo_adaptado())

        with pytest.raises(CurriculoAdaptadoNaoEncontrado):
            BuscarCurriculoAdaptado(repositorio).executar("adaptado-1", "outra-pessoa")

    def test_curriculo_inexistente_gera_erro(self, repositorio):
        with pytest.raises(CurriculoAdaptadoNaoEncontrado):
            BuscarCurriculoAdaptado(repositorio).executar("nao-existe", "ana")


class TestListarCurriculosAdaptados:
    def test_lista_so_os_do_perfil_do_mais_recente_para_o_mais_antigo(self, repositorio):
        antigo = curriculo_adaptado(id="a-1", atualizado_em=AGORA)
        recente = curriculo_adaptado(id="a-2", atualizado_em=DEPOIS)
        repositorio.salvar(antigo)
        repositorio.salvar(recente)
        repositorio.salvar(curriculo_adaptado(id="a-3", perfil_identificador="outra-pessoa"))

        assert ListarCurriculosAdaptados(repositorio).executar("ana") == (recente, antigo)


class CurriculoSalvoRepositoryQueFalha(CurriculoSalvoRepositoryFake):
    def atualizar_pdf(self, curriculo_id, perfil_identificador, pdf_bytes) -> bool:
        raise RuntimeError("falha ao atualizar o PDF")


def _curriculo_salvo() -> CurriculoSalvo:
    return CurriculoSalvo(
        id="salvo-9",
        perfil_identificador="ana",
        nome_referencia="Ana.pdf",
        pdf_bytes=b"%PDF-antigo",
        data_upload=AGORA,
    )


class TestAtualizarCurriculoAdaptadoComCurriculoSalvo:
    def _servico(self, repositorio, gerador_pdf, salvos):
        return AtualizarCurriculoAdaptado(
            repositorio, gerador_pdf, repositorio_curriculo_salvo=salvos, relogio=lambda: DEPOIS
        )

    def _dto(self) -> AtualizarCurriculoAdaptadoInputDto:
        return AtualizarCurriculoAdaptadoInputDto("adaptado-1", "ana", _revisado(("A", ("b",))), DATA)

    def test_atualiza_o_pdf_do_curriculo_salvo_vinculado(self, repositorio, gerador_pdf):
        salvos = CurriculoSalvoRepositoryFake()
        salvos.salvar(_curriculo_salvo())
        repositorio.salvar(curriculo_adaptado().com_curriculo_salvo("salvo-9"))

        self._servico(repositorio, gerador_pdf, salvos).executar(self._dto())

        assert salvos.listar_por_perfil("ana")[0].pdf_bytes == b"%PDF-gerado"

    def test_sem_vinculo_o_curriculo_salvo_nao_e_tocado(self, repositorio, gerador_pdf):
        salvos = CurriculoSalvoRepositoryFake()
        salvos.salvar(_curriculo_salvo())
        repositorio.salvar(curriculo_adaptado())

        self._servico(repositorio, gerador_pdf, salvos).executar(self._dto())

        assert salvos.listar_por_perfil("ana")[0].pdf_bytes == b"%PDF-antigo"

    def test_curriculo_salvo_removido_nao_gera_erro(self, repositorio, gerador_pdf):
        repositorio.salvar(curriculo_adaptado().com_curriculo_salvo("salvo-removido"))

        resultado = self._servico(repositorio, gerador_pdf, CurriculoSalvoRepositoryFake()).executar(
            self._dto()
        )

        assert resultado.pdf_bytes == b"%PDF-gerado"

    def test_falha_ao_atualizar_o_pdf_salvo_devolve_o_pdf_novo_e_registra_em_log(
        self, repositorio, gerador_pdf, caplog
    ):
        repositorio.salvar(curriculo_adaptado().com_curriculo_salvo("salvo-9"))
        salvos = CurriculoSalvoRepositoryQueFalha()

        with caplog.at_level(logging.WARNING):
            resultado = self._servico(repositorio, gerador_pdf, salvos).executar(self._dto())

        assert resultado.pdf_bytes == b"%PDF-gerado"
        assert repositorio.buscar("adaptado-1", "ana").rascunho == _revisado(("A", ("b",)))
        assert "salvo-9" in caplog.text

    def test_sem_repositorio_de_curriculo_salvo_so_atualiza_o_adaptado(self, repositorio, gerador_pdf):
        repositorio.salvar(curriculo_adaptado().com_curriculo_salvo("salvo-9"))

        resultado = AtualizarCurriculoAdaptado(
            repositorio, gerador_pdf, relogio=lambda: DEPOIS
        ).executar(self._dto())

        assert resultado.pdf_bytes == b"%PDF-gerado"
