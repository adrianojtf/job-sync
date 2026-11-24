import pytest

from jobsync.shared_kernel.domain.rotulos_blocos_experiencia import (
    BlocoExperiencia,
    bloco_do_rotulo,
    rotulo_do_bloco,
)


class TestRotulosBlocosExperiencia:
    @pytest.mark.parametrize(
        ("bloco", "idioma", "esperado"),
        [
            (BlocoExperiencia.CONTEXTO, "en", "Context"),
            (BlocoExperiencia.CONTEXTO, "pt", "Contexto"),
            (BlocoExperiencia.RESPONSABILIDADES, "en", "Key Responsibilities"),
            (BlocoExperiencia.RESPONSABILIDADES, "pt", "Principais responsabilidades"),
            (BlocoExperiencia.REALIZACOES, "en", "Key Achievements"),
            (BlocoExperiencia.REALIZACOES, "pt", "Principais realizações"),
            (BlocoExperiencia.SKILLS, "en", "Technologies"),
            (BlocoExperiencia.SKILLS, "pt", "Tecnologias"),
        ],
    )
    def test_rotulo_do_bloco_segue_o_idioma(self, bloco, idioma, esperado):
        assert rotulo_do_bloco(bloco, idioma) == esperado

    def test_idioma_nao_suportado_levanta_erro(self):
        with pytest.raises(ValueError, match="idioma alvo inválido"):
            rotulo_do_bloco(BlocoExperiencia.CONTEXTO, "fr")

    @pytest.mark.parametrize(
        ("rotulo", "esperado"),
        [
            ("Context", BlocoExperiencia.CONTEXTO),
            ("CONTEXTO", BlocoExperiencia.CONTEXTO),
            ("Key Responsibilities", BlocoExperiencia.RESPONSABILIDADES),
            ("Responsabilidades", BlocoExperiencia.RESPONSABILIDADES),
            ("Key Achievements", BlocoExperiencia.REALIZACOES),
            ("Principais realizacoes", BlocoExperiencia.REALIZACOES),
            ("Principais entregas", BlocoExperiencia.REALIZACOES),
            ("Technologies", BlocoExperiencia.SKILLS),
            ("  skills:  ", BlocoExperiencia.SKILLS),
            ("Tecnologias", BlocoExperiencia.SKILLS),
        ],
    )
    def test_reconhece_rotulos_e_apelidos_sem_diferenciar_caixa_ou_acento(self, rotulo, esperado):
        assert bloco_do_rotulo(rotulo) == esperado

    def test_texto_que_nao_e_rotulo_devolve_none(self):
        assert bloco_do_rotulo("Criei APIs") is None
