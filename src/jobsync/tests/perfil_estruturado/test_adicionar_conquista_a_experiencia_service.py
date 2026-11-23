"""Testes do caso de uso AdicionarConquistaAExperiencia."""
import pytest

from jobsync.perfil_estruturado import ExperienciaProfissional, OrigemConquista, PerfilEstruturado
from jobsync.perfil_estruturado.adapters.perfil_estruturado_repository_fake import (
    PerfilEstruturadoRepositoryFake,
)
from jobsync.perfil_estruturado.domain.exceptions import ExperienciaNaoEncontrada, PerfilEstruturadoNaoEncontrado
from jobsync.perfil_estruturado.service_layer.adicionar_conquista_a_experiencia import (
    AdicionarConquistaAExperiencia,
    AdicionarConquistaAExperienciaInputDto,
)


def _perfil() -> PerfilEstruturado:
    return PerfilEstruturado(
        perfil_identificador="adriano",
        nome_completo="Adriano Teixeira",
        email="adriano@email.com",
        linkedin="",
        resumo_profissional="Backend.",
        experiencias=(
            ExperienciaProfissional("Neoway", "Dev Java", "2020", "APIs."),
            ExperienciaProfissional("TechCorp", "Engenheiro", "2022", "Backend."),
        ),
        formacoes=(),
        certificacoes=(),
        idiomas=(),
        tecnologias=("Java",),
    )


@pytest.fixture
def repositorio() -> PerfilEstruturadoRepositoryFake:
    repositorio = PerfilEstruturadoRepositoryFake()
    repositorio.salvar(_perfil())
    return repositorio


def _entrada(indice: int = 1, texto: str = "Atuei com o cliente em um MVP.", perfil: str = "adriano"):
    return AdicionarConquistaAExperienciaInputDto(perfil_identificador=perfil, experiencia_indice=indice, texto=texto)


class TestAdicionarConquistaAExperiencia:
    def test_grava_a_conquista_com_origem_resposta_a_pergunta(self, repositorio):
        AdicionarConquistaAExperiencia(repositorio).executar(_entrada())

        salvo = repositorio.buscar_por_perfil("adriano")
        conquista = salvo.experiencias[1].conquistas[0]
        assert conquista.texto == "Atuei com o cliente em um MVP."
        assert conquista.origem == OrigemConquista.RESPOSTA_PERGUNTA

    def test_devolve_o_perfil_atualizado(self, repositorio):
        atualizado = AdicionarConquistaAExperiencia(repositorio).executar(_entrada())

        assert atualizado == repositorio.buscar_por_perfil("adriano")

    def test_nao_altera_o_resto_do_perfil(self, repositorio):
        AdicionarConquistaAExperiencia(repositorio).executar(_entrada())

        salvo = repositorio.buscar_por_perfil("adriano")
        original = _perfil()
        assert salvo.experiencias[0] == original.experiencias[0]
        assert (salvo.resumo_profissional, salvo.tecnologias) == (original.resumo_profissional, original.tecnologias)

    def test_perfil_inexistente_levanta_erro(self, repositorio):
        with pytest.raises(PerfilEstruturadoNaoEncontrado):
            AdicionarConquistaAExperiencia(repositorio).executar(_entrada(perfil="outro"))

    def test_experiencia_inexistente_levanta_erro_sem_gravar(self, repositorio):
        with pytest.raises(ExperienciaNaoEncontrada):
            AdicionarConquistaAExperiencia(repositorio).executar(_entrada(indice=5))

        assert repositorio.buscar_por_perfil("adriano") == _perfil()

    @pytest.mark.parametrize("texto", ["", "   "])
    def test_texto_vazio_levanta_erro_sem_gravar(self, repositorio, texto):
        with pytest.raises(ValueError, match="conquista"):
            AdicionarConquistaAExperiencia(repositorio).executar(_entrada(texto=texto))

        assert repositorio.buscar_por_perfil("adriano") == _perfil()

    def test_conquista_duplicada_levanta_erro(self, repositorio):
        servico = AdicionarConquistaAExperiencia(repositorio)
        servico.executar(_entrada())

        with pytest.raises(ValueError, match="duplicadas"):
            servico.executar(_entrada(texto="atuei com o CLIENTE em um MVP"))
