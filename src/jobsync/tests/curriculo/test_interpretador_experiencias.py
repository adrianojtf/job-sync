import pytest

from jobsync.curriculo.adapters.pdf.interpretador_experiencias import (
    BlocoExperiencia,
    InterpretadorExperiencias,
)


def _unico_bloco(conteudo: str) -> BlocoExperiencia:
    blocos = InterpretadorExperiencias().interpretar(conteudo)

    assert len(blocos) == 1
    return blocos[0]


class TestInterpretadorExperiencias:
    def test_separa_empresa_e_periodo_do_formato_do_modelo(self):
        bloco = _unico_bloco("Starian Mar 2026 - Present")

        assert bloco.empresa == "Starian"
        assert bloco.periodo == "Mar 2026 - Present"

    def test_hifen_no_nome_da_empresa_nao_separa(self):
        bloco = _unico_bloco("SIPPulse - High-Performance NGN SIP Solutions Nov 2022 - Mar 2026")

        assert bloco.empresa == "SIPPulse - High-Performance NGN SIP Solutions"
        assert bloco.periodo == "Nov 2022 - Mar 2026"

    @pytest.mark.parametrize(
        "periodo",
        ["Dec 2020 - Nov 2022", "Dez 2020 - Atual", "01/2020 - 12/2022", "2018 - Presente", "Jul 2014 – Oct 2018"],
    )
    def test_reconhece_periodos_em_ingles_e_portugues(self, periodo):
        bloco = _unico_bloco(f"Dígitro Tecnologia {periodo}")

        assert bloco.empresa == "Dígitro Tecnologia"
        assert bloco.periodo == periodo

    def test_linha_sem_periodo_mantem_apenas_a_empresa(self):
        bloco = _unico_bloco("Starian")

        assert bloco.empresa == "Starian"
        assert bloco.periodo == ""

    def test_formato_com_travessao_e_parenteses_separa_cargo_empresa_e_periodo(self):
        bloco = _unico_bloco("Software Engineer — Starian (Mar 2026 - Present)")

        assert bloco.cargo == "Software Engineer"
        assert bloco.empresa == "Starian"
        assert bloco.periodo == "Mar 2026 - Present"

    def test_formato_com_travessao_e_parenteses_vazios_deixa_o_periodo_vazio(self):
        bloco = _unico_bloco("Software Engineer — Starian ()")

        assert bloco.cargo == "Software Engineer"
        assert bloco.empresa == "Starian"
        assert bloco.periodo == ""

    def test_formato_com_travessao_sem_parenteses_separa_cargo_e_empresa(self):
        bloco = _unico_bloco("Software Engineer — Starian")

        assert bloco.cargo == "Software Engineer"
        assert bloco.empresa == "Starian"
        assert bloco.periodo == ""

    def test_travessao_com_hifen_no_nome_da_empresa_mantem_o_nome_inteiro(self):
        bloco = _unico_bloco("Dev — SIPPulse - High-Performance (2022 - Atual)")

        assert bloco.cargo == "Dev"
        assert bloco.empresa == "SIPPulse - High-Performance"
        assert bloco.periodo == "2022 - Atual"

    def test_formacao_com_travessao_separa_curso_e_instituicao(self):
        bloco = _unico_bloco("Análise e Desenvolvimento de Sistemas — Estácio (Jun 2022 - Jun 2024)")

        assert bloco.cargo == "Análise e Desenvolvimento de Sistemas"
        assert bloco.empresa == "Estácio"
        assert bloco.periodo == "Jun 2022 - Jun 2024"

    def test_certificacao_com_travessao_aceita_apenas_o_ano_nos_parenteses(self):
        bloco = _unico_bloco("AWS Developer — Amazon (2023)")

        assert bloco.cargo == "AWS Developer"
        assert bloco.empresa == "Amazon"
        assert bloco.periodo == "2023"

    @pytest.mark.parametrize("linha", ["Estácio (UFSC)", "Curso — Estácio (UFSC)"])
    def test_parenteses_que_nao_sao_periodo_continuam_no_nome_da_instituicao(self, linha):
        bloco = _unico_bloco(linha)

        assert bloco.empresa == "Estácio (UFSC)"
        assert bloco.periodo == ""

    def test_reconhece_o_cargo_na_segunda_linha(self):
        bloco = _unico_bloco("Starian Mar 2026 - Present\nSoftware Engineer")

        assert bloco.cargo == "Software Engineer"

    def test_segunda_linha_com_ano_nao_e_cargo(self):
        bloco = _unico_bloco("Starian Mar 2026 - Present\nMigrei o sistema em 2024 para a nuvem.")

        assert bloco.cargo == ""
        assert bloco.descricao == ("Migrei o sistema em 2024 para a nuvem.",)

    def test_cargo_do_cabecalho_com_travessao_nao_consome_a_segunda_linha(self):
        bloco = _unico_bloco("Dev — Starian (2024)\nContexto: Empresa de ERP.")

        assert bloco.cargo == "Dev"
        assert bloco.contexto == "Contexto: Empresa de ERP."

    @pytest.mark.parametrize("marcador", ["-", "•", "●", "*"])
    def test_reconhece_topicos_com_qualquer_marcador(self, marcador):
        bloco = _unico_bloco(f"Starian 2024 - 2025\nDev\n{marcador} Criei APIs\n{marcador} Reduzi custos")

        assert bloco.topicos == ("Criei APIs", "Reduzi custos")

    @pytest.mark.parametrize(
        "linha",
        ["Context: Empresa de telecom.", "Contexto: Empresa de telecom.", "CONTEXT: Empresa de telecom.", "contexto:Empresa de telecom."],
    )
    def test_reconhece_o_contexto_pelo_rotulo_nos_dois_idiomas(self, linha):
        bloco = _unico_bloco(f"Dev — Starian (2024)\n- Criei APIs\n{linha}")

        assert bloco.contexto == linha

    def test_linhas_apos_o_contexto_continuam_o_mesmo_paragrafo(self):
        bloco = _unico_bloco("Dev — Starian (2024)\nContext: Empresa de telecom que\nopera em todo o Brasil.")

        assert bloco.contexto == "Context: Empresa de telecom que opera em todo o Brasil."

    def test_linha_que_apenas_comeca_com_a_palavra_contexto_nao_e_rotulo(self):
        bloco = _unico_bloco("Dev — Starian\n- Criei APIs.\nContextualizei o sistema legado.")

        assert bloco.contexto == ""
        assert bloco.descricao == ("Contextualizei o sistema legado.",)

    def test_bloco_so_com_contexto(self):
        bloco = _unico_bloco("Starian Mar 2026 - Present\nSoftware Engineer\nContext: ERP de construção civil.")

        assert bloco.topicos == ()
        assert bloco.contexto == "Context: ERP de construção civil."

    def test_bloco_sem_contexto(self):
        bloco = _unico_bloco("Starian Mar 2026 - Present\nSoftware Engineer\n- Criei APIs")

        assert bloco.contexto == ""
        assert bloco.topicos == ("Criei APIs",)

    def test_separa_varios_blocos_por_linha_em_branco(self):
        blocos = InterpretadorExperiencias().interpretar(
            "Starian 2024 - 2025\nDev\n- A\nContext: X\n\nSIPPulse 2020 - 2022\nJunior\n- B"
        )

        assert [bloco.empresa for bloco in blocos] == ["Starian", "SIPPulse"]
        assert blocos[1].topicos == ("B",)

    def test_conteudo_vazio_nao_gera_blocos(self):
        assert InterpretadorExperiencias().interpretar("  \n\n ") == []

    def test_nenhuma_linha_de_entrada_e_descartada(self):
        conteudo = (
            "Dev — Starian (2024)\n- Criei APIs\nTexto solto aqui\nContext: Empresa de telecom."
        )

        bloco = _unico_bloco(conteudo)

        texto = " ".join([bloco.empresa, bloco.periodo, bloco.cargo, *bloco.topicos, *bloco.descricao, bloco.contexto])
        for trecho in ("Dev", "Starian", "2024", "Criei APIs", "Texto solto aqui", "Empresa de telecom."):
            assert trecho in texto
