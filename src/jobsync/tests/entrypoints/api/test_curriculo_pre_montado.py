from jobsync.entrypoints.api.curriculo_pre_montado import experiencias_do_perfil
from jobsync.perfil_estruturado import Conquista, ExperienciaProfissional, PerfilEstruturado


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
        tecnologias=(),
    )


class TestExperienciasDoPerfil:
    def test_leva_os_quatro_blocos_para_a_experiencia_de_avaliacao(self):
        perfil = _perfil(
            ExperienciaProfissional(
                "Starian", "Dev", "2024", "",
                conquistas=(Conquista("Atendi 1.000 usuários"),),
                contexto="ERP financeiro.",
                responsabilidades=("Projetar telas",),
                skills=("Java", "SQL"),
            )
        )

        (experiencia,) = experiencias_do_perfil(perfil)

        assert experiencia.contexto == "ERP financeiro."
        assert experiencia.responsabilidades == ("Projetar telas",)
        assert experiencia.conquistas == ("Atendi 1.000 usuários",)
        assert experiencia.skills == ("Java", "SQL")

    def test_perfil_sem_experiencias_devolve_none(self):
        assert experiencias_do_perfil(_perfil()) is None
