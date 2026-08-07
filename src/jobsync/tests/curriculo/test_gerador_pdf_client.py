"""Teste do adapter GeradorPdfClient.

Não depende de rede nem de LLM: valida apenas que o PDF é gerado
corretamente a partir de um Curriculo de domínio.
"""
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Spacer

from jobsync.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from jobsync.curriculo.adapters.gerador_pdf_client import GeradorPdfClient


def test_aplica_enfase_tecnologias():
    texto = "Languages: Python, Java, Go"
    resultado = GeradorPdfClient._aplicar_enfase(texto, TipoSecao.TECNOLOGIAS)

    assert resultado == "<b>Languages</b>: Python, Java, Go"


def test_aplica_enfase_tecnologias_multiplas_categorias():
    texto = "Languages: Python, Java\nDatabases: PostgreSQL\nDevOps: Docker"
    resultado = GeradorPdfClient._aplicar_enfase(texto, TipoSecao.TECNOLOGIAS)

    assert "<b>Languages</b>: Python, Java" in resultado
    assert "<b>Databases</b>: PostgreSQL" in resultado
    assert "<b>DevOps</b>: Docker" in resultado


def test_aplica_enfase_tecnologias_em_portugues():
    texto = "Linguagens: Python, Java\nDesenvolvimento Web: Django"
    resultado = GeradorPdfClient._aplicar_enfase(texto, TipoSecao.TECNOLOGIAS, "pt")

    assert "<b>Linguagens</b>: Python, Java" in resultado
    assert "<b>Desenvolvimento Web</b>: Django" in resultado


def test_aplica_enfase_tecnologias_com_idioma_desconhecido_usa_fallback_portugues():
    texto = "Languages: Python, Java\nDatabases: PostgreSQL"
    resultado = GeradorPdfClient._aplicar_enfase(texto, TipoSecao.TECNOLOGIAS, "fr")

    assert "<b>Linguagens</b>: Python, Java" in resultado
    assert "<b>Bancos de Dados</b>: PostgreSQL" in resultado


def test_aplica_enfase_tecnologias_preserva_conteudo_factual_em_portugues():
    texto = "Languages: Python, Java, Go"
    resultado = GeradorPdfClient._aplicar_enfase(texto, TipoSecao.TECNOLOGIAS, "pt")

    assert "<b>Linguagens</b>: Python, Java, Go" in resultado
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
    estilo = getSampleStyleSheet()["Normal"]
    conteudo = "Languages: Python, Java\nDatabases: PostgreSQL"
    elementos = GeradorPdfClient()._formatar_conteudo(conteudo, estilo, TipoSecao.TECNOLOGIAS, "en")

    paragrafos = [elemento for elemento in elementos if hasattr(elemento, "text")]
    spacers = [elemento for elemento in elementos if isinstance(elemento, Spacer)]

    assert len(paragrafos) == 2
    assert "<b>Languages</b>: Python, Java" in paragrafos[0].text
    assert "<b>Databases</b>: PostgreSQL" in paragrafos[1].text
    assert any(getattr(elemento, "height", None) == 2 for elemento in spacers)


def test_formatar_conteudo_tecnologias_sem_categorias_explicitas_preserva_texto():
    estilo = getSampleStyleSheet()["Normal"]
    conteudo = "Python, Java, Go"
    elementos = GeradorPdfClient()._formatar_conteudo(conteudo, estilo, TipoSecao.TECNOLOGIAS, "en")

    paragrafos = [elemento for elemento in elementos if hasattr(elemento, "text")]

    assert len(paragrafos) == 1
    assert paragrafos[0].text == "Python, Java, Go"


def test_formatar_experiencias_com_cabecalho_e_posicao():
    estilo = getSampleStyleSheet()["Normal"]
    conteudo = "Starian Mar 2026 - Present\nSoftware Engineer\n- Desenvolvi APIs REST\n\nIFSC - Técnico em Telecomunicações"
    elementos = GeradorPdfClient()._formatar_conteudo(conteudo, estilo, TipoSecao.EXPERIENCIAS)

    paragrafos = [elemento for elemento in elementos if hasattr(elemento, "text")]

    assert paragrafos[0].text == "<b>Starian Mar 2026 - Present</b>"
    assert paragrafos[1].text == "<b>Software Engineer</b>"
    assert paragrafos[2].text == "&bull;&nbsp;&nbsp;Desenvolvi APIs REST"
    assert any("<b>IFSC - Técnico em Telecomunicações</b>" in getattr(elemento, "text", "") for elemento in paragrafos)


def test_nao_aplica_negrito_em_descricao_de_experiencia():
    estilo = getSampleStyleSheet()["Normal"]
    conteudo = "Starian Mar 2026 - Present\nSoftware Engineer\n- Conduzi integração com APIs\n- Reduzi tempo de deploy"
    elementos = GeradorPdfClient()._formatar_conteudo(conteudo, estilo, TipoSecao.EXPERIENCIAS)

    paragrafos = [elemento for elemento in elementos if hasattr(elemento, "text")]
    assert paragrafos[2].text == "&bull;&nbsp;&nbsp;Conduzi integração com APIs"
    assert paragrafos[3].text == "&bull;&nbsp;&nbsp;Reduzi tempo de deploy"


def test_adiciona_espacamento_extra_entre_blocos_de_experiencia():
    estilo = getSampleStyleSheet()["Normal"]
    conteudo = "Starian Mar 2026 - Present\nSoftware Engineer\n- Desenvolvi APIs REST\n\nIFSC - Técnico em Telecomunicações"
    elementos = GeradorPdfClient()._formatar_conteudo(conteudo, estilo, TipoSecao.EXPERIENCIAS)

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
