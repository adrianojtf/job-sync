import pytest

from jobsync.perfil_estruturado import ExperienciaProfissional, PerfilEstruturado
from jobsync.perfil_estruturado.adapters.perfil_estruturado_repository_fake import (
    PerfilEstruturadoRepositoryFake,
)
from jobsync.perfil_estruturado.domain.blocos_experiencia import BlocosExperiencia, ExperienciaParaCompletar
from jobsync.perfil_estruturado.domain.completador_blocos_experiencia_port import (
    CompletadorBlocosExperienciaPort,
)
from jobsync.perfil_estruturado.domain.estruturar_experiencia_service import EstruturarExperienciaService
from jobsync.perfil_estruturado.domain.exceptions import PerfilEstruturadoNaoEncontrado
from jobsync.perfil_estruturado.service_layer.migrar_experiencias_do_perfil import (
    MigrarExperienciasDoPerfil,
    MigrarExperienciasDoPerfilInputDto,
)


class CompletadorFake(CompletadorBlocosExperienciaPort):
    def __init__(self):
        self.pedidos: list[ExperienciaParaCompletar] = []

    def completar(self, experiencia: ExperienciaParaCompletar, idioma: str | None = None) -> BlocosExperiencia:
        self.pedidos.append(experiencia)
        return BlocosExperiencia(
            contexto="Contexto gerado.",
            responsabilidades=("Responsabilidade gerada.",),
            realizacoes=("Realização gerada.",),
            skills=("Skill gerada",),
        )


def _perfil(*experiencias: ExperienciaProfissional) -> PerfilEstruturado:
    return PerfilEstruturado(
        perfil_identificador="adriano",
        nome_completo="Adriano",
        email="adriano@email.com",
        linkedin="",
        resumo_profissional="",
        experiencias=experiencias,
        formacoes=(),
        certificacoes=(),
        idiomas=(),
        tecnologias=("Java",),
    )


LEGADA = ExperienciaProfissional("Neoway", "Dev Java", "2020", "Desenvolvi APIs em Java.")
ESTRUTURADA = ExperienciaProfissional("Starian", "Dev", "2024", "", contexto="ERP.", skills=("Java",))


@pytest.fixture
def repositorio() -> PerfilEstruturadoRepositoryFake:
    return PerfilEstruturadoRepositoryFake()


class TestMigrarExperienciasDoPerfil:
    def test_migra_so_as_experiencias_legadas_e_devolve_o_rascunho(self, repositorio):
        repositorio.salvar(_perfil(LEGADA, ESTRUTURADA))
        completador = CompletadorFake()
        use_case = MigrarExperienciasDoPerfil(repositorio, EstruturarExperienciaService(completador))

        rascunho = use_case.executar(MigrarExperienciasDoPerfilInputDto(perfil_identificador="adriano"))

        migrada, intacta = rascunho.experiencias
        assert migrada.contexto == "Contexto gerado."
        assert migrada.descricao == ""
        assert (migrada.empresa, migrada.cargo, migrada.periodo) == ("Neoway", "Dev Java", "2020")
        assert intacta == ESTRUTURADA
        assert [pedido.empresa for pedido in completador.pedidos] == ["Neoway"]

    def test_nao_grava_o_rascunho(self, repositorio):
        repositorio.salvar(_perfil(LEGADA))
        use_case = MigrarExperienciasDoPerfil(repositorio, EstruturarExperienciaService(CompletadorFake()))

        use_case.executar(MigrarExperienciasDoPerfilInputDto(perfil_identificador="adriano"))

        assert repositorio.buscar_por_perfil("adriano").experiencias == (LEGADA,)

    def test_perfil_sem_experiencias_legadas_nao_chama_a_ia(self, repositorio):
        repositorio.salvar(_perfil(ESTRUTURADA))
        completador = CompletadorFake()
        use_case = MigrarExperienciasDoPerfil(repositorio, EstruturarExperienciaService(completador))

        rascunho = use_case.executar(MigrarExperienciasDoPerfilInputDto(perfil_identificador="adriano"))

        assert rascunho.experiencias == (ESTRUTURADA,)
        assert completador.pedidos == []

    def test_perfil_inexistente_levanta_erro(self, repositorio):
        use_case = MigrarExperienciasDoPerfil(repositorio, EstruturarExperienciaService(CompletadorFake()))

        with pytest.raises(PerfilEstruturadoNaoEncontrado):
            use_case.executar(MigrarExperienciasDoPerfilInputDto(perfil_identificador="nao-existe"))

    def test_identificador_vazio_levanta_erro(self, repositorio):
        use_case = MigrarExperienciasDoPerfil(repositorio, EstruturarExperienciaService(CompletadorFake()))

        with pytest.raises(ValueError, match="identificador"):
            use_case.executar(MigrarExperienciasDoPerfilInputDto(perfil_identificador=" "))
