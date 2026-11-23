"""Testes da seleção do que entra em Competências e do corte pelo teto."""
from jobsync.curriculo import (
    CategoriaCompetencia,
    EquivalenciaTecnologia,
    SelecaoDeCompetencias,
    limitar_ao_teto,
    restringir_aos_permitidos,
)
from jobsync.vaga import (
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)


def _requisito(nome: str, categoria: CategoriaRequisitoTecnico = CategoriaRequisitoTecnico.TECNOLOGIA):
    return RequisitoTecnico(
        nome=nome,
        categoria=categoria,
        tipo=TipoRequisitoTecnico.EXPLICITO,
        origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
    )


def _selecionar(itens=(), textos=(), requisitos=(), equivalencias=()):
    return SelecaoDeCompetencias().selecionar(itens, textos, requisitos, equivalencias)


class TestSelecaoDeCompetencias:
    def test_sem_vaga_os_permitidos_sao_os_itens_do_candidato(self):
        resultado = _selecionar(itens=("Java", "Python"))

        assert resultado.permitidos == ("Java", "Python")
        assert resultado.lacunas == ()

    def test_tecnologia_da_vaga_sem_evidencia_vira_lacuna_e_nao_entra(self):
        resultado = _selecionar(itens=("Java",), requisitos=(_requisito("Kafka"),))

        assert resultado.permitidos == ("Java",)
        assert resultado.lacunas == ("Kafka",)

    def test_tecnologia_da_vaga_citada_numa_experiencia_tem_evidencia_e_entra(self):
        resultado = _selecionar(
            itens=("Java",),
            textos=("Mensageria com RabbitMQ no billing.",),
            requisitos=(_requisito("RabbitMQ"),),
        )

        assert resultado.permitidos == ("Java", "RabbitMQ")
        assert resultado.lacunas == ()

    def test_a_citacao_na_experiencia_respeita_palavra_inteira(self):
        resultado = _selecionar(
            itens=("Python",),
            textos=("Telas em JavaScript.",),
            requisitos=(_requisito("Java"),),
        )

        assert resultado.permitidos == ("Python",)
        assert resultado.lacunas == ("Java",)

    def test_equivalencia_aplicada_acrescenta_a_tecnologia_alvo(self):
        resultado = _selecionar(
            itens=("React",),
            requisitos=(_requisito("Angular"),),
            equivalencias=(EquivalenciaTecnologia(original="React", alvo="Angular"),),
        )

        assert resultado.permitidos == ("React", "Angular")
        assert resultado.lacunas == ()

    def test_requisito_que_nao_e_tecnologia_nem_ferramenta_e_ignorado(self):
        resultado = _selecionar(
            itens=("Java",),
            requisitos=(
                _requisito("aprovação humana", CategoriaRequisitoTecnico.HABILIDADE),
                _requisito("serviços financeiros", CategoriaRequisitoTecnico.OUTRA),
                _requisito("Scrum", CategoriaRequisitoTecnico.METODOLOGIA),
            ),
        )

        assert resultado.permitidos == ("Java",)
        assert resultado.lacunas == ()

    def test_ferramenta_sem_evidencia_tambem_vira_lacuna(self):
        resultado = _selecionar(
            itens=("Java",), requisitos=(_requisito("Terraform", CategoriaRequisitoTecnico.FERRAMENTA),)
        )

        assert resultado.lacunas == ("Terraform",)

    def test_requisito_ja_coberto_por_um_item_do_candidato_nao_vira_lacuna(self):
        resultado = _selecionar(
            itens=("Spring Boot",), requisitos=(_requisito("Spring"), _requisito("spring boot"))
        )

        assert resultado.permitidos == ("Spring Boot",)
        assert resultado.lacunas == ()

    def test_compara_sem_diferenciar_maiusculas_e_minusculas_e_remove_duplicatas(self):
        resultado = _selecionar(
            itens=("Java", "java", " Python "), requisitos=(_requisito("JAVA"), _requisito("kafka"), _requisito("Kafka"))
        )

        assert resultado.permitidos == ("Java", "Python")
        assert resultado.lacunas == ("kafka",)

    def test_lacunas_seguem_a_ordem_da_vaga(self):
        resultado = _selecionar(requisitos=(_requisito("Go"), _requisito("Kafka"), _requisito("AWS")))

        assert resultado.lacunas == ("Go", "Kafka", "AWS")

    def test_item_do_candidato_em_branco_e_descartado(self):
        assert _selecionar(itens=("  ", "Java")).permitidos == ("Java",)


class TestLimitarAoTeto:
    def _categorias(self):
        return (
            CategoriaCompetencia("Linguagens", ("Java", "Python", "Go")),
            CategoriaCompetencia("Ferramentas", ("Git", "Docker", "Maven")),
        )

    def test_abaixo_do_teto_nao_muda(self):
        assert limitar_ao_teto(self._categorias(), {"java"}, teto=10) == self._categorias()

    def test_acima_do_teto_remove_primeiro_os_nao_relevantes_a_partir_do_fim(self):
        resultado = limitar_ao_teto(self._categorias(), {"docker"}, teto=4)

        assert resultado == (
            CategoriaCompetencia("Linguagens", ("Java", "Python", "Go")),
            CategoriaCompetencia("Ferramentas", ("Docker",)),
        )

    def test_so_remove_relevantes_quando_nao_sobra_item_irrelevante(self):
        resultado = limitar_ao_teto(self._categorias(), {"java", "python", "go", "git", "docker", "maven"}, teto=4)

        assert [tag for categoria in resultado for tag in categoria.tags] == ["Java", "Python", "Go", "Git"]

    def test_categoria_que_fica_sem_item_some(self):
        resultado = limitar_ao_teto(self._categorias(), {"java", "python", "go"}, teto=3)

        assert resultado == (CategoriaCompetencia("Linguagens", ("Java", "Python", "Go")),)

    def test_relevantes_sem_diferenciar_maiusculas_e_minusculas(self):
        resultado = limitar_ao_teto(self._categorias(), {"DOCKER"}, teto=1)

        assert resultado == (CategoriaCompetencia("Ferramentas", ("Docker",)),)

    def test_o_teto_padrao_e_45(self):
        muitas = (CategoriaCompetencia("Tudo", tuple(f"T{n}" for n in range(60))),)

        resultado = limitar_ao_teto(muitas, set())

        assert len(resultado[0].tags) == 45
        assert resultado[0].tags[0] == "T0"


class TestRelevantes:
    def test_relevantes_sao_os_permitidos_que_a_vaga_pede(self):
        resultado = _selecionar(
            itens=("Java", "Python", "Spring Boot"),
            requisitos=(_requisito("Java"), _requisito("Spring")),
        )

        assert resultado.relevantes == ("Java", "Spring Boot")

    def test_a_relevancia_vale_nos_dois_sentidos_do_nome(self):
        resultado = _selecionar(itens=("Spring",), requisitos=(_requisito("Spring Boot"),))

        assert resultado.relevantes == ("Spring",)

    def test_sem_requisitos_nada_e_relevante(self):
        assert _selecionar(itens=("Java",)).relevantes == ()


class TestRestringirAosPermitidos:
    def test_descarta_o_que_nao_esta_nos_permitidos_sem_diferenciar_caixa(self):
        categorias = (
            CategoriaCompetencia("Linguagens", ("Java", "Rust", "python")),
            CategoriaCompetencia("Ferramentas", ("Kafka",)),
        )

        resultado = restringir_aos_permitidos(categorias, ("Java", "Python"))

        assert resultado == (CategoriaCompetencia("Linguagens", ("Java", "python")),)

    def test_nao_muda_o_que_ja_esta_dentro_dos_permitidos(self):
        categorias = (CategoriaCompetencia("Linguagens", ("Java", "Python")),)

        assert restringir_aos_permitidos(categorias, ("Python", "Java")) == categorias

    def test_sem_permitidos_nao_sobra_categoria(self):
        categorias = (CategoriaCompetencia("Linguagens", ("Java",)),)

        assert restringir_aos_permitidos(categorias, ()) == ()
