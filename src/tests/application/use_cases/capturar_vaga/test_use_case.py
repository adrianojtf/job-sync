"""Testes do caso de uso CapturarVaga."""

from application.use_cases.capturar_vaga import CapturarVaga, CapturarVagaInputDto
from domain.vaga import Vaga
from domain.vaga.vaga_repository import VagaRepository


class VagaRepositoryFake(VagaRepository):
    def __init__(self) -> None:
        self.vagas_salvas: list[Vaga] = []

    def salvar(self, vaga: Vaga) -> Vaga:
        self.vagas_salvas.append(vaga)
        return vaga

    def listar_nao_convertidas(self, perfil_identificador: str) -> tuple[Vaga, ...]:
        return tuple(v for v in self.vagas_salvas if v.perfil_identificador == perfil_identificador)

    def marcar_como_convertida(self, vaga_id: str) -> None:
        raise NotImplementedError


class TestCapturarVaga:
    def test_persiste_vaga_com_id_unico_e_data_captura(self):
        repositorio = VagaRepositoryFake()
        use_case = CapturarVaga(repositorio_vaga=repositorio)

        vaga = use_case.executar(
            CapturarVagaInputDto(
                perfil_identificador="matheus",
                texto_descricao="Vaga para Engenheiro de Software",
                url_origem="https://exemplo.com/vaga/1",
            )
        )

        assert vaga.id
        assert vaga.perfil_identificador == "matheus"
        assert vaga.texto_descricao == "Vaga para Engenheiro de Software"
        assert vaga.url_origem == "https://exemplo.com/vaga/1"
        assert vaga.data_captura is not None
        assert repositorio.vagas_salvas == [vaga]

    def test_url_origem_e_opcional(self):
        repositorio = VagaRepositoryFake()
        use_case = CapturarVaga(repositorio_vaga=repositorio)

        vaga = use_case.executar(
            CapturarVagaInputDto(perfil_identificador="matheus", texto_descricao="Vaga colada manualmente")
        )

        assert vaga.url_origem is None
