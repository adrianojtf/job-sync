import pytest

from jobsync.perfil_estruturado.domain.blocos_experiencia import (
    BlocosExperiencia,
    ReconhecedorBlocosExperiencia,
)
from jobsync.shared_kernel.domain.rotulos_blocos_experiencia import BlocoExperiencia

STARIAN = """\
Context: At Starian, one of Brazil's leading ERP companies, I develop financial modules.
Key Responsibilities:
- End-to-end ownership of features within an enterprise ERP platform.
- Technical design, implementation, testing, and delivery.
Key Achievements:
- Contributed to the evolution of ERP financial capabilities supporting more than 1,000 users.
Technologies: Java | PostgreSQL | SQL | REST APIs | React | ERP"""


class TestReconhecedorBlocosExperiencia:
    def test_reconhece_os_quatro_blocos_em_ingles_sem_resto(self):
        resultado = ReconhecedorBlocosExperiencia().reconhecer(STARIAN)

        assert resultado.blocos.contexto.startswith("At Starian, one of Brazil's leading ERP")
        assert resultado.blocos.responsabilidades == (
            "End-to-end ownership of features within an enterprise ERP platform.",
            "Technical design, implementation, testing, and delivery.",
        )
        assert resultado.blocos.realizacoes == (
            "Contributed to the evolution of ERP financial capabilities supporting more than 1,000 users.",
        )
        assert resultado.blocos.skills == ("Java", "PostgreSQL", "SQL", "REST APIs", "React", "ERP")
        assert resultado.resto == ""
        assert resultado.blocos.completos is True

    def test_reconhece_os_rotulos_em_portugues(self):
        resultado = ReconhecedorBlocosExperiencia().reconhecer(
            "Contexto: ERP financeiro.\n"
            "Principais responsabilidades:\n- Projetar telas\n"
            "Principais realizações:\n- Atendi 1.000 usuários\n"
            "Tecnologias: Java, SQL"
        )

        assert resultado.blocos.contexto == "ERP financeiro."
        assert resultado.blocos.responsabilidades == ("Projetar telas",)
        assert resultado.blocos.realizacoes == ("Atendi 1.000 usuários",)
        assert resultado.blocos.skills == ("Java", "SQL")

    def test_reconhece_apelidos_dos_rotulos(self):
        resultado = ReconhecedorBlocosExperiencia().reconhecer("Principais entregas:\n- Reduzi custos\nSkills: Java")

        assert resultado.blocos.realizacoes == ("Reduzi custos",)
        assert resultado.blocos.skills == ("Java",)

    def test_texto_sem_rotulos_vira_resto_e_nenhum_bloco(self):
        texto = "Desenvolvi APIs em Java.\n- Reduzi o tempo de resposta."

        resultado = ReconhecedorBlocosExperiencia().reconhecer(texto)

        assert resultado.blocos == BlocosExperiencia()
        assert resultado.resto == texto
        assert resultado.blocos.ausentes == tuple(BlocoExperiencia)

    def test_blocos_parciais_deixam_os_demais_ausentes(self):
        resultado = ReconhecedorBlocosExperiencia().reconhecer("Technologies: Java | SQL")

        assert resultado.blocos.skills == ("Java", "SQL")
        assert resultado.blocos.ausentes == (
            BlocoExperiencia.CONTEXTO,
            BlocoExperiencia.RESPONSABILIDADES,
            BlocoExperiencia.REALIZACOES,
        )

    def test_texto_antes_do_primeiro_rotulo_vira_resto(self):
        resultado = ReconhecedorBlocosExperiencia().reconhecer("Atuei em fintech.\nKey Achievements:\n- Reduzi custos")

        assert resultado.resto == "Atuei em fintech."
        assert resultado.blocos.realizacoes == ("Reduzi custos",)

    def test_contexto_em_varias_linhas_vira_um_paragrafo(self):
        resultado = ReconhecedorBlocosExperiencia().reconhecer("Context: Empresa de ERP\npara a construção civil.")

        assert resultado.blocos.contexto == "Empresa de ERP para a construção civil."

    def test_linha_continuada_de_um_item_se_junta_ao_item(self):
        resultado = ReconhecedorBlocosExperiencia().reconhecer(
            "Key Responsibilities:\n- Projetar telas\n  do contas a receber\n- Testar"
        )

        assert resultado.blocos.responsabilidades == ("Projetar telas do contas a receber", "Testar")

    def test_item_na_mesma_linha_do_rotulo_e_reconhecido(self):
        resultado = ReconhecedorBlocosExperiencia().reconhecer("Key Achievements: Reduzi custos em 20%.")

        assert resultado.blocos.realizacoes == ("Reduzi custos em 20%.",)

    def test_rotulo_dentro_de_bullet_nao_abre_bloco(self):
        resultado = ReconhecedorBlocosExperiencia().reconhecer("Key Achievements:\n- Technologies: Java")

        assert resultado.blocos.realizacoes == ("Technologies: Java",)
        assert resultado.blocos.skills == ()

    def test_skills_repetidas_aparecem_uma_vez(self):
        resultado = ReconhecedorBlocosExperiencia().reconhecer("Technologies: Java | java | SQL")

        assert resultado.blocos.skills == ("Java", "SQL")

    @pytest.mark.parametrize("texto", ["", "   \n  "])
    def test_texto_vazio_nao_reconhece_nada(self, texto):
        resultado = ReconhecedorBlocosExperiencia().reconhecer(texto)

        assert resultado.blocos == BlocosExperiencia()
        assert resultado.resto == ""


class TestBlocosExperiencia:
    def test_completado_com_mantem_os_blocos_presentes(self):
        reconhecidos = BlocosExperiencia(contexto="Original.", skills=("Java",))
        gerados = BlocosExperiencia(
            contexto="Gerado.", responsabilidades=("Gerada",), realizacoes=("Gerada",), skills=("Go",)
        )

        resultado = reconhecidos.completado_com(gerados)

        assert resultado == BlocosExperiencia(
            contexto="Original.", responsabilidades=("Gerada",), realizacoes=("Gerada",), skills=("Java",)
        )
