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
from jobsync.curriculo import ContextoVaga, EquivalenciaTecnologia, PedidoRefino, SecaoCurriculo, TipoSecao

from jobsync.curriculo.adapters.prompt_contexto_vaga import LIMITE_DE_CONQUISTAS_NO_RESUMO
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
        ContextoVaga(
            descricao_vaga="Vaga para desenvolvedor backend com Python.",
            idioma_alvo="pt",
            analise_vaga=analise_vaga,
        ),
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
        secao, ContextoVaga(descricao_vaga="vaga qualquer", idioma_alvo="pt", analise_vaga=analise_vaga)
    )

    assert "Python" in secao_ajustada.conteudo


def _prompt_da_secao(
    tipo: TipoSecao,
    idioma: str,
    cargo_alvo: str = "",
    ajustes: tuple[EquivalenciaTecnologia, ...] = (),
    itens_permitidos: tuple[str, ...] | None = None,
    conquistas_do_historico: tuple[str, ...] = (),
) -> str:
    cliente_fake = ClienteOpenAIFake({"conteudo_ajustado": "Conteúdo ajustado"})
    ajustador = AjustadorTextoClient(cliente_openai=cliente_fake)
    analise_vaga = AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga qualquer")
    secao = SecaoCurriculo(tipo, "Seção", "Starian - Engenheiro\nCriei APIs.")

    ajustador.ajustar_secao(
        secao,
        ContextoVaga(
            descricao_vaga="vaga qualquer",
            idioma_alvo=idioma,
            analise_vaga=analise_vaga,
            cargo_alvo=cargo_alvo,
            conquistas_do_historico=conquistas_do_historico,
        ),
        ajustes,
        itens_permitidos,
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
        ContextoVaga(
            descricao_vaga="vaga",
            idioma_alvo="pt",
            analise_vaga=AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga"),
        ),
    )

    sistema = cliente.solicitar_json.call_args.kwargs["prompt_sistema"]
    assert "inventar experiência, empresa ou tecnologia" in sistema
    assert "resultado que não exista" not in sistema


def test_prompt_traz_o_cargo_alvo_quando_informado() -> None:
    prompt = _prompt_da_secao(TipoSecao.PERFIL, "pt", cargo_alvo="Code Reviewer")

    assert "Cargo-alvo (título da vaga): Code Reviewer" in prompt


def test_prompt_omite_o_cargo_alvo_quando_vazio() -> None:
    prompt = _prompt_da_secao(TipoSecao.PERFIL, "pt")

    assert "Cargo-alvo" not in prompt


REACT_ANGULAR = EquivalenciaTecnologia(original="React", alvo="Angular")


def test_tecnologias_listam_a_original_e_a_equivalente() -> None:
    prompt = _prompt_da_secao(TipoSecao.TECNOLOGIAS, "pt", ajustes=(REACT_ANGULAR,))

    assert "Liste também Angular ao lado de React" in prompt


def test_perfil_pode_citar_a_tecnologia_equivalente() -> None:
    prompt = _prompt_da_secao(TipoSecao.PERFIL, "pt", ajustes=(REACT_ANGULAR,))

    assert "Pode citar Angular, equivalente a React" in prompt


def test_sem_ajustes_o_prompt_nao_cita_equivalencias() -> None:
    prompt = _prompt_da_secao(TipoSecao.TECNOLOGIAS, "pt")

    assert "Liste também" not in prompt


def test_perfil_proibe_tecnologia_inventada_com_a_excecao_das_equivalentes() -> None:
    prompt = _prompt_da_secao(TipoSecao.PERFIL, "pt")

    assert "cargos ou tecnologias que não constam" not in prompt
    assert "empresas, tecnologias, práticas nem métricas, exceto as tecnologias equivalentes" in prompt


def test_experiencias_da_fonte_pdf_trazem_a_regra_de_responsabilidades_implicitas() -> None:
    prompt = _prompt_da_secao(TipoSecao.EXPERIENCIAS, "pt")

    assert "responsabilidade essencial da vaga" in prompt
    assert "não invente métricas para elas" in prompt


def test_prompt_de_sistema_usa_o_cargo_alvo_para_a_enfase() -> None:
    cliente = Mock(spec=ClienteOpenAI)
    cliente.solicitar_json.return_value = {"conteudo_ajustado": "Conteúdo ajustado"}

    AjustadorTextoClient(cliente_openai=cliente).ajustar_secao(
        SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Engenheiro."),
        ContextoVaga(
            descricao_vaga="vaga",
            idioma_alvo="pt",
            analise_vaga=AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga"),
        ),
    )

    sistema = cliente.solicitar_json.call_args.kwargs["prompt_sistema"]
    assert "use o cargo-alvo para escolher a ênfase e o vocabulário" in sistema



def _prompt_do_refino(refino: PedidoRefino) -> tuple[str, str, SecaoCurriculo]:
    cliente = Mock(spec=ClienteOpenAI)
    cliente.solicitar_json.return_value = {"conteudo_ajustado": "  Resumo refinado.  "}
    secao = SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Resumo atual editado.")

    refinada = AjustadorTextoClient(cliente_openai=cliente).refinar_secao(
        secao,
        ContextoVaga(
            descricao_vaga="Vaga Angular",
            idioma_alvo="pt",
            analise_vaga=AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="Vaga Angular"),
            cargo_alvo="Code Reviewer",
        ),
        refino,
    )

    argumentos = cliente.solicitar_json.call_args.kwargs
    return argumentos["prompt_sistema"], argumentos["prompt_usuario"], refinada


def test_refinar_secao_parte_do_texto_atual_e_nao_do_conteudo_original() -> None:
    _, usuario, refinada = _prompt_do_refino(PedidoRefino())

    assert refinada == SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Resumo refinado.")
    assert "Texto atual:\nResumo atual editado." in usuario
    assert "Conteúdo original" not in usuario
    assert "Vaga Angular" in usuario
    assert "Cargo-alvo (título da vaga): Code Reviewer" in usuario


def test_refinar_secao_usa_o_foco_da_tentativa_e_as_sugestoes_anteriores() -> None:
    _, usuario, _ = _prompt_do_refino(
        PedidoRefino(tentativa=3, sugestoes_anteriores=("Versão 1.", "Versão 2."))
    )

    assert "Foco desta versão: palavras-chave da vaga" in usuario
    assert "Não repita estas versões já sugeridas" in usuario
    assert "Versão 1." in usuario and "Versão 2." in usuario


def test_refinar_secao_mantem_as_regras_da_secao() -> None:
    sistema, usuario, _ = _prompt_do_refino(PedidoRefino())

    assert "não invente anos de experiência, cargos, empresas, tecnologias, práticas nem métricas" in usuario
    assert "conteudo_ajustado" in sistema
@pytest.mark.parametrize("tipo", list(TipoSecao))
def test_prompt_de_qualquer_secao_pede_para_preservar_linhas_e_topicos(tipo: TipoSecao) -> None:
    prompt = _prompt_da_secao(tipo, "pt")

    assert "Preserve a estrutura de linhas do conteúdo original" in prompt
    assert 'começa com "- "' in prompt
    assert "Nunca junte tópicos ou linhas em um parágrafo" in prompt


def test_prompt_de_tecnologias_pede_uma_categoria_por_linha_no_formato_rotulo_e_itens() -> None:
    prompt = _prompt_da_secao(TipoSecao.TECNOLOGIAS, "en")

    assert "uma categoria por linha" in prompt
    assert "Rótulo: item1, item2" in prompt


def test_prompt_de_tecnologias_mantem_as_categorias_que_o_original_ja_tem() -> None:
    prompt = _prompt_da_secao(TipoSecao.TECNOLOGIAS, "pt")

    assert "Se o original já tiver categorias, mantenha-as" in prompt


@pytest.mark.parametrize(
    "rotulo",
    [
        "Linguagens",
        "Backend e APIs",
        "IA no Desenvolvimento",
        "Qualidade e Testes",
        "Práticas de Engenharia",
        "Bancos de Dados",
        "Frontend",
        "Ferramentas",
    ],
)
def test_prompt_de_tecnologias_sugere_as_categorias_padrao_quando_a_lista_vem_solta(rotulo: str) -> None:
    prompt = _prompt_da_secao(TipoSecao.TECNOLOGIAS, "pt")

    assert rotulo in prompt
    assert "lista única" in prompt


def test_prompt_de_tecnologias_nao_manda_deixar_tudo_em_uma_categoria() -> None:
    prompt = _prompt_da_secao(TipoSecao.TECNOLOGIAS, "pt")

    assert "não crie categorias" not in prompt


def test_prompt_de_tecnologias_pede_rotulos_no_idioma_de_saida_e_sem_inventar_tecnologias() -> None:
    prompt = _prompt_da_secao(TipoSecao.TECNOLOGIAS, "en")

    assert "no idioma de saída" in prompt
    assert "não repita a mesma tecnologia" in prompt


@pytest.mark.parametrize("tipo", [TipoSecao.PERFIL, TipoSecao.FORMACAO, TipoSecao.IDIOMAS])
def test_prompt_de_outras_secoes_nao_traz_a_regra_de_categorias_de_tecnologia(tipo: TipoSecao) -> None:
    prompt = _prompt_da_secao(tipo, "pt")

    assert "uma categoria por linha" not in prompt


def test_perfil_pede_resumo_de_ate_60_palavras_em_um_paragrafo_de_ate_3_frases() -> None:
    prompt = _prompt_da_secao(TipoSecao.PERFIL, "pt")

    assert "um único parágrafo de até 60 palavras e até 3 frases" in prompt
    assert "mesma voz do resumo original" in prompt


def test_perfil_usa_o_cargo_alvo_como_eixo_sem_declarar_cargo_nao_exercido() -> None:
    prompt = _prompt_da_secao(TipoSecao.PERFIL, "pt")

    assert "na linha do cargo-alvo" in prompt
    assert "sem declarar como título um cargo que ele não exerceu" in prompt


def test_perfil_limita_a_3_temas_escritos_como_acoes_do_candidato() -> None:
    prompt = _prompt_da_secao(TipoSecao.PERFIL, "pt")

    assert "no máximo 3 temas centrais da vaga" in prompt
    assert "como ações do candidato" in prompt


def test_perfil_proibe_copiar_a_vaga_listas_ponto_e_virgula_e_falar_da_vaga() -> None:
    prompt = _prompt_da_secao(TipoSecao.PERFIL, "pt")

    assert "não copie trechos da vaga" in prompt
    assert "não faça listas de termos" in prompt
    assert "não use ponto e vírgula" in prompt
    assert "não fale da vaga nem da oportunidade" in prompt


def test_perfil_omite_tema_sem_sustentacao_e_nao_inventa_fatos() -> None:
    prompt = _prompt_da_secao(TipoSecao.PERFIL, "pt")

    assert "Omita o tema que o histórico não sustenta" in prompt
    assert "não invente anos de experiência, cargos, empresas, tecnologias, práticas nem métricas" in prompt


def test_perfil_nao_recebe_a_ordem_de_incluir_as_tecnologias_da_vaga() -> None:
    prompt = _prompt_da_secao(TipoSecao.PERFIL, "pt")

    assert "Cada tecnologia da análise de vaga deve aparecer no texto final" not in prompt
    assert "Não inclua tecnologias da vaga que o histórico do candidato não sustenta" in prompt


@pytest.mark.parametrize("tipo", [tipo for tipo in TipoSecao if tipo != TipoSecao.PERFIL])
def test_nenhuma_outra_secao_recebe_a_ordem_de_incluir_as_tecnologias_da_vaga(tipo: TipoSecao) -> None:
    prompt = _prompt_da_secao(tipo, "pt")

    assert "Cada tecnologia da análise de vaga deve aparecer no texto final" not in prompt
    assert "Inclua explicitamente na seção reescrita todas as tecnologias" not in prompt


def test_perfil_mantem_o_complemento_de_tecnologia_equivalente_com_a_nova_regra() -> None:
    prompt = _prompt_da_secao(TipoSecao.PERFIL, "pt", ajustes=(REACT_ANGULAR,), cargo_alvo="Code Reviewer")

    assert "no máximo 3 temas centrais da vaga" in prompt
    assert "Pode citar Angular, equivalente a React" in prompt
    assert "Cargo-alvo (título da vaga): Code Reviewer" in prompt


@pytest.mark.parametrize("tipo", [tipo for tipo in TipoSecao if tipo != TipoSecao.PERFIL])
def test_prompt_de_outras_secoes_nao_traz_a_regra_do_resumo(tipo: TipoSecao) -> None:
    prompt = _prompt_da_secao(tipo, "pt")

    assert "no máximo 3 temas centrais da vaga" not in prompt
    assert "não copie trechos da vaga" not in prompt


@pytest.mark.parametrize("tentativa", [1, 2, 3, 4])
def test_refinar_o_perfil_traz_a_regra_do_resumo_em_qualquer_foco(tentativa: int) -> None:
    _, usuario, _ = _prompt_do_refino(PedidoRefino(tentativa=tentativa))

    assert "temas centrais da vaga" in usuario
    assert "não copie trechos da vaga" in usuario


def test_refinar_o_perfil_com_foco_de_aderencia_parte_do_texto_atual_com_a_regra() -> None:
    _, usuario, _ = _prompt_do_refino(PedidoRefino(tentativa=1))

    assert "Foco desta versão: aderência à vaga" in usuario
    assert "Texto atual:\nResumo atual editado." in usuario
    assert "até 60 palavras e até 3 frases" in usuario


def test_refino_do_perfil_com_foco_palavras_chave_mantem_a_proibicao_de_copiar_a_vaga() -> None:
    _, usuario, _ = _prompt_do_refino(PedidoRefino(tentativa=3))

    assert "Foco desta versão: palavras-chave da vaga" in usuario
    assert "não copie trechos da vaga" in usuario
    assert "não faça listas de termos" in usuario
    assert "Cada tecnologia da análise de vaga deve aparecer no texto final" not in usuario


@pytest.mark.parametrize("tipo", list(TipoSecao))
def test_nenhum_prompt_manda_incluir_todas_as_tecnologias_da_vaga(tipo: TipoSecao) -> None:
    prompt = _prompt_da_secao(tipo, "pt", itens_permitidos=("Java",))

    assert "todas as tecnologias" not in prompt
    assert "deve aparecer no texto final" not in prompt


def test_o_refino_tambem_nao_manda_incluir_todas_as_tecnologias_da_vaga() -> None:
    _, usuario, _ = _prompt_do_refino(PedidoRefino())

    assert "todas as tecnologias" not in usuario


def test_tecnologias_com_itens_permitidos_lista_cada_item_e_proibe_os_demais() -> None:
    prompt = _prompt_da_secao(TipoSecao.TECNOLOGIAS, "pt", itens_permitidos=("Java", "PostgreSQL", "Docker"))

    assert "Itens permitidos: Java, PostgreSQL, Docker" in prompt
    assert "use somente estes itens" in prompt
    assert "não acrescente nenhum outro" in prompt


def test_tecnologias_com_itens_permitidos_pede_ordenar_pelo_que_a_vaga_mais_pede() -> None:
    prompt = _prompt_da_secao(TipoSecao.TECNOLOGIAS, "pt", itens_permitidos=("Java",))

    assert "mais relevantes para a vaga" in prompt


def test_tecnologias_sem_a_lista_permitida_nao_acrescenta_tecnologias_da_vaga() -> None:
    prompt = _prompt_da_secao(TipoSecao.TECNOLOGIAS, "pt")

    assert "Itens permitidos" not in prompt
    assert "não acrescente tecnologias da vaga" in prompt


def test_tecnologias_com_equivalencia_continua_pedindo_a_original_ao_lado_da_alvo() -> None:
    prompt = _prompt_da_secao(
        TipoSecao.TECNOLOGIAS, "pt", ajustes=(REACT_ANGULAR,), itens_permitidos=("React", "Angular")
    )

    assert "Liste também Angular ao lado de React" in prompt


@pytest.mark.parametrize("tipo", [tipo for tipo in TipoSecao if tipo != TipoSecao.TECNOLOGIAS])
def test_as_outras_secoes_nao_recebem_a_lista_de_itens_permitidos(tipo: TipoSecao) -> None:
    prompt = _prompt_da_secao(tipo, "pt", itens_permitidos=("Java",))

    assert "Itens permitidos" not in prompt


def test_o_refino_de_tecnologias_nao_acrescenta_tecnologias_da_vaga() -> None:
    cliente = Mock(spec=ClienteOpenAI)
    cliente.solicitar_json.return_value = {"conteudo_ajustado": "Linguagens: Java"}

    AjustadorTextoClient(cliente_openai=cliente).refinar_secao(
        SecaoCurriculo(TipoSecao.TECNOLOGIAS, "Competências", "Linguagens: Java"),
        ContextoVaga(
            descricao_vaga="Vaga Kafka",
            idioma_alvo="pt",
            analise_vaga=AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="Vaga Kafka"),
        ),
        PedidoRefino(),
    )

    assert "não acrescente tecnologias da vaga" in cliente.solicitar_json.call_args.kwargs["prompt_usuario"]


CONQUISTAS_DO_HISTORICO = (
    "Atuei junto ao cliente na entrega de um MVP.",
    "Reduzi o tempo de deploy.",
)


def test_perfil_traz_as_conquistas_do_historico_como_base_de_fatos() -> None:
    prompt = _prompt_da_secao(TipoSecao.PERFIL, "pt", conquistas_do_historico=CONQUISTAS_DO_HISTORICO)

    assert "Conquistas do histórico do candidato" in prompt
    assert all(f"- {conquista}" in prompt for conquista in CONQUISTAS_DO_HISTORICO)
    assert "o histórico sustenta" in prompt
    assert "não copie as conquistas" in prompt


def test_perfil_sem_conquistas_do_historico_nao_traz_o_bloco() -> None:
    prompt = _prompt_da_secao(TipoSecao.PERFIL, "pt")

    assert "Conquistas do histórico do candidato" not in prompt


@pytest.mark.parametrize("tipo", [tipo for tipo in TipoSecao if tipo != TipoSecao.PERFIL])
def test_outras_secoes_nao_trazem_as_conquistas_do_historico(tipo: TipoSecao) -> None:
    prompt = _prompt_da_secao(tipo, "pt", conquistas_do_historico=CONQUISTAS_DO_HISTORICO)

    assert "Conquistas do histórico do candidato" not in prompt


def test_perfil_limita_as_conquistas_do_historico_as_primeiras() -> None:
    conquistas = tuple(f"Conquista numero {numero:02d}." for numero in range(LIMITE_DE_CONQUISTAS_NO_RESUMO + 5))

    prompt = _prompt_da_secao(TipoSecao.PERFIL, "pt", conquistas_do_historico=conquistas)

    assert f"- {conquistas[LIMITE_DE_CONQUISTAS_NO_RESUMO - 1]}" in prompt
    assert f"- {conquistas[LIMITE_DE_CONQUISTAS_NO_RESUMO]}" not in prompt


def test_refino_do_perfil_tambem_traz_as_conquistas_do_historico() -> None:
    cliente = Mock(spec=ClienteOpenAI)
    cliente.solicitar_json.return_value = {"conteudo_ajustado": "Resumo refinado."}
    secao = SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Resumo atual editado.")
    contexto = ContextoVaga(
        descricao_vaga="Vaga",
        idioma_alvo="pt",
        analise_vaga=AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="Vaga"),
        conquistas_do_historico=CONQUISTAS_DO_HISTORICO,
    )

    AjustadorTextoClient(cliente_openai=cliente).refinar_secao(secao, contexto, PedidoRefino())

    assert "- Reduzi o tempo de deploy." in cliente.solicitar_json.call_args.kwargs["prompt_usuario"]
