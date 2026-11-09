"""Testes dos Value Objects de equivalência de tecnologias e do PlanoAdaptacao."""
import pytest

from jobsync.curriculo import (
    AjusteTecnologia,
    DiretrizesExperiencia,
    EquivalenciaTecnologia,
    ExperienciaParaAvaliacao,
    ManutencaoTecnologia,
    PlanoAdaptacao,
)

REACT_ANGULAR = EquivalenciaTecnologia(original="React", alvo="Angular")


def _experiencia(descricao: str, cargo: str = "Dev") -> ExperienciaParaAvaliacao:
    return ExperienciaParaAvaliacao(descricao=descricao, cargo=cargo, empresa="Empresa", periodo="2024")


class TestEquivalenciaTecnologia:
    def test_apara_os_nomes(self):
        equivalencia = EquivalenciaTecnologia(original="  React ", alvo=" Angular  ")

        assert equivalencia == REACT_ANGULAR

    @pytest.mark.parametrize("original, alvo", [("", "Angular"), ("React", "  ")])
    def test_nome_vazio_gera_erro(self, original, alvo):
        with pytest.raises(ValueError, match="tecnologia"):
            EquivalenciaTecnologia(original=original, alvo=alvo)

    def test_original_igual_ao_alvo_gera_erro(self):
        with pytest.raises(ValueError, match="diferentes"):
            EquivalenciaTecnologia(original="React", alvo="react")


class TestPlanoAdaptacao:
    def test_uma_ocorrencia_recebe_a_troca(self):
        plano = PlanoAdaptacao.distribuir([_experiencia("Front-end em React e Java.")], [REACT_ANGULAR])

        assert plano.ajustes == (AjusteTecnologia(indice_experiencia=0, equivalencia=REACT_ANGULAR),)
        assert plano.manutencoes == ()
        assert plano.diretrizes(0) == DiretrizesExperiencia(trocar=(REACT_ANGULAR,))

    def test_duas_ocorrencias_trocam_na_primeira_e_mantem_na_ultima(self):
        experiencias = [_experiencia("Usei React."), _experiencia("Telas em react.")]

        plano = PlanoAdaptacao.distribuir(experiencias, [REACT_ANGULAR])

        assert plano.diretrizes(0) == DiretrizesExperiencia(trocar=(REACT_ANGULAR,))
        assert plano.diretrizes(1) == DiretrizesExperiencia(manter=("React",))
        assert plano.manutencoes == (ManutencaoTecnologia(indice_experiencia=1, tecnologia="React"),)

    def test_tres_ocorrencias_mantem_a_original_so_na_ultima(self):
        experiencias = [_experiencia("React"), _experiencia("Go"), _experiencia("React"), _experiencia("React")]

        plano = PlanoAdaptacao.distribuir(experiencias, [REACT_ANGULAR])

        assert [ajuste.indice_experiencia for ajuste in plano.ajustes] == [0, 2]
        assert plano.diretrizes(1) == DiretrizesExperiencia()
        assert plano.diretrizes(3) == DiretrizesExperiencia(manter=("React",))

    def test_alvo_ja_presente_no_perfil_descarta_a_troca(self):
        experiencias = [_experiencia("Usei React."), _experiencia("Usei Angular.")]

        plano = PlanoAdaptacao.distribuir(experiencias, [REACT_ANGULAR])

        assert plano == PlanoAdaptacao.vazio()

    def test_compara_por_palavra_inteira(self):
        java_kotlin = EquivalenciaTecnologia(original="Java", alvo="Kotlin")

        plano = PlanoAdaptacao.distribuir([_experiencia("Front-end em JavaScript.")], [java_kotlin])

        assert plano == PlanoAdaptacao.vazio()

    def test_reconhece_tecnologias_com_simbolos(self):
        dotnet_java = EquivalenciaTecnologia(original=".NET", alvo="Java")

        plano = PlanoAdaptacao.distribuir([_experiencia("APIs em .NET e C#.")], [dotnet_java])

        assert plano.diretrizes(0) == DiretrizesExperiencia(trocar=(dotnet_java,))

    def test_procura_a_tecnologia_tambem_no_cargo(self):
        plano = PlanoAdaptacao.distribuir(
            [_experiencia("Criei telas.", cargo="Desenvolvedor React")], [REACT_ANGULAR]
        )

        assert plano.diretrizes(0) == DiretrizesExperiencia(trocar=(REACT_ANGULAR,))

    def test_experiencia_sem_descricao_fica_sem_diretrizes(self):
        experiencias = [_experiencia("  ", cargo="Desenvolvedor React"), _experiencia("Usei React.")]

        plano = PlanoAdaptacao.distribuir(experiencias, [REACT_ANGULAR])

        assert plano.diretrizes(0) == DiretrizesExperiencia()
        assert plano.diretrizes(1) == DiretrizesExperiencia(trocar=(REACT_ANGULAR,))

    def test_duas_equivalencias_na_mesma_experiencia(self):
        mysql_postgres = EquivalenciaTecnologia(original="MySQL", alvo="PostgreSQL")

        plano = PlanoAdaptacao.distribuir(
            [_experiencia("React com MySQL.")], [REACT_ANGULAR, mysql_postgres]
        )

        assert plano.diretrizes(0) == DiretrizesExperiencia(trocar=(REACT_ANGULAR, mysql_postgres))

    def test_so_a_primeira_equivalencia_de_cada_original_e_usada(self):
        react_vue = EquivalenciaTecnologia(original="react", alvo="Vue")

        plano = PlanoAdaptacao.distribuir([_experiencia("Usei React.")], [REACT_ANGULAR, react_vue])

        assert plano.diretrizes(0) == DiretrizesExperiencia(trocar=(REACT_ANGULAR,))

    def test_original_ausente_do_perfil_nao_gera_troca(self):
        plano = PlanoAdaptacao.distribuir([_experiencia("APIs em Go.")], [REACT_ANGULAR])

        assert plano == PlanoAdaptacao.vazio()

    def test_plano_vazio_nao_tem_diretrizes(self):
        plano = PlanoAdaptacao.vazio()

        assert plano.ajustes == ()
        assert plano.manutencoes == ()
        assert plano.diretrizes(0) == DiretrizesExperiencia()
