import logging

from reportlab.lib.fonts import tt2ps
from reportlab.pdfbase import pdfmetrics

from jobsync.curriculo.adapters.pdf.registrador_fontes_pdf import RegistradorFontesPdf


class TestRegistradorFontesPdf:
    def test_registra_familia_carlito_quando_arquivos_existem(self):
        familia = RegistradorFontesPdf().registrar()

        assert familia.regular == "Carlito"
        assert familia.bold == "Carlito-Bold"
        assert familia.italic == "Carlito-Italic"
        assert familia.bold_italic == "Carlito-BoldItalic"
        assert "Carlito-Bold" in pdfmetrics.getRegisteredFontNames()

    def test_associa_negrito_e_italico_da_familia_para_markup_inline(self):
        RegistradorFontesPdf().registrar()

        assert tt2ps("Carlito", 1, 0) == "Carlito-Bold"
        assert tt2ps("Carlito", 0, 1) == "Carlito-Italic"
        assert tt2ps("Carlito", 1, 1) == "Carlito-BoldItalic"

    def test_usa_helvetica_quando_diretorio_de_fontes_nao_existe(self, tmp_path):
        registrador = RegistradorFontesPdf(diretorio_fontes=tmp_path / "inexistente")

        familia = registrador.registrar()

        assert familia.regular == "Helvetica"
        assert familia.bold == "Helvetica-Bold"
        assert familia.italic == "Helvetica-Oblique"
        assert familia.bold_italic == "Helvetica-BoldOblique"

    def test_emite_warning_quando_usa_fallback(self, tmp_path, caplog):
        registrador = RegistradorFontesPdf(diretorio_fontes=tmp_path / "inexistente")

        with caplog.at_level(logging.WARNING):
            registrador.registrar()

        assert "Carlito" in caplog.text
        assert "Helvetica" in caplog.text

    def test_registrar_duas_vezes_retorna_a_mesma_familia_sem_falhar(self):
        registrador = RegistradorFontesPdf()

        primeira = registrador.registrar()
        segunda = registrador.registrar()

        assert primeira == segunda
