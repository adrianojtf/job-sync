"""Testes do caso de uso SalvarPerfilEstruturado."""

import pytest

from jobsync.perfil_estruturado import (
    Certificacao,
    ExperienciaProfissional,
    FormacaoAcademica,
    Idioma,
    NivelIdioma,
    PerfilEstruturado,
)
from jobsync.perfil_estruturado.domain.perfil_estruturado_repository import PerfilEstruturadoRepository
from jobsync.perfil_estruturado.service_layer.salvar_perfil_estruturado import (
    SalvarPerfilEstruturado,
    SalvarPerfilEstruturadoInputDto,
)


class RepositorioFake(PerfilEstruturadoRepository):
    def __init__(self):
        self.perfil_salvo: PerfilEstruturado | None = None

    def salvar(self, perfil: PerfilEstruturado) -> PerfilEstruturado:
        self.perfil_salvo = perfil
        return perfil

    def buscar_por_perfil(self, perfil_identificador: str) -> PerfilEstruturado | None:
        return self.perfil_salvo


def _input_dto(**overrides) -> SalvarPerfilEstruturadoInputDto:
    dados = dict(
        perfil_identificador="matheus",
        nome_completo="Matheus Henrique Moreira",
        email="matheus@example.com",
        linkedin="linkedin.com/in/matheus",
        resumo_profissional="Resumo qualquer.",
        experiencias=(),
        formacoes=(),
        certificacoes=(),
        idiomas=(),
        tecnologias=(),
    )
    dados.update(overrides)
    return SalvarPerfilEstruturadoInputDto(**dados)


class TestSalvarPerfilEstruturado:
    def test_salva_perfil_valido(self):
        repositorio = RepositorioFake()
        use_case = SalvarPerfilEstruturado(repositorio=repositorio)

        resultado = use_case.executar(_input_dto())

        assert repositorio.perfil_salvo == resultado.perfil
        assert resultado.perfil.perfil_identificador == "matheus"

    def test_identificador_vazio_gera_erro(self):
        use_case = SalvarPerfilEstruturado(repositorio=RepositorioFake())

        with pytest.raises(ValueError, match="identificador"):
            use_case.executar(_input_dto(perfil_identificador=""))

    def test_nome_completo_vazio_gera_erro(self):
        use_case = SalvarPerfilEstruturado(repositorio=RepositorioFake())

        with pytest.raises(ValueError, match="nome completo"):
            use_case.executar(_input_dto(nome_completo=""))

    def test_email_vazio_gera_erro(self):
        use_case = SalvarPerfilEstruturado(repositorio=RepositorioFake())

        with pytest.raises(ValueError, match="email"):
            use_case.executar(_input_dto(email=""))


class TestSalvarPerfilEstruturadoComSkills:
    def test_inclui_nas_tecnologias_as_skills_das_experiencias_e_informa_quais(self):
        repositorio = RepositorioFake()
        use_case = SalvarPerfilEstruturado(repositorio=repositorio)
        experiencia = ExperienciaProfissional(
            empresa="Starian", cargo="Dev", periodo="2024", descricao="", skills=("Java", "Flyway")
        )

        resultado = use_case.executar(_input_dto(experiencias=(experiencia,), tecnologias=("java", "SQL")))

        assert resultado.tecnologias_incluidas == ("Flyway",)
        assert resultado.perfil.tecnologias == ("java", "SQL", "Flyway")
        assert repositorio.perfil_salvo.tecnologias == ("java", "SQL", "Flyway")

    def test_sem_skills_novas_nao_informa_tecnologias_incluidas(self):
        use_case = SalvarPerfilEstruturado(repositorio=RepositorioFake())

        resultado = use_case.executar(_input_dto(tecnologias=("Python",)))

        assert resultado.tecnologias_incluidas == ()
        assert resultado.perfil.tecnologias == ("Python",)


def _experiencia(periodo: str = "2024 - Atual", empresa: str = "Starian") -> ExperienciaProfissional:
    return ExperienciaProfissional(empresa=empresa, cargo="Dev", periodo=periodo, descricao="")


class TestSalvarPerfilEstruturadoValidaPeriodo:
    def test_periodo_de_experiencia_fora_do_formato_gera_erro_com_posicao_e_exemplo(self):
        use_case = SalvarPerfilEstruturado(repositorio=RepositorioFake())
        experiencias = (_experiencia("2020 - 2022"), _experiencia("ontem"))

        with pytest.raises(ValueError, match=r"Experiência 2: período inválido.*Mar 2024 - Atual"):
            use_case.executar(_input_dto(experiencias=experiencias))

    def test_periodo_de_formacao_fora_do_formato_gera_erro(self):
        use_case = SalvarPerfilEstruturado(repositorio=RepositorioFake())
        formacoes = (FormacaoAcademica(instituicao="USP", curso="BCC", periodo="2020 a 2024"),)

        with pytest.raises(ValueError, match="Formação 1: período inválido"):
            use_case.executar(_input_dto(formacoes=formacoes))

    def test_ano_de_certificacao_invalido_gera_erro(self):
        use_case = SalvarPerfilEstruturado(repositorio=RepositorioFake())
        certificacoes = (Certificacao(nome="AWS", instituicao="Amazon", ano="23"),)

        with pytest.raises(ValueError, match="Certificação 1: ano inválido"):
            use_case.executar(_input_dto(certificacoes=certificacoes))

    def test_inicio_depois_do_fim_gera_erro(self):
        use_case = SalvarPerfilEstruturado(repositorio=RepositorioFake())

        with pytest.raises(ValueError, match="início não pode ser depois do fim"):
            use_case.executar(_input_dto(experiencias=(_experiencia("2024 - 2020"),)))

    @pytest.mark.parametrize("periodo", ["", "  ", "2024", "2020-2022", "Mar 2026 - Atual", "01/2020 - 12/2022"])
    def test_periodos_vazios_ou_validos_sao_aceitos(self, periodo):
        repositorio = RepositorioFake()
        use_case = SalvarPerfilEstruturado(repositorio=repositorio)

        use_case.executar(_input_dto(experiencias=(_experiencia(periodo),)))

        assert repositorio.perfil_salvo is not None

    def test_perfil_recusado_nao_e_salvo(self):
        repositorio = RepositorioFake()
        use_case = SalvarPerfilEstruturado(repositorio=repositorio)

        with pytest.raises(ValueError):
            use_case.executar(_input_dto(experiencias=(_experiencia("ontem"),)))

        assert repositorio.perfil_salvo is None


class TestSalvarPerfilEstruturadoLimiteDeItens:
    def test_ate_quinze_itens_em_cada_lista_sao_aceitos(self):
        use_case = SalvarPerfilEstruturado(repositorio=RepositorioFake())
        dto = _input_dto(
            experiencias=tuple(_experiencia(empresa=f"Empresa {n}") for n in range(15)),
            idiomas=tuple(Idioma(idioma=f"Idioma {n}", nivel=NivelIdioma.BASICO) for n in range(15)),
        )

        use_case.executar(dto)

    @pytest.mark.parametrize(
        ("campo", "lista", "nome"),
        [
            ("experiencias", lambda n: _experiencia(empresa=f"E{n}"), "experiências"),
            ("formacoes", lambda n: FormacaoAcademica(instituicao=f"I{n}", curso="C", periodo=""), "formações"),
            ("certificacoes", lambda n: Certificacao(nome=f"N{n}", instituicao="", ano=""), "certificações"),
            ("idiomas", lambda n: Idioma(idioma=f"L{n}", nivel=NivelIdioma.BASICO), "idiomas"),
        ],
    )
    def test_mais_de_quinze_itens_geram_erro(self, campo, lista, nome):
        use_case = SalvarPerfilEstruturado(repositorio=RepositorioFake())
        dto = _input_dto(**{campo: tuple(lista(n) for n in range(16))})

        with pytest.raises(ValueError, match=f"lista de {nome} aceita no máximo 15"):
            use_case.executar(dto)

    def test_tecnologias_nao_tem_limite(self):
        use_case = SalvarPerfilEstruturado(repositorio=RepositorioFake())

        resultado = use_case.executar(_input_dto(tecnologias=tuple(f"Tec {n}" for n in range(40))))

        assert len(resultado.perfil.tecnologias) == 40
