"""Teste do adapter GeradorPdfReportLab.

Não depende de rede nem de LLM: valida apenas que o PDF é gerado
corretamente a partir de um Curriculo de domínio.
"""
from domain.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from infrastructure.pdf.gerador_pdf_reportlab import GeradorPdfReportLab
from reportlab.lib.styles import ParagraphStyle


def test_gera_pdf_valido_com_todas_as_secoes():
    curriculo = Curriculo(
        nome_completo="Adriano João Teixeira Filho",
        email="adriano@example.com",
        linkedin="linkedin.com/in/adriano",
        secoes=(
            SecaoCurriculo(TipoSecao.TECNOLOGIAS, "Tecnologias", "Java, Go, Python"),
            SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Engenheiro de software backend."),
            SecaoCurriculo(
                TipoSecao.EXPERIENCIAS,
                "Experiências",
                "Starian - Engenheiro de Software\n- Melhorei performance em 30%",
            ),
            SecaoCurriculo(TipoSecao.FORMACAO, "Formação acadêmica", "Estácio - ADS"),
        ),
    )

    gerador = GeradorPdfReportLab()
    pdf_bytes = gerador.gerar(curriculo)

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500


def test_formatar_conteudo_aplica_negrito_em_labels_e_empresas():
    estilo = ParagraphStyle("Teste", fontSize=10)
    elementos = GeradorPdfReportLab._formatar_conteudo(
        "Languages: Python, Go\nStarian - Engenheiro de Software\n- Liderança técnica",
        {"corpo": estilo, "corpo_bullet": estilo},
    )

    assert len(elementos) == 6
    assert "<b>Languages:</b> Python, Go" in elementos[0].text
    assert "<b>Starian</b> - <b>Engenheiro de Software</b>" in elementos[2].text
    assert elementos[4].text == "Liderança técnica"
