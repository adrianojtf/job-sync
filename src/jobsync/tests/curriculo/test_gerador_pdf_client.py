"""Teste do adapter GeradorPdfClient.

Não depende de rede nem de LLM: valida apenas que o PDF é gerado
corretamente a partir de um Curriculo de domínio.
"""
import io

import pdfplumber
import pytest
from reportlab.lib.colors import HexColor
from reportlab.platypus import Spacer

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


def test_formatar_experiencias_com_cabecalho_e_posicao():
    conteudo = "Starian Mar 2026 - Present\nSoftware Engineer\n- Desenvolvi APIs REST\n\nIFSC - Técnico em Telecomunicações"
    elementos = GeradorPdfClient()._formatar_conteudo(conteudo, TipoSecao.EXPERIENCIAS)

    paragrafos = [elemento for elemento in elementos if hasattr(elemento, "text")]

    assert paragrafos[0].text == "<b>Starian Mar 2026 - Present</b>"
    assert paragrafos[1].text == "<b>Software Engineer</b>"
    assert paragrafos[2].text == "&bull;&nbsp;&nbsp;Desenvolvi APIs REST"
    assert any("<b>IFSC - Técnico em Telecomunicações</b>" in getattr(elemento, "text", "") for elemento in paragrafos)


def test_nao_aplica_negrito_em_descricao_de_experiencia():
    conteudo = "Starian Mar 2026 - Present\nSoftware Engineer\n- Conduzi integração com APIs\n- Reduzi tempo de deploy"
    elementos = GeradorPdfClient()._formatar_conteudo(conteudo, TipoSecao.EXPERIENCIAS)

    paragrafos = [elemento for elemento in elementos if hasattr(elemento, "text")]
    assert paragrafos[2].text == "&bull;&nbsp;&nbsp;Conduzi integração com APIs"
    assert paragrafos[3].text == "&bull;&nbsp;&nbsp;Reduzi tempo de deploy"


def test_adiciona_espacamento_extra_entre_blocos_de_experiencia():
    conteudo = "Starian Mar 2026 - Present\nSoftware Engineer\n- Desenvolvi APIs REST\n\nIFSC - Técnico em Telecomunicações"
    elementos = GeradorPdfClient()._formatar_conteudo(conteudo, TipoSecao.EXPERIENCIAS)

    spacers = [elemento for elemento in elementos if isinstance(elemento, Spacer)]
    assert sum(1 for elemento in spacers if getattr(elemento, "height", None) == 6) == 1


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


def _paragrafos_de_experiencias(conteudo: str) -> list:
    elementos = GeradorPdfClient()._formatar_conteudo(conteudo, TipoSecao.EXPERIENCIAS)
    return [elemento for elemento in elementos if hasattr(elemento, "text")]


def test_formata_linha_de_contexto_em_italico_cinza_depois_dos_bullets():
    conteudo = (
        "Software Engineer — SIPPulse (2022 - Atual)\n"
        "- Developed a VoIP billing system.\n"
        "Context: Worked on the communications platform."
    )

    paragrafos = _paragrafos_de_experiencias(conteudo)

    contexto = paragrafos[-1]
    assert contexto.text == "Context: Worked on the communications platform."
    assert contexto.style.fontName == "Helvetica-Oblique"
    assert contexto.style.textColor == HexColor("#666666")
    assert paragrafos[1].text == "&bull;&nbsp;&nbsp;Developed a VoIP billing system."


@pytest.mark.parametrize("linha", ["Contexto: Empresa de telecom.", "CONTEXT: Telecom company.", "contexto:Empresa."])
def test_reconhece_o_rotulo_do_contexto_nos_dois_idiomas_sem_diferenciar_maiusculas(linha):
    paragrafos = _paragrafos_de_experiencias(f"Dev — TechCorp (2024)\n- Criei APIs.\n{linha}")

    assert paragrafos[-1].style.fontName == "Helvetica-Oblique"
    assert paragrafos[-1].text == linha


def test_contexto_logo_apos_o_cabecalho_nao_vira_negrito():
    paragrafos = _paragrafos_de_experiencias("Dev — TechCorp (2024)\nContexto: Empresa de telecom.")

    assert paragrafos[0].text == "<b>Dev — TechCorp (2024)</b>"
    assert paragrafos[1].text == "Contexto: Empresa de telecom."
    assert paragrafos[1].style.fontName == "Helvetica-Oblique"


def test_escapa_caracteres_especiais_na_linha_de_contexto():
    paragrafos = _paragrafos_de_experiencias("Dev — TechCorp\nContexto: P&D de <telecom>.")

    assert paragrafos[1].text == "Contexto: P&amp;D de &lt;telecom&gt;."


def test_experiencia_sem_contexto_nao_gera_linha_em_italico():
    paragrafos = _paragrafos_de_experiencias("Dev — TechCorp (2024)\n- Criei APIs.\n- Reduzi custos.")

    assert all(p.style.fontName != "Helvetica-Oblique" for p in paragrafos)
    assert len(paragrafos) == 3


def test_linha_que_apenas_comeca_com_a_palavra_contexto_nao_e_tratada_como_rotulo():
    paragrafos = _paragrafos_de_experiencias("Dev — TechCorp\n- Criei APIs.\nContextualizei o sistema legado.")

    assert paragrafos[-1].text == "Contextualizei o sistema legado."
    assert paragrafos[-1].style.fontName != "Helvetica-Oblique"


def test_cada_experiencia_tem_o_proprio_contexto():
    conteudo = (
        "Dev — A (2024)\n- Criei APIs.\nContexto: Empresa A.\n\n"
        "Dev — B (2022)\n- Criei testes.\nContexto: Empresa B."
    )

    paragrafos = _paragrafos_de_experiencias(conteudo)

    textos_em_italico = [p.text for p in paragrafos if p.style.fontName == "Helvetica-Oblique"]
    assert textos_em_italico == ["Contexto: Empresa A.", "Contexto: Empresa B."]


def test_pdf_desenha_o_contexto_em_fonte_obliqua_cinza_depois_dos_bullets():
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
        "• Developed a VoIP billing system."
    )
    assert letras_da_linha
    assert all("Oblique" in c["fontname"] for c in letras_da_linha)
    assert all(c["non_stroking_color"] == pytest.approx((0.4, 0.4, 0.4)) for c in letras_da_linha)


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
    assert all("Oblique" in c["fontname"] for c in letras)


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
