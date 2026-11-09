"""Teste do adapter GeradorPdfClient.

Não depende de rede nem de LLM: valida apenas que o PDF é gerado
corretamente a partir de um Curriculo de domínio.
"""
import io

import pdfplumber
import pytest

from jobsync.curriculo import (
    Curriculo,
    ExperienciaAdaptada,
    RascunhoCurriculoAdaptado,
    SecaoCurriculo,
    TipoSecao,
)
from jobsync.curriculo.adapters.gerador_pdf_client import GeradorPdfClient
from jobsync.curriculo.adapters.pdf.registrador_fontes_pdf import RegistradorFontesPdf


def test_aplica_enfase_tecnologias():
    texto = "Languages: Python, Java, Go"
    resultado = GeradorPdfClient._aplicar_enfase(texto, TipoSecao.TECNOLOGIAS)

    assert resultado == "<b>Languages:</b> Python, Java, Go"


def test_aplica_enfase_tecnologias_multiplas_categorias():
    texto = "Languages: Python, Java\nDatabases: PostgreSQL\nDevOps: Docker"
    resultado = GeradorPdfClient._aplicar_enfase(texto, TipoSecao.TECNOLOGIAS)

    assert "<b>Languages:</b> Python, Java" in resultado
    assert "<b>Databases:</b> PostgreSQL" in resultado
    assert "<b>DevOps:</b> Docker" in resultado


def test_aplica_enfase_tecnologias_em_portugues():
    texto = "Linguagens: Python, Java\nDesenvolvimento Web: Django"
    resultado = GeradorPdfClient._aplicar_enfase(texto, TipoSecao.TECNOLOGIAS, "pt")

    assert "<b>Linguagens:</b> Python, Java" in resultado
    assert "<b>Desenvolvimento Web:</b> Django" in resultado


def test_aplica_enfase_tecnologias_com_idioma_desconhecido_usa_fallback_portugues():
    texto = "Languages: Python, Java\nDatabases: PostgreSQL"
    resultado = GeradorPdfClient._aplicar_enfase(texto, TipoSecao.TECNOLOGIAS, "fr")

    assert "<b>Linguagens:</b> Python, Java" in resultado
    assert "<b>Bancos de Dados:</b> PostgreSQL" in resultado


def test_aplica_enfase_tecnologias_preserva_conteudo_factual_em_portugues():
    texto = "Languages: Python, Java, Go"
    resultado = GeradorPdfClient._aplicar_enfase(texto, TipoSecao.TECNOLOGIAS, "pt")

    assert "<b>Linguagens:</b> Python, Java, Go" in resultado
    assert "Python, Java, Go" in resultado
    assert "Languages" not in resultado


def test_localiza_titulo_de_secao_para_ingles():
    gerador = GeradorPdfClient()

    assert gerador._obter_titulo_secao(TipoSecao.PERFIL, "Perfil", "en") == "Profile"


def test_aplica_enfase_formacao():
    texto = "Estácio - ADS"
    resultado = GeradorPdfClient._aplicar_enfase(texto, TipoSecao.FORMACAO)

    assert resultado == "<b>Estácio</b> - <b>ADS</b>"


def test_formatar_conteudo_tecnologias_separa_categorias_com_espacamento():
    conteudo = "Languages: Python, Java\nDatabases: PostgreSQL"
    elementos = GeradorPdfClient()._formatar_conteudo(conteudo, TipoSecao.TECNOLOGIAS, "en")

    paragrafos = [elemento for elemento in elementos if hasattr(elemento, "text")]

    assert len(paragrafos) == 2
    assert "<b>Languages:</b> Python, Java" in paragrafos[0].text
    assert "<b>Databases:</b> PostgreSQL" in paragrafos[1].text
    assert all(paragrafo.style.spaceAfter == 2 for paragrafo in paragrafos)


def test_formatar_conteudo_tecnologias_sem_categorias_explicitas_preserva_texto():
    conteudo = "Python, Java, Go"
    elementos = GeradorPdfClient()._formatar_conteudo(conteudo, TipoSecao.TECNOLOGIAS, "en")

    paragrafos = [elemento for elemento in elementos if hasattr(elemento, "text")]

    assert len(paragrafos) == 1
    assert paragrafos[0].text == "Python, Java, Go"


def test_aplica_enfase_formacao_com_education_e_grau():
    texto = "Education: Estácio, Jun 2022 - Jun 2024, Associate Degree in Systems Analysis and Development"
    resultado = GeradorPdfClient._aplicar_enfase(texto, TipoSecao.FORMACAO)

    assert resultado == "<b>Education</b>: <b>Estácio</b>, Jun 2022 - Jun 2024, <b>Associate Degree in Systems Analysis and Development</b>"


def test_gera_pdf_valido_com_todas_as_secoes():
    curriculo = Curriculo(
        nome_completo="Adriano João Teixeira Filho",
        email="adriano@example.com",
        linkedin="linkedin.com/in/adriano",
        secoes=(
            SecaoCurriculo(TipoSecao.TECNOLOGIAS, "Tecnologias", "Languages: Python, Java, Go"),
            SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Engenheiro de software backend."),
            SecaoCurriculo(
                TipoSecao.EXPERIENCIAS,
                "Experiências",
                "Starian Mar 2026 - Present\nSoftware Engineer\n- Melhorei performance em 30%",
            ),
            SecaoCurriculo(TipoSecao.FORMACAO, "Formação acadêmica", "Estácio - ADS"),
        ),
    )

    gerador = GeradorPdfClient()
    pdf_bytes = gerador.gerar(curriculo, "pt")

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500


def test_pdf_desenha_o_contexto_em_fonte_italica_cinza_depois_dos_bullets():
    curriculo = Curriculo(
        nome_completo="Ana Souza",
        email="ana@example.com",
        linkedin="",
        secoes=(
            SecaoCurriculo(
                TipoSecao.EXPERIENCIAS,
                "Experiências",
                "Software Engineer — SIPPulse (2022 - Atual)\n"
                "- Developed a VoIP billing system.\n"
                "Contexto: Atuei na plataforma de comunicação.",
            ),
        ),
    )

    pdf_bytes = GeradorPdfClient().gerar(curriculo, "pt")

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        pagina = pdf.pages[0]
        linhas = pagina.extract_text().splitlines()
        topo_do_contexto = _topo(pagina, "Contexto:")
        letras_da_linha = [
            c for c in pagina.chars if c["text"].strip() and abs(c["top"] - topo_do_contexto) < 1
        ]

    assert linhas.index("Contexto: Atuei na plataforma de comunicação.") > linhas.index(
        "● Developed a VoIP billing system."
    )
    assert letras_da_linha
    assert all(c["fontname"].endswith("Carlito-Italic") for c in letras_da_linha)
    assert all(_hex(c["non_stroking_color"]) == "#595959" for c in letras_da_linha)


def _topo(pagina, palavra: str) -> float:
    return next(p["top"] for p in pagina.extract_words() if p["text"] == palavra)


@pytest.mark.parametrize(("idioma", "rotulo"), [("pt", "Contexto:"), ("en", "Context:")])
def test_pdf_de_um_rascunho_desenha_o_contexto_no_rotulo_do_idioma(idioma, rotulo):
    rascunho = RascunhoCurriculoAdaptado(
        nome_completo="Ana Souza",
        email="ana@example.com",
        linkedin="",
        secoes=(),
        experiencias=(
            ExperienciaAdaptada(
                cargo="Engenheira",
                empresa="TechCorp",
                periodo="2024",
                conquistas=("Criei APIs.", "Reduzi custos."),
                contexto="Empresa de pagamentos.",
            ),
        ),
    )

    pdf_bytes = GeradorPdfClient().gerar(rascunho.para_curriculo(idioma), idioma)

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        pagina = pdf.pages[0]
        topo = _topo(pagina, rotulo)
        letras = [c for c in pagina.chars if c["text"].strip() and abs(c["top"] - topo) < 1]
        texto = pagina.extract_text()

    assert f"{rotulo} Empresa de pagamentos." in texto
    assert all(c["fontname"].endswith("Carlito-Italic") for c in letras)


def _hex(cor) -> str:
    return "#%02X%02X%02X" % tuple(round(c * 255) for c in cor)


def _pagina_do_pdf(curriculo: Curriculo, idioma: str = "en", gerador: GeradorPdfClient | None = None):
    pdf_bytes = (gerador or GeradorPdfClient()).gerar(curriculo, idioma)
    return pdfplumber.open(io.BytesIO(pdf_bytes)).pages[0]


def _curriculo_com(*secoes: SecaoCurriculo, linkedin: str = "linkedin.com/in/adriano") -> Curriculo:
    return Curriculo(
        nome_completo="Adriano João Teixeira Filho",
        email="adriano@example.com",
        linkedin=linkedin,
        secoes=tuple(secoes),
    )


def _tecnologias(conteudo: str) -> SecaoCurriculo:
    return SecaoCurriculo(TipoSecao.TECNOLOGIAS, "Tecnologias", conteudo)


def _perfil(conteudo: str) -> SecaoCurriculo:
    return SecaoCurriculo(TipoSecao.PERFIL, "Perfil", conteudo)


def _divisorias_de_secao(pagina) -> list[dict]:
    return [linha for linha in pagina.lines if linha["x1"] - linha["x0"] > 400]


def _linhas_de_texto(pagina) -> list[str]:
    return [linha["text"] for linha in pagina.extract_text_lines()]


def test_layout_nome_centralizado_em_caixa_alta_bold_16_azul_marinho():
    pagina = _pagina_do_pdf(_curriculo_com(_perfil("Texto")))

    linha = pagina.extract_text_lines()[0]
    primeiro_caractere = linha["chars"][0]
    assert linha["text"] == "ADRIANO JOÃO TEIXEIRA FILHO"
    assert primeiro_caractere["fontname"].endswith("Carlito-Bold")
    assert round(primeiro_caractere["size"]) == 16
    assert _hex(primeiro_caractere["non_stroking_color"]) == "#1F3864"
    assert abs((linha["x0"] + linha["x1"]) / 2 - 306) < 2


def test_layout_contato_centralizado_cinza_com_linkedin_clicavel_em_azul():
    pagina = _pagina_do_pdf(_curriculo_com(_perfil("Texto")))

    linha = pagina.extract_text_lines()[1]
    caracteres = linha["chars"]
    assert linha["text"] == "LinkedIn: linkedin.com/in/adriano | Email: adriano@example.com"
    assert round(caracteres[0]["size"]) == 10
    assert _hex(caracteres[0]["non_stroking_color"]) == "#595959"
    assert _hex(caracteres[len("LinkedIn: ") + 1]["non_stroking_color"]) == "#0563C1"
    assert abs((linha["x0"] + linha["x1"]) / 2 - 306) < 2
    assert [link["uri"] for link in pagina.hyperlinks] == ["https://linkedin.com/in/adriano"]


def test_layout_link_do_linkedin_ja_com_protocolo_nao_duplica_https():
    pagina = _pagina_do_pdf(_curriculo_com(_perfil("Texto"), linkedin="https://linkedin.com/in/adriano"))

    assert [link["uri"] for link in pagina.hyperlinks] == ["https://linkedin.com/in/adriano"]


def test_layout_contato_sem_linkedin_mostra_apenas_o_email():
    pagina = _pagina_do_pdf(_curriculo_com(_perfil("Texto"), linkedin=""))

    assert _linhas_de_texto(pagina)[1] == "Email: adriano@example.com"
    assert pagina.hyperlinks == []


def test_layout_nao_tem_linha_divisoria_abaixo_do_cabecalho():
    pagina = _pagina_do_pdf(_curriculo_com(_perfil("Texto")))

    topo_do_titulo = next(linha["top"] for linha in pagina.extract_text_lines() if linha["text"] == "PROFILE")
    divisorias = _divisorias_de_secao(pagina)
    assert len(divisorias) == 1
    assert divisorias[0]["top"] > topo_do_titulo


def test_layout_titulo_de_secao_em_caixa_alta_bold_11_azul_com_linha_de_largura_total():
    pagina = _pagina_do_pdf(_curriculo_com(_tecnologias("Languages: Java"), _perfil("Texto")))

    titulos = [linha for linha in pagina.extract_text_lines() if linha["text"] in ("TECHNICAL SKILLS", "PROFILE")]
    assert [titulo["text"] for titulo in titulos] == ["TECHNICAL SKILLS", "PROFILE"]
    caractere = titulos[0]["chars"][0]
    assert caractere["fontname"].endswith("Carlito-Bold")
    assert round(caractere["size"]) == 11
    assert _hex(caractere["non_stroking_color"]) == "#1F3864"
    divisorias = _divisorias_de_secao(pagina)
    assert len(divisorias) == 2
    for linha in divisorias:
        assert linha["linewidth"] == 0.75
        assert _hex(linha["stroking_color"]) == "#1F3864"
        assert abs(linha["x0"] - 45) < 0.5
        assert abs(linha["x1"] - 567) < 0.5


def test_layout_titulos_de_secao_seguem_o_idioma_alvo():
    pagina = _pagina_do_pdf(_curriculo_com(_tecnologias("Linguagens: Java"), _perfil("Texto")), idioma="pt")

    assert "TECNOLOGIAS" in _linhas_de_texto(pagina)
    assert "PERFIL" in _linhas_de_texto(pagina)


def test_layout_tecnologias_uma_categoria_por_linha_com_rotulo_em_negrito():
    pagina = _pagina_do_pdf(_curriculo_com(_tecnologias("Languages: Java, Go\nFrameworks: Spring Boot\nOther: Linux")))

    linhas = {linha["text"]: linha for linha in pagina.extract_text_lines()}
    for texto in ("Languages: Java, Go", "Frameworks: Spring Boot", "Other: Linux"):
        assert texto in linhas
        caracteres = linhas[texto]["chars"]
        assert caracteres[0]["fontname"].endswith("Carlito-Bold")
        assert caracteres[-1]["fontname"].endswith("Carlito-Regular")
        assert round(caracteres[0]["size"], 1) == 10.5
        assert _hex(caracteres[0]["non_stroking_color"]) == "#000000"
        assert abs(linhas[texto]["x0"] - 45) < 1


def test_layout_tecnologias_em_linha_unica_com_varias_categorias_vira_uma_linha_por_categoria():
    conteudo = "Languages: Java, Go, Frameworks: Hibernate, Web Development: RESTful APIs, JSF, DevOps: Docker"
    pagina = _pagina_do_pdf(_curriculo_com(_tecnologias(conteudo)))

    linhas = _linhas_de_texto(pagina)
    assert "Languages: Java, Go" in linhas
    assert "Frameworks: Hibernate" in linhas
    assert "Web Development: RESTful APIs, JSF" in linhas
    assert "DevOps: Docker" in linhas


def test_layout_tecnologias_remove_marcador_das_linhas_de_categoria():
    pagina = _pagina_do_pdf(_curriculo_com(_tecnologias("- Languages: Java\n• Databases: MySQL")))

    linhas = _linhas_de_texto(pagina)
    assert "Languages: Java" in linhas
    assert "Databases: MySQL" in linhas
    assert not any("●" in linha or "•" in linha for linha in linhas)


def test_layout_perfil_junta_linhas_consecutivas_em_um_paragrafo():
    pagina = _pagina_do_pdf(_curriculo_com(_perfil("Engenheiro de software\nbackend com foco em APIs.")))

    assert "Engenheiro de software backend com foco em APIs." in _linhas_de_texto(pagina)


def test_layout_perfil_separa_paragrafos_por_linha_em_branco():
    pagina = _pagina_do_pdf(_curriculo_com(_perfil("Primeiro paragrafo.\n\nSegundo paragrafo.")))

    linhas = _linhas_de_texto(pagina)
    assert "Primeiro paragrafo." in linhas
    assert "Segundo paragrafo." in linhas


def test_layout_perfil_em_regular_10_5_preto_alinhado_a_margem_de_45_pt():
    pagina = _pagina_do_pdf(_curriculo_com(_perfil("Resumo profissional.")))

    linha = next(linha for linha in pagina.extract_text_lines() if linha["text"] == "Resumo profissional.")
    caractere = linha["chars"][0]
    assert caractere["fontname"].endswith("Carlito-Regular")
    assert round(caractere["size"], 1) == 10.5
    assert _hex(caractere["non_stroking_color"]) == "#000000"
    assert abs(linha["x0"] - 45) < 1


def test_layout_sem_arquivos_de_fonte_usa_helvetica_e_ainda_gera_pdf_valido(tmp_path):
    registrador = RegistradorFontesPdf(diretorio_fontes=tmp_path / "inexistente")
    gerador = GeradorPdfClient(registrador_fontes=registrador)

    pagina = _pagina_do_pdf(_curriculo_com(_perfil("Texto")), gerador=gerador)

    nomes = {caractere["fontname"] for caractere in pagina.chars}
    assert any("Helvetica" in nome for nome in nomes)
    assert not any("Carlito" in nome for nome in nomes)


def test_layout_dois_pontos_do_rotulo_de_tecnologia_tambem_ficam_em_negrito():
    pagina = _pagina_do_pdf(_curriculo_com(_tecnologias("Languages: Java")))

    linha = next(linha for linha in pagina.extract_text_lines() if linha["text"] == "Languages: Java")
    negrito = "".join(c["text"] for c in linha["chars"] if c["fontname"].endswith("Carlito-Bold"))
    assert negrito == "Languages:"


_AZUL_MARINHO = "#1F3864"
_CINZA = "#595959"


def _pagina_de_experiencias(conteudo: str, idioma: str = "en"):
    secao = SecaoCurriculo(TipoSecao.EXPERIENCIAS, "Experiências", conteudo)
    return _pagina_do_pdf(_curriculo_com(secao), idioma)


def _linha(pagina, texto: str) -> dict:
    return next(linha for linha in pagina.extract_text_lines() if linha["text"] == texto)


def _caracteres_visiveis(linha: dict) -> list[dict]:
    return [c for c in linha["chars"] if c["text"].strip()]


def _fonte(caractere: dict) -> str:
    return caractere["fontname"].split("+")[-1]


def test_experiencia_empresa_em_bold_11_5_e_periodo_em_cinza_alinhado_a_direita():
    pagina = _pagina_de_experiencias("Starian Mar 2026 - Present\nSoftware Engineer")

    linha = _linha(pagina, "Starian Mar 2026 - Present")
    empresa = _caracteres_visiveis(linha)[: len("Starian")]
    periodo = _caracteres_visiveis(linha)[len("Starian"):]
    assert all(_fonte(c) == "Carlito-Bold" and round(c["size"], 1) == 11.5 for c in empresa)
    assert all(_hex(c["non_stroking_color"]) == "#000000" for c in empresa)
    assert all(_fonte(c) == "Carlito-Regular" and round(c["size"], 1) == 10.5 for c in periodo)
    assert all(_hex(c["non_stroking_color"]) == _CINZA for c in periodo)
    assert abs(empresa[0]["x0"] - 45) < 1
    assert abs(linha["x1"] - 513) < 1


def test_experiencia_cargo_em_italico_azul_marinho_na_linha_abaixo_da_empresa():
    pagina = _pagina_de_experiencias("Starian Mar 2026 - Present\nSoftware Engineer")

    empresa = _linha(pagina, "Starian Mar 2026 - Present")
    cargo = _linha(pagina, "Software Engineer")
    assert cargo["top"] > empresa["top"]
    assert abs(cargo["x0"] - 45) < 1
    assert all(_fonte(c) == "Carlito-Italic" for c in _caracteres_visiveis(cargo))
    assert all(_hex(c["non_stroking_color"]) == _AZUL_MARINHO for c in _caracteres_visiveis(cargo))


def test_experiencia_topico_com_marcador_recuado_e_continuacao_alinhada_ao_texto():
    topico = "Desenvolvi um sistema de faturamento para telefonia com processamento em lote de milhares de bilhetes por minuto e cache"
    pagina = _pagina_de_experiencias(f"Starian 2024 - 2025\nDev\n- {topico}")

    palavras = pagina.extract_words()
    marcador = next(p for p in palavras if p["text"] == "●")
    primeira_palavra = next(p for p in palavras if p["text"] == "Desenvolvi")
    linhas_do_topico = [p for p in pagina.extract_text_lines() if p["top"] >= marcador["top"] - 1]
    assert abs(marcador["x0"] - 63) < 1.5
    assert abs(primeira_palavra["x0"] - 81) < 1
    assert len(linhas_do_topico) >= 2
    assert all(abs(linha["x0"] - 81) < 1 or abs(linha["x0"] - 63) < 1.5 for linha in linhas_do_topico)
    assert abs(linhas_do_topico[1]["x0"] - 81) < 1


def test_experiencia_topicos_nao_mostram_o_hifen_do_texto_de_entrada():
    pagina = _pagina_de_experiencias("Starian 2024 - 2025\nDev\n- Criei APIs\n- Reduzi custos")

    linhas = _linhas_de_texto(pagina)
    assert "● Criei APIs" in linhas
    assert "● Reduzi custos" in linhas
    assert not any(linha.startswith("- ") for linha in linhas)


def test_experiencia_contexto_em_italico_cinza_depois_dos_topicos_sem_recuo():
    pagina = _pagina_de_experiencias(
        "SIPPulse 2022 - 2026\nSoftware Engineer\n- Criei APIs\nContext: Worked on the communications platform."
    )

    topico = _linha(pagina, "● Criei APIs")
    contexto = _linha(pagina, "Context: Worked on the communications platform.")
    assert contexto["top"] > topico["top"]
    assert abs(contexto["x0"] - 45) < 1
    assert all(_fonte(c) == "Carlito-Italic" for c in _caracteres_visiveis(contexto))
    assert all(_hex(c["non_stroking_color"]) == _CINZA for c in _caracteres_visiveis(contexto))


@pytest.mark.parametrize(
    "linha_de_contexto",
    ["Contexto: Empresa de telecom.", "CONTEXT: Telecom company.", "contexto:Empresa."],
)
def test_experiencia_reconhece_o_rotulo_do_contexto_nos_dois_idiomas_sem_diferenciar_maiusculas(linha_de_contexto):
    pagina = _pagina_de_experiencias(f"Dev — TechCorp (2024)\n- Criei APIs.\n{linha_de_contexto}")

    contexto = next(l for l in pagina.extract_text_lines() if l["text"].lower().startswith(("contexto", "context")))
    assert all(_fonte(c) == "Carlito-Italic" for c in _caracteres_visiveis(contexto))


def test_experiencia_contexto_logo_apos_o_cabecalho_nao_vira_cargo_nem_negrito():
    pagina = _pagina_de_experiencias("Dev — TechCorp (2024)\nContexto: Empresa de telecom.")

    cargo = _linha(pagina, "Dev")
    contexto = _linha(pagina, "Contexto: Empresa de telecom.")
    assert all(_hex(c["non_stroking_color"]) == _AZUL_MARINHO for c in _caracteres_visiveis(cargo))
    assert all(_hex(c["non_stroking_color"]) == _CINZA for c in _caracteres_visiveis(contexto))
    assert not any("Bold" in _fonte(c) for c in _caracteres_visiveis(contexto))


def test_experiencia_escapa_caracteres_especiais_no_contexto():
    pagina = _pagina_de_experiencias("Dev — TechCorp\nContexto: P&D de <telecom>.")

    assert "Contexto: P&D de <telecom>." in _linhas_de_texto(pagina)


def test_experiencia_sem_contexto_nao_gera_texto_em_italico_cinza():
    pagina = _pagina_de_experiencias("Dev — TechCorp (2024)\n- Criei APIs.\n- Reduzi custos.")

    italicos_cinza = [
        c for c in pagina.chars if _fonte(c) == "Carlito-Italic" and _hex(c["non_stroking_color"]) == _CINZA
    ]
    assert italicos_cinza == []


def test_experiencia_linha_que_apenas_comeca_com_a_palavra_contexto_e_texto_normal():
    pagina = _pagina_de_experiencias("Dev — TechCorp\n- Criei APIs.\nContextualizei o sistema legado.")

    linha = _linha(pagina, "Contextualizei o sistema legado.")
    assert all(_fonte(c) == "Carlito-Regular" for c in _caracteres_visiveis(linha))
    assert all(_hex(c["non_stroking_color"]) == "#000000" for c in _caracteres_visiveis(linha))


def test_experiencia_cada_bloco_tem_o_proprio_contexto_em_italico():
    pagina = _pagina_de_experiencias(
        "Dev — A (2024)\n- Criei APIs.\nContexto: Empresa A.\n\nDev — B (2022)\n- Criei testes.\nContexto: Empresa B."
    )

    linhas_em_italico_cinza = [
        l["text"] for l in pagina.extract_text_lines()
        if all(_fonte(c) == "Carlito-Italic" and _hex(c["non_stroking_color"]) == _CINZA for c in _caracteres_visiveis(l))
    ]
    assert linhas_em_italico_cinza == ["Contexto: Empresa A.", "Contexto: Empresa B."]


def test_experiencia_so_com_contexto_nao_gera_marcador():
    pagina = _pagina_de_experiencias("Starian Mar 2026 - Present\nSoftware Engineer\nContext: ERP de construção civil.")

    assert "Context: ERP de construção civil." in _linhas_de_texto(pagina)
    assert not any("●" in linha for linha in _linhas_de_texto(pagina))


def test_experiencia_sem_periodo_mostra_apenas_a_empresa():
    pagina = _pagina_de_experiencias("Starian\nSoftware Engineer\n- Criei APIs")

    linha = _linha(pagina, "Starian")
    assert all(_fonte(c) == "Carlito-Bold" for c in _caracteres_visiveis(linha))


def test_experiencia_no_formato_com_travessao_desenha_empresa_periodo_e_cargo_do_modelo():
    pagina = _pagina_de_experiencias("Software Engineer — Starian (Mar 2026 - Present)\n- Criei APIs")

    empresa = _linha(pagina, "Starian Mar 2026 - Present")
    cargo = _linha(pagina, "Software Engineer")
    assert abs(empresa["x1"] - 513) < 1
    assert cargo["top"] > empresa["top"]
    assert all(_fonte(c) == "Carlito-Italic" for c in _caracteres_visiveis(cargo))
    assert not any("—" in linha for linha in _linhas_de_texto(pagina))


def test_experiencia_texto_extraido_segue_a_ordem_empresa_periodo_cargo_topicos_contexto():
    pagina = _pagina_de_experiencias(
        "Starian Mar 2026 - Present\nSoftware Engineer\n- Primeiro\n- Segundo\nContext: Fim."
    )

    linhas = _linhas_de_texto(pagina)
    assert linhas[linhas.index("Starian Mar 2026 - Present"):] == [
        "Starian Mar 2026 - Present",
        "Software Engineer",
        "● Primeiro",
        "● Segundo",
        "Context: Fim.",
    ]


def test_experiencia_deixa_espaco_vertical_visivel_entre_blocos():
    pagina = _pagina_de_experiencias("A 2024 - 2025\nDev\n- Um\n\nB 2022 - 2023\nDev\n- Dois")

    ultimo_do_primeiro = _linha(pagina, "● Um")
    segundo_bloco = _linha(pagina, "B 2022 - 2023")
    passo_entre_linhas_do_mesmo_bloco = _linha(pagina, "Dev")["top"] - _linha(pagina, "A 2024 - 2025")["top"]
    assert segundo_bloco["top"] - ultimo_do_primeiro["top"] > passo_entre_linhas_do_mesmo_bloco + 4


def test_experiencia_nao_deixa_o_cabecalho_orfao_no_fim_da_pagina():
    blocos = "\n\n".join(f"Empresa {n} 2020 - 2021\nDev\n- Entrega {n}\n- Outra {n}" for n in range(1, 40))

    pdf = pdfplumber.open(io.BytesIO(GeradorPdfClient().gerar(
        _curriculo_com(SecaoCurriculo(TipoSecao.EXPERIENCIAS, "Experiências", blocos)), "en")))

    assert len(pdf.pages) >= 2
    for pagina in pdf.pages:
        linhas = _linhas_de_texto(pagina)
        if linhas and linhas[-1].startswith("Empresa"):
            raise AssertionError(f"cabeçalho órfão no fim da página: {linhas[-1]}")


def _topos(pagina) -> dict[str, float]:
    return {linha["text"]: linha["top"] for linha in pagina.extract_text_lines()}


def test_layout_nome_comeca_no_topo_do_modelo():
    pagina = _pagina_do_pdf(_curriculo_com(_perfil("Texto")))

    assert abs(_topos(pagina)["ADRIANO JOÃO TEIXEIRA FILHO"] - 39.5) < 0.6


def test_layout_ritmo_vertical_das_secoes_segue_o_modelo():
    secoes = (
        _tecnologias("Languages: Java\nFrameworks: Spring Boot"),
        _perfil("Resumo."),
        SecaoCurriculo(TipoSecao.EXPERIENCIAS, "Experiências", "Starian Mar 2026 - Present\nSoftware Engineer"),
    )
    pagina = _pagina_do_pdf(_curriculo_com(*secoes))

    topos = _topos(pagina)
    assert abs((topos["Languages: Java"] - topos["TECHNICAL SKILLS"]) - 22.1) < 0.7
    assert abs((topos["Frameworks: Spring Boot"] - topos["Languages: Java"]) - 14.8) < 0.3
    assert abs((topos["PROFILE"] - topos["Frameworks: Spring Boot"]) - 27.9) < 1.0
    assert abs((topos["EXPERIENCE"] - topos["Resumo."]) - 27.9) < 1.0
    assert abs((topos["Starian Mar 2026 - Present"] - topos["EXPERIENCE"]) - 26.3) < 1.0
    assert abs((topos["Software Engineer"] - topos["Starian Mar 2026 - Present"]) - 14.8) < 0.5


def test_layout_ritmo_vertical_das_experiencias_segue_o_modelo():
    pagina = _pagina_de_experiencias(
        "A 2024 - 2025\nCargo A\n- Um\n- Dois\nContext: Fim do primeiro.\n\nB 2022 - 2023\nCargo B\nContext: Segundo."
    )

    topos = _topos(pagina)
    assert abs((topos["● Dois"] - topos["● Um"]) - 15.8) < 0.5
    assert abs((topos["● Um"] - topos["Cargo A"]) - 16.7) < 0.7
    assert abs((topos["Context: Segundo."] - topos["Cargo B"]) - 16.8) < 0.5
    assert abs((topos["Context: Fim do primeiro."] - topos["● Dois"]) - 15.8) < 0.5
    assert abs((topos["B 2022 - 2023"] - topos["Context: Fim do primeiro."]) - 23.0) < 1.0
