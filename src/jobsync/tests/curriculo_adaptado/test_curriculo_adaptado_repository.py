"""Contrato do CurriculoAdaptadoRepository, verificado no fake e no PostgreSQL."""
import pytest

from jobsync.curriculo_adaptado.adapters import (
    CurriculoAdaptadoRepositoryFake,
    CurriculoAdaptadoRepositoryImpl,
)
from jobsync.perfil.adapters.perfil_repository_impl import PerfilRepositoryImpl
from jobsync.tests.curriculo_adaptado.exemplos import AGORA, DEPOIS, curriculo_adaptado, rascunho


@pytest.fixture(params=["fake", "postgres"])
def repositorio(request):
    if request.param == "fake":
        return CurriculoAdaptadoRepositoryFake()
    pool = request.getfixturevalue("pool_postgres")
    PerfilRepositoryImpl(pool).criar("ana")
    PerfilRepositoryImpl(pool).criar("outra-pessoa")
    return CurriculoAdaptadoRepositoryImpl(pool)


class TestCurriculoAdaptadoRepository:
    def test_salvar_e_buscar_devolvem_o_mesmo_curriculo_completo(self, repositorio):
        curriculo = curriculo_adaptado()

        repositorio.salvar(curriculo)

        assert repositorio.buscar(curriculo.id, "ana") == curriculo

    def test_buscar_inexistente_devolve_none(self, repositorio):
        assert repositorio.buscar("nao-existe", "ana") is None

    def test_buscar_com_o_id_de_outro_perfil_devolve_none(self, repositorio):
        repositorio.salvar(curriculo_adaptado())

        assert repositorio.buscar("adaptado-1", "outra-pessoa") is None

    def test_salvar_com_o_mesmo_id_substitui_o_conteudo(self, repositorio):
        original = curriculo_adaptado()
        repositorio.salvar(original)
        editado = original.com_rascunho_revisado(
            rascunho().__class__.revisado(
                nome_completo="Ana Souza",
                email="ana@ex.com",
                linkedin="",
                secoes=(),
                experiencias=None,
                competencias=(("Linguagens", ("Go",)),),
            ),
            DEPOIS,
        )

        repositorio.salvar(editado)

        assert repositorio.buscar(original.id, "ana") == editado
        assert len(repositorio.listar_por_perfil("ana")) == 1

    def test_listar_traz_so_os_do_perfil_do_mais_recente_para_o_mais_antigo(self, repositorio):
        antigo = curriculo_adaptado(id="a-1", atualizado_em=AGORA)
        recente = curriculo_adaptado(id="a-2", atualizado_em=DEPOIS)
        repositorio.salvar(antigo)
        repositorio.salvar(recente)
        repositorio.salvar(curriculo_adaptado(id="a-3", perfil_identificador="outra-pessoa"))

        assert repositorio.listar_por_perfil("ana") == (recente, antigo)

    def test_listar_sem_curriculos_devolve_tupla_vazia(self, repositorio):
        assert repositorio.listar_por_perfil("ana") == ()

    def test_vincular_guarda_o_id_do_curriculo_salvo(self, repositorio):
        repositorio.salvar(curriculo_adaptado())

        repositorio.vincular_curriculo_salvo("adaptado-1", "ana", "salvo-9")

        assert repositorio.buscar("adaptado-1", "ana").curriculo_salvo_id == "salvo-9"

    def test_vincular_com_o_perfil_errado_nao_altera_nada(self, repositorio):
        repositorio.salvar(curriculo_adaptado())

        repositorio.vincular_curriculo_salvo("adaptado-1", "outra-pessoa", "salvo-9")

        assert repositorio.buscar("adaptado-1", "ana").curriculo_salvo_id is None

    def test_salvar_de_novo_preserva_o_vinculo_quando_ele_vem_no_agregado(self, repositorio):
        vinculado = curriculo_adaptado().com_curriculo_salvo("salvo-9")
        repositorio.salvar(vinculado)

        repositorio.salvar(vinculado.com_rascunho_revisado(rascunho(), DEPOIS))

        assert repositorio.buscar("adaptado-1", "ana").curriculo_salvo_id == "salvo-9"
