from jobsync.vaga.adapters.html_para_texto import converter_html_em_texto


class TestConverterHtmlEmTexto:
    def test_converte_quebras_de_linha_e_paragrafos(self):
        html = "<p>Primeiro parágrafo.</p><p>Segundo parágrafo.<br>Linha seguinte.</p>"

        texto = converter_html_em_texto(html)

        assert texto == "Primeiro parágrafo.\n\nSegundo parágrafo.\nLinha seguinte."

    def test_converte_listas_em_itens_com_marcador(self):
        html = "<strong>O que buscamos</strong><ul><li>Python</li><li>FastAPI</li></ul>"

        texto = converter_html_em_texto(html)

        assert texto == "O que buscamos\n- Python\n- FastAPI"

    def test_preserva_a_estrutura_de_titulos_com_quebras_duplas(self):
        html = "<strong>Sobre a empresa<br><br></strong>Somos uma fintech.<br><br><strong>A vaga<br><br></strong>Buscamos pessoas."

        texto = converter_html_em_texto(html)

        assert texto == "Sobre a empresa\n\nSomos uma fintech.\n\nA vaga\n\nBuscamos pessoas."

    def test_remove_script_e_style(self):
        html = "<style>.a{color:red}</style><script>var x = 1;</script><p>Conteúdo da vaga</p>"

        texto = converter_html_em_texto(html)

        assert texto == "Conteúdo da vaga"

    def test_ignora_as_tags_informadas(self):
        html = "<nav>Menu</nav><main><p>Vaga</p></main><footer>Rodapé</footer>"

        texto = converter_html_em_texto(html, ignorar_tags=("nav", "footer"))

        assert texto == "Vaga"

    def test_decodifica_entidades_html(self):
        html = "<p>Experi&ecirc;ncia em R&amp;D &lt;3 anos&gt;</p>"

        texto = converter_html_em_texto(html)

        assert texto == "Experiência em R&D <3 anos>"

    def test_colapsa_espacos_e_linhas_em_branco_repetidas(self):
        html = "<p>  muito     espaço  </p>\n\n\n<p>outro</p>"

        texto = converter_html_em_texto(html)

        assert texto == "muito espaço\n\noutro"

    def test_devolve_texto_vazio_para_html_sem_conteudo(self):
        assert converter_html_em_texto("<div> </div>") == ""
        assert converter_html_em_texto("") == ""
