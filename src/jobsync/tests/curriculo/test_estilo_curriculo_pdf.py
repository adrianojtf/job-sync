from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from jobsync.curriculo.adapters.pdf.estilo_curriculo_pdf import EstiloCurriculoPdf
from jobsync.curriculo.adapters.pdf.registrador_fontes_pdf import FamiliaFonte, RegistradorFontesPdf


def _estilo() -> EstiloCurriculoPdf:
    return EstiloCurriculoPdf(familia=RegistradorFontesPdf().registrar())


class TestEstiloCurriculoPdf:
    def test_topico_tem_recuo_do_marcador_e_do_texto_do_modelo(self):
        topico = _estilo().topico

        assert topico.bulletIndent == 18
        assert topico.leftIndent == 36
        assert topico.bulletFontSize == 10
        assert topico.bulletFontName == "Carlito"

    def test_nome_e_centralizado_bold_16_azul_marinho(self):
        nome = _estilo().nome

        assert nome.alignment == TA_CENTER
        assert nome.fontName == "Carlito-Bold"
        assert nome.fontSize == 16
        assert nome.textColor == HexColor("#1F3864")

    def test_contato_e_centralizado_10_cinza(self):
        contato = _estilo().contato

        assert contato.alignment == TA_CENTER
        assert contato.fontSize == 10
        assert contato.textColor == HexColor("#595959")

    def test_titulo_de_secao_e_bold_11_azul_marinho(self):
        titulo = _estilo().titulo_secao

        assert titulo.fontName == "Carlito-Bold"
        assert titulo.fontSize == 11
        assert titulo.textColor == HexColor("#1F3864")

    def test_empresa_periodo_cargo_e_contexto_seguem_o_modelo(self):
        estilo = _estilo()

        assert (estilo.empresa.fontName, estilo.empresa.fontSize) == ("Carlito-Bold", 11.5)
        assert estilo.periodo.alignment == TA_RIGHT
        assert estilo.periodo.textColor == HexColor("#595959")
        assert estilo.cargo.fontName == "Carlito-Italic"
        assert estilo.cargo.textColor == HexColor("#1F3864")
        assert estilo.contexto.fontName == "Carlito-Italic"
        assert estilo.contexto.textColor == HexColor("#595959")

    def test_corpo_e_regular_10_5_preto_com_entrelinha_do_modelo(self):
        corpo = _estilo().corpo

        assert corpo.fontName == "Carlito"
        assert corpo.fontSize == 10.5
        assert corpo.leading == 12.8
        assert corpo.textColor == HexColor("#000000")

    def test_expoe_tokens_de_pagina_e_cores_do_modelo(self):
        estilo = _estilo()

        assert estilo.margem_lateral == 45
        assert estilo.cor_destaque == HexColor("#1F3864")
        assert estilo.cor_secundaria == HexColor("#595959")
        assert estilo.cor_link == HexColor("#0563C1")
        assert estilo.espessura_linha_secao == 0.75

    def test_usa_a_familia_de_fontes_informada(self):
        familia = FamiliaFonte("Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique")
        estilo = EstiloCurriculoPdf(familia=familia)

        assert estilo.nome.fontName == "Helvetica-Bold"
        assert estilo.cargo.fontName == "Helvetica-Oblique"
        assert estilo.topico.bulletFontName == "Helvetica"
