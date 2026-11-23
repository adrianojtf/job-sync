"""Testes das competências (categorias com tags) do currículo."""
import pytest

from jobsync.curriculo import CategoriaCompetencia, categorias_de_texto, categorias_para_texto


class TestCategoriaCompetencia:
    def test_nome_vazio_gera_erro(self):
        with pytest.raises(ValueError, match="nome da categoria"):
            CategoriaCompetencia(nome="  ", tags=("Java",))

    def test_categoria_sem_tags_gera_erro(self):
        with pytest.raises(ValueError, match="ao menos uma tag"):
            CategoriaCompetencia(nome="Linguagens", tags=())

    def test_revisada_apara_nome_e_tags(self):
        categoria = CategoriaCompetencia.revisada("  Linguagens ", ["  Java", "Python  "])

        assert categoria == CategoriaCompetencia(nome="Linguagens", tags=("Java", "Python"))

    def test_revisada_descarta_tags_vazias(self):
        categoria = CategoriaCompetencia.revisada("Linguagens", ["Java", "  ", ""])

        assert categoria.tags == ("Java",)

    def test_revisada_descarta_tags_duplicadas_sem_diferenciar_caixa(self):
        categoria = CategoriaCompetencia.revisada("Linguagens", ["Java", "java", "JAVA", "Python"])

        assert categoria.tags == ("Java", "Python")

    def test_revisada_devolve_none_sem_nome(self):
        assert CategoriaCompetencia.revisada("  ", ["Java"]) is None

    def test_revisada_devolve_none_sem_tags(self):
        assert CategoriaCompetencia.revisada("Linguagens", ["", "  "]) is None

    def test_para_linha_junta_o_nome_e_as_tags(self):
        categoria = CategoriaCompetencia(nome="Bancos de Dados", tags=("SQL", "PostgreSQL"))

        assert categoria.para_linha() == "Bancos de Dados: SQL, PostgreSQL"


class TestCategoriasDeTexto:
    def test_uma_categoria_por_linha(self):
        texto = "Linguagens: Java, Python\nBancos de Dados: SQL, PostgreSQL"

        assert categorias_de_texto(texto) == (
            CategoriaCompetencia("Linguagens", ("Java", "Python")),
            CategoriaCompetencia("Bancos de Dados", ("SQL", "PostgreSQL")),
        )

    def test_aceita_marcadores_no_inicio_da_linha(self):
        texto = "- Linguagens: Java\n• Frontend: React\n* Ferramentas: Git"

        assert [categoria.nome for categoria in categorias_de_texto(texto)] == [
            "Linguagens",
            "Frontend",
            "Ferramentas",
        ]

    def test_linha_sem_rotulo_vai_para_a_categoria_padrao(self):
        assert categorias_de_texto("Java, Python, SQL") == (
            CategoriaCompetencia("Tecnologias", ("Java", "Python", "SQL")),
        )

    def test_linhas_sem_rotulo_formam_uma_unica_categoria_padrao(self):
        assert categorias_de_texto("Java, Python\nSQL") == (
            CategoriaCompetencia("Tecnologias", ("Java", "Python", "SQL")),
        )

    def test_so_o_primeiro_dois_pontos_separa_o_rotulo(self):
        categorias = categorias_de_texto("Versões: Java 17, Node: 20")

        assert categorias == (CategoriaCompetencia("Versões", ("Java 17", "Node: 20")),)

    def test_virgula_dentro_de_parenteses_nao_separa_tags(self):
        categorias = categorias_de_texto("Backend: Spring (Boot, Data), NestJS")

        assert categorias[0].tags == ("Spring (Boot, Data)", "NestJS")

    def test_ignora_linhas_em_branco_e_categorias_sem_tags(self):
        texto = "\nLinguagens: Java\n\nVazia:\n"

        assert categorias_de_texto(texto) == (CategoriaCompetencia("Linguagens", ("Java",)),)

    def test_texto_vazio_nao_gera_categorias(self):
        assert categorias_de_texto("  \n ") == ()


class TestCategoriasParaTexto:
    def test_uma_categoria_por_linha(self):
        categorias = (
            CategoriaCompetencia("Linguagens", ("Java", "Python")),
            CategoriaCompetencia("Frontend", ("React",)),
        )

        assert categorias_para_texto(categorias) == "Linguagens: Java, Python\nFrontend: React"

    def test_ida_e_volta_preserva_as_categorias(self):
        categorias = (
            CategoriaCompetencia("Backend", ("Spring (Boot, Data)", "NestJS")),
            CategoriaCompetencia("Ferramentas", ("Git", "Docker")),
        )

        assert categorias_de_texto(categorias_para_texto(categorias)) == categorias
