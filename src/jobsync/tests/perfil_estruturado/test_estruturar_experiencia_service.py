from jobsync.perfil_estruturado.domain.blocos_experiencia import BlocosExperiencia, ExperienciaParaCompletar
from jobsync.perfil_estruturado.domain.completador_blocos_experiencia_port import (
    CompletadorBlocosExperienciaPort,
)
from jobsync.perfil_estruturado.domain.estruturar_experiencia_service import EstruturarExperienciaService
from jobsync.perfil_estruturado.domain.exceptions import CompletarBlocosIndisponivel
from jobsync.perfil_estruturado.domain.perfil_estruturado import Conquista, ExperienciaProfissional

GERADOS = BlocosExperiencia(
    contexto="Contexto gerado.",
    responsabilidades=("Responsabilidade gerada.",),
    realizacoes=("Realização gerada.",),
    skills=("Skill gerada",),
)


class CompletadorFake(CompletadorBlocosExperienciaPort):
    def __init__(self, gerados: BlocosExperiencia = GERADOS, erro: Exception | None = None):
        self._gerados = gerados
        self._erro = erro
        self.chamadas: list[tuple[ExperienciaParaCompletar, str | None]] = []

    def completar(self, experiencia: ExperienciaParaCompletar, idioma: str | None = None) -> BlocosExperiencia:
        self.chamadas.append((experiencia, idioma))
        if self._erro is not None:
            raise self._erro
        return self._gerados


def _experiencia(descricao: str, **extras) -> ExperienciaProfissional:
    return ExperienciaProfissional(empresa="Starian", cargo="Dev", periodo="2024 - Atual", descricao=descricao, **extras)


COMPLETA = (
    "Context: ERP.\nKey Responsibilities:\n- Projetar\nKey Achievements:\n- Atendi 1.000 usuários\nTechnologies: Java | SQL"
)


class TestEstruturarExperienciaService:
    def test_blocos_todos_reconhecidos_nao_chamam_a_ia(self):
        completador = CompletadorFake()

        resultado = EstruturarExperienciaService(completador).executar(_experiencia(COMPLETA))

        assert completador.chamadas == []
        assert resultado.contexto == "ERP."
        assert resultado.responsabilidades == ("Projetar",)
        assert [c.texto for c in resultado.conquistas] == ["Atendi 1.000 usuários"]
        assert resultado.skills == ("Java", "SQL")
        assert resultado.descricao == ""

    def test_a_ia_recebe_so_o_que_falta_e_o_reconhecido_prevalece(self):
        completador = CompletadorFake()

        resultado = EstruturarExperienciaService(completador).executar(
            _experiencia("Technologies: Java | SQL\nAtuei em fintech."), idioma="pt"
        )

        (pedido, idioma), = completador.chamadas
        assert pedido.reconhecidos.skills == ("Java", "SQL")
        assert pedido.resto == "Atuei em fintech."
        assert pedido.cargo == "Dev"
        assert idioma == "pt"
        assert resultado.skills == ("Java", "SQL")
        assert resultado.contexto == "Contexto gerado."
        assert resultado.responsabilidades == ("Responsabilidade gerada.",)
        assert [c.texto for c in resultado.conquistas] == ["Realização gerada."]
        assert resultado.descricao == ""

    def test_descricao_sem_rotulos_vai_toda_para_a_ia(self):
        completador = CompletadorFake()

        EstruturarExperienciaService(completador).executar(_experiencia("Desenvolvi APIs em Java."))

        (pedido, _), = completador.chamadas
        assert pedido.resto == "Desenvolvi APIs em Java."
        assert pedido.reconhecidos == BlocosExperiencia()

    def test_falha_da_ia_mantem_os_reconhecidos_e_o_resto_na_descricao(self):
        completador = CompletadorFake(erro=CompletarBlocosIndisponivel())

        resultado = EstruturarExperienciaService(completador).executar(
            _experiencia("Technologies: Java\nAtuei em fintech.")
        )

        assert resultado.skills == ("Java",)
        assert resultado.contexto == ""
        assert resultado.descricao == "Atuei em fintech."

    def test_sem_completador_so_reconhece(self):
        resultado = EstruturarExperienciaService(None).executar(_experiencia("Technologies: Java"))

        assert resultado.skills == ("Java",)

    def test_blocos_ja_preenchidos_no_perfil_prevalecem_sobre_o_texto(self):
        completador = CompletadorFake()
        experiencia = _experiencia(
            "Context: Do texto.\nTechnologies: Go",
            contexto="Do perfil.",
            conquistas=(Conquista("Já cadastrada."),),
            responsabilidades=("Do perfil",),
            skills=("Java",),
        )

        resultado = EstruturarExperienciaService(completador).executar(experiencia)

        assert completador.chamadas == []
        assert resultado.contexto == "Do perfil."
        assert resultado.skills == ("Java",)
        assert [c.texto for c in resultado.conquistas] == ["Já cadastrada."]

    def test_preserva_cargo_empresa_e_periodo(self):
        resultado = EstruturarExperienciaService(CompletadorFake()).executar(_experiencia("Algo."))

        assert (resultado.empresa, resultado.cargo, resultado.periodo) == ("Starian", "Dev", "2024 - Atual")

    def test_realizacoes_repetidas_viram_uma_conquista(self):
        resultado = EstruturarExperienciaService(None).executar(
            _experiencia("Key Achievements:\n- Reduzi custos.\n- reduzi custos")
        )

        assert [c.texto for c in resultado.conquistas] == ["Reduzi custos."]
