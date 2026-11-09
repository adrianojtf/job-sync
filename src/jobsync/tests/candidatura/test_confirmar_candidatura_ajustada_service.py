import logging

import pytest

from jobsync.candidatura import Candidatura, CandidaturaRepository, StatusCandidatura
from jobsync.candidatura.service_layer.confirmar_candidatura_ajustada import (
    ConfirmarCandidaturaAjustada,
    ConfirmarCandidaturaAjustadaInputDto,
)
from jobsync.curriculo_salvo import CurriculoSalvo, CurriculoSalvoRepository
from jobsync.curriculo_salvo.domain.limite_curriculos_salvos import (
    LIMITE_CURRICULOS_POR_PERFIL,
    LimiteCurriculosSalvosExcedido,
)
from jobsync.vaga import Vaga
from jobsync.vaga.domain.vaga_repository import VagaRepository

DESCRICAO_DA_VAGA = "Vaga confidencial de engenharia de software"
PDF = b"%PDF-1.4 conteudo-do-curriculo-gerado"


class FalhaDeBanco(RuntimeError):
    pass


class CandidaturaRepositoryFake(CandidaturaRepository):
    def __init__(self, falhar_ao_salvar: bool = False) -> None:
        self.candidaturas: list[Candidatura] = []
        self._falhar_ao_salvar = falhar_ao_salvar

    def salvar(self, candidatura: Candidatura) -> Candidatura:
        if self._falhar_ao_salvar:
            raise FalhaDeBanco("falha ao salvar a candidatura")
        self.candidaturas.append(candidatura)
        return candidatura

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[Candidatura, ...]:
        return tuple(self.candidaturas)

    def atualizar_status(self, candidatura_id: str, novo_status: StatusCandidatura) -> Candidatura:
        raise NotImplementedError


class VagaRepositoryFake(VagaRepository):
    def __init__(self, falhar_ao_salvar: bool = False, falhar_ao_marcar: bool = False) -> None:
        self.vagas: list[Vaga] = []
        self.convertidas: set[str] = set()
        self._falhar_ao_salvar = falhar_ao_salvar
        self._falhar_ao_marcar = falhar_ao_marcar

    def salvar(self, vaga: Vaga) -> Vaga:
        if self._falhar_ao_salvar:
            raise FalhaDeBanco("falha ao salvar a vaga")
        self.vagas.append(vaga)
        return vaga

    def listar_nao_convertidas(self, perfil_identificador: str) -> tuple[Vaga, ...]:
        return tuple(vaga for vaga in self.vagas if vaga.id not in self.convertidas)

    def marcar_como_convertida(self, vaga_id: str) -> None:
        if self._falhar_ao_marcar:
            raise FalhaDeBanco("falha ao marcar a vaga")
        self.convertidas.add(vaga_id)


class CurriculoSalvoRepositoryFake(CurriculoSalvoRepository):
    def __init__(self, quantidade_inicial: int = 0, falhar_ao_remover: bool = False) -> None:
        self.curriculos: list[CurriculoSalvo] = []
        self.removidos: list[str] = []
        self._quantidade_inicial = quantidade_inicial
        self._falhar_ao_remover = falhar_ao_remover

    def salvar(self, curriculo: CurriculoSalvo) -> CurriculoSalvo:
        self.curriculos.append(curriculo)
        return curriculo

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[CurriculoSalvo, ...]:
        return tuple(c for c in self.curriculos if c.id not in self.removidos)

    def remover(self, curriculo_id: str, perfil_identificador: str) -> None:
        if self._falhar_ao_remover:
            raise FalhaDeBanco("falha ao remover o currículo")
        self.removidos.append(curriculo_id)

    def contar_por_perfil(self, perfil_identificador: str) -> int:
        return self._quantidade_inicial + len(self.listar_por_perfil(perfil_identificador))


def _dto(**overrides) -> ConfirmarCandidaturaAjustadaInputDto:
    dados = dict(
        perfil_identificador="ana",
        cargo="Engenheiro de Software",
        empresa="TechCorp",
        descricao_vaga=DESCRICAO_DA_VAGA,
        nome_arquivo="AnaSouza-2026-11-09-Engenheiro-TechCorp.pdf",
        pdf_bytes=PDF,
    )
    dados.update(overrides)
    return ConfirmarCandidaturaAjustadaInputDto(**dados)


def _caso_de_uso(candidaturas=None, vagas=None, curriculos=None) -> ConfirmarCandidaturaAjustada:
    return ConfirmarCandidaturaAjustada(
        repositorio_candidatura=candidaturas or CandidaturaRepositoryFake(),
        repositorio_vaga=vagas or VagaRepositoryFake(),
        repositorio_curriculo_salvo=curriculos or CurriculoSalvoRepositoryFake(),
    )


class TestConfirmarCandidaturaAjustada:
    def test_cria_candidatura_aplicada_com_empresa_cargo_e_o_pdf_gerado_vinculado(self):
        candidaturas, vagas, curriculos = CandidaturaRepositoryFake(), VagaRepositoryFake(), CurriculoSalvoRepositoryFake()

        candidatura = _caso_de_uso(candidaturas, vagas, curriculos).executar(_dto())

        curriculo = curriculos.curriculos[0]
        assert candidaturas.candidaturas == [candidatura]
        assert candidatura.status == StatusCandidatura.APLICADO
        assert candidatura.empresa == "TechCorp"
        assert candidatura.cargo == "Engenheiro de Software"
        assert candidatura.perfil_identificador == "ana"
        assert candidatura.curriculo_salvo_id == curriculo.id
        assert curriculo.pdf_bytes == PDF
        assert curriculo.nome_referencia == "AnaSouza-2026-11-09-Engenheiro-TechCorp.pdf"
        assert curriculo.perfil_identificador == "ana"

    def test_guarda_a_descricao_da_vaga_ligada_a_candidatura(self):
        vagas = VagaRepositoryFake()

        candidatura = _caso_de_uso(vagas=vagas).executar(_dto())

        assert len(vagas.vagas) == 1
        assert vagas.vagas[0].id == candidatura.vaga_id
        assert vagas.vagas[0].texto_descricao == DESCRICAO_DA_VAGA
        assert vagas.vagas[0].perfil_identificador == "ana"

    def test_marca_a_vaga_como_convertida_e_ela_nao_aparece_em_vagas_salvas(self):
        vagas = VagaRepositoryFake()

        candidatura = _caso_de_uso(vagas=vagas).executar(_dto())

        assert candidatura.vaga_id in vagas.convertidas
        assert vagas.listar_nao_convertidas("ana") == ()

    def test_biblioteca_cheia_levanta_o_limite_e_nao_grava_nada(self):
        candidaturas, vagas = CandidaturaRepositoryFake(), VagaRepositoryFake()
        curriculos = CurriculoSalvoRepositoryFake(quantidade_inicial=LIMITE_CURRICULOS_POR_PERFIL)

        with pytest.raises(LimiteCurriculosSalvosExcedido):
            _caso_de_uso(candidaturas, vagas, curriculos).executar(_dto())

        assert candidaturas.candidaturas == []
        assert vagas.vagas == []
        assert curriculos.curriculos == []

    def test_aceita_o_decimo_curriculo(self):
        curriculos = CurriculoSalvoRepositoryFake(quantidade_inicial=LIMITE_CURRICULOS_POR_PERFIL - 1)

        candidatura = _caso_de_uso(curriculos=curriculos).executar(_dto())

        assert candidatura.status == StatusCandidatura.APLICADO

    def test_falha_ao_salvar_a_vaga_remove_o_curriculo_e_nao_cria_candidatura(self):
        candidaturas, curriculos = CandidaturaRepositoryFake(), CurriculoSalvoRepositoryFake()

        with pytest.raises(FalhaDeBanco, match="vaga"):
            _caso_de_uso(candidaturas, VagaRepositoryFake(falhar_ao_salvar=True), curriculos).executar(_dto())

        assert curriculos.removidos == [curriculos.curriculos[0].id]
        assert curriculos.listar_por_perfil("ana") == ()
        assert candidaturas.candidaturas == []

    def test_falha_ao_marcar_a_vaga_remove_o_curriculo_e_nao_cria_candidatura(self):
        candidaturas, curriculos = CandidaturaRepositoryFake(), CurriculoSalvoRepositoryFake()

        with pytest.raises(FalhaDeBanco, match="marcar"):
            _caso_de_uso(candidaturas, VagaRepositoryFake(falhar_ao_marcar=True), curriculos).executar(_dto())

        assert curriculos.removidos == [curriculos.curriculos[0].id]
        assert candidaturas.candidaturas == []

    def test_falha_ao_salvar_a_candidatura_remove_o_curriculo_e_deixa_a_vaga_convertida(self):
        vagas, curriculos = VagaRepositoryFake(), CurriculoSalvoRepositoryFake()

        with pytest.raises(FalhaDeBanco, match="candidatura"):
            _caso_de_uso(CandidaturaRepositoryFake(falhar_ao_salvar=True), vagas, curriculos).executar(_dto())

        assert curriculos.removidos == [curriculos.curriculos[0].id]
        assert vagas.listar_nao_convertidas("ana") == ()

    def test_falha_na_compensacao_nao_esconde_o_erro_original_e_registra_aviso(self, caplog):
        curriculos = CurriculoSalvoRepositoryFake(falhar_ao_remover=True)
        vagas = VagaRepositoryFake(falhar_ao_salvar=True)

        with caplog.at_level(logging.WARNING):
            with pytest.raises(FalhaDeBanco, match="salvar a vaga"):
                _caso_de_uso(vagas=vagas, curriculos=curriculos).executar(_dto())

        assert "não foi possível remover" in caplog.text.lower()

    @pytest.mark.parametrize(
        ("campo", "valor"),
        [
            ("perfil_identificador", "  "),
            ("cargo", ""),
            ("empresa", "   "),
            ("descricao_vaga", ""),
            ("nome_arquivo", " "),
            ("pdf_bytes", b""),
            ("pdf_bytes", b"nao e um pdf"),
        ],
    )
    def test_dados_invalidos_levantam_value_error_e_nao_gravam_nada(self, campo, valor):
        candidaturas, vagas, curriculos = CandidaturaRepositoryFake(), VagaRepositoryFake(), CurriculoSalvoRepositoryFake()

        with pytest.raises(ValueError):
            _caso_de_uso(candidaturas, vagas, curriculos).executar(_dto(**{campo: valor}))

        assert candidaturas.candidaturas == []
        assert vagas.vagas == []
        assert curriculos.curriculos == []

    def test_log_informa_identificadores_e_tamanho_sem_dados_pessoais(self, caplog):
        with caplog.at_level(logging.INFO):
            candidatura = _caso_de_uso().executar(_dto())

        assert candidatura.id in caplog.text
        assert f"pdf_bytes={len(PDF)}" in caplog.text
        for sigiloso in (DESCRICAO_DA_VAGA, "TechCorp", "Engenheiro de Software", "AnaSouza", "%PDF"):
            assert sigiloso not in caplog.text
