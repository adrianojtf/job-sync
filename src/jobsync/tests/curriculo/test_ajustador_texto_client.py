"""Testes para o adaptador AjustadorTextoClient."""
from unittest.mock import Mock

import pytest

from jobsync.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from jobsync.curriculo import SecaoCurriculo, TipoSecao

from jobsync.curriculo.adapters.ajustador_texto_client import AjustadorTextoClient
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI


class ClienteOpenAIFake:
    def __init__(self, resposta):
        self.resposta = resposta
        self.prompt_usuario: str | None = None

    def solicitar_json(self, prompt_sistema: str, prompt_usuario: str) -> dict:
        self.prompt_usuario = prompt_usuario
        return self.resposta


def test_ajustador_texto_openai_usa_analise_vaga_estruturada_no_prompt() -> None:
    cliente_fake = ClienteOpenAIFake({"conteudo_ajustado": "Conteúdo ajustado"})
    ajustador = AjustadorTextoClient(cliente_openai=cliente_fake)

    analise_vaga = AnaliseVaga(
        requisitos=(
            RequisitoTecnico(
                nome="Python",
                categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
                tipo=TipoRequisitoTecnico.EXPLICITO,
                origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
            ),
            RequisitoTecnico(
                nome="Desenvolvimento web",
                categoria=CategoriaRequisitoTecnico.HABILIDADE,
                tipo=TipoRequisitoTecnico.IMPLICITO,
                origem=OrigemRequisitoTecnico.INTERPRETACAO,
            ),
        ),
        ambiguidade=("Desejável conhecimento em bancos de dados relacionais",),
        texto_original="Vaga para desenvolvedor backend com Python.",
    )

    secao = SecaoCurriculo(TipoSecao.TECNOLOGIAS, "Tecnologias", "Python, Django")
    secao_ajustada = ajustador.ajustar_secao(
        secao,
        descricao_vaga="Vaga para desenvolvedor backend com Python.",
        idioma_alvo="pt",
        analise_vaga=analise_vaga,
    )

    assert secao_ajustada.conteudo == "Conteúdo ajustado"
    assert cliente_fake.prompt_usuario is not None
    prompt_text = cliente_fake.prompt_usuario.lower()
    assert "requisitos explícitos: python" in prompt_text
    assert "requisitos implícitos: desenvolvimento web" in prompt_text
    assert "trechos ambíguos: desejável conhecimento em bancos de dados relacionais" in prompt_text
    assert "não infira frameworks, ferramentas ou habilidades" in prompt_text


def test_ajustador_texto_openai_resposta_estruturada_em_dict_nao_quebra() -> None:
    """Regressão: o modelo às vezes devolve um objeto em vez de texto puro no campo 'conteudo_ajustado'."""
    cliente_fake = ClienteOpenAIFake({"conteudo_ajustado": {"bullet_1": "Python", "bullet_2": "Django"}})
    ajustador = AjustadorTextoClient(cliente_openai=cliente_fake)

    analise_vaga = AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga qualquer")
    secao = SecaoCurriculo(TipoSecao.TECNOLOGIAS, "Tecnologias", "Python, Django")

    secao_ajustada = ajustador.ajustar_secao(
        secao, descricao_vaga="vaga qualquer", idioma_alvo="pt", analise_vaga=analise_vaga
    )

    assert "Python" in secao_ajustada.conteudo


def _prompt_da_secao(tipo: TipoSecao, idioma: str) -> str:
    cliente_fake = ClienteOpenAIFake({"conteudo_ajustado": "Conteúdo ajustado"})
    ajustador = AjustadorTextoClient(cliente_openai=cliente_fake)
    analise_vaga = AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga qualquer")
    secao = SecaoCurriculo(tipo, "Seção", "Starian - Engenheiro\nCriei APIs.")

    ajustador.ajustar_secao(
        secao, descricao_vaga="vaga qualquer", idioma_alvo=idioma, analise_vaga=analise_vaga
    )

    assert cliente_fake.prompt_usuario is not None
    return cliente_fake.prompt_usuario


def test_prompt_de_experiencias_pede_conquistas_em_bullets_e_linha_final_de_contexto() -> None:
    prompt = _prompt_da_secao(TipoSecao.EXPERIENCIAS, "pt")

    assert "um bloco por experiência" in prompt
    assert "primeira linha de identificação" in prompt
    assert 'iniciada por "- "' in prompt
    assert "de 2 a 6 conquistas" in prompt
    assert '"Contexto: ..."' in prompt
    assert "de 1 a 3 frases" in prompt


def test_prompt_de_experiencias_usa_o_rotulo_de_contexto_do_idioma_alvo() -> None:
    prompt = _prompt_da_secao(TipoSecao.EXPERIENCIAS, "en")

    assert '"Context: ..."' in prompt
    assert '"Contexto: ..."' not in prompt


def test_prompt_de_experiencias_permite_estimar_metricas_quando_o_original_nao_tem_numero() -> None:
    prompt = _prompt_da_secao(TipoSecao.EXPERIENCIAS, "pt")

    assert "Prefira sempre os números do original" in prompt
    assert "métricas e volumes plausíveis e conservadores" in prompt
    assert "Preserve empresas, cargos e datas exatamente como no original" in prompt


def test_prompt_das_outras_secoes_nao_recebe_o_padrao_de_conquistas_e_contexto() -> None:
    prompt = _prompt_da_secao(TipoSecao.PERFIL, "pt")

    assert "Contexto:" not in prompt
    assert "conquistas" not in prompt


def test_prompt_de_sistema_nao_proibe_resultados_que_a_instrucao_de_experiencias_permite() -> None:
    cliente = Mock(spec=ClienteOpenAI)
    cliente.solicitar_json.return_value = {"conteudo_ajustado": "Conteúdo ajustado"}
    secao = SecaoCurriculo(TipoSecao.EXPERIENCIAS, "Experiências", "Starian - Engenheiro")

    AjustadorTextoClient(cliente_openai=cliente).ajustar_secao(
        secao,
        descricao_vaga="vaga",
        idioma_alvo="pt",
        analise_vaga=AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga"),
    )

    sistema = cliente.solicitar_json.call_args.kwargs["prompt_sistema"]
    assert "inventar experiência, empresa ou tecnologia" in sistema
    assert "resultado que não exista" not in sistema


@pytest.mark.parametrize("tipo", list(TipoSecao))
def test_prompt_de_qualquer_secao_pede_para_preservar_linhas_e_topicos(tipo: TipoSecao) -> None:
    prompt = _prompt_da_secao(tipo, "pt")

    assert "Preserve a estrutura de linhas do conteúdo original" in prompt
    assert 'começa com "- "' in prompt
    assert "Nunca junte tópicos ou linhas em um parágrafo" in prompt


def test_prompt_de_tecnologias_pede_uma_categoria_por_linha_sem_criar_categorias() -> None:
    prompt = _prompt_da_secao(TipoSecao.TECNOLOGIAS, "en")

    assert "uma categoria por linha" in prompt
    assert "Rótulo: item1, item2" in prompt
    assert "não crie categorias" in prompt


@pytest.mark.parametrize("tipo", [TipoSecao.PERFIL, TipoSecao.FORMACAO, TipoSecao.IDIOMAS])
def test_prompt_de_outras_secoes_nao_traz_a_regra_de_categorias_de_tecnologia(tipo: TipoSecao) -> None:
    prompt = _prompt_da_secao(tipo, "pt")

    assert "uma categoria por linha" not in prompt
