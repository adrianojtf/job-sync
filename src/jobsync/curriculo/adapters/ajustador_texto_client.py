"""Adapter (implementa AjustadorTextoPort) que reescreve uma seção do currículo via IA.

Cada seção é processada de forma isolada e independente: o prompt varia
conforme o tipo de seção (Tecnologias, Perfil, Experiências, Formação),
priorizando o conteúdo mais relevante para a vaga-alvo e traduzindo/adaptando
para o idioma solicitado, sem inventar fatos que não constam no original.
"""
from __future__ import annotations

from collections.abc import Sequence

from jobsync.curriculo.adapters.prompt_contexto_vaga import (
    REGRA_RESPONSABILIDADES_IMPLICITAS,
    REGRA_RESUMO_ADERENTE_A_VAGA,
    bloco_conquistas_do_historico,
    linha_cargo_alvo,
)
from jobsync.curriculo.adapters.prompt_refino import bloco_refino
from jobsync.curriculo.domain.ajustador_texto_port import AjustadorTextoPort
from jobsync.curriculo.domain.equivalencia_tecnologia import EquivalenciaTecnologia
from jobsync.curriculo.domain.refino import PedidoRefino
from jobsync.curriculo.domain.rotulos_experiencia import ROTULO_CONTEXTO
from jobsync.vaga import TipoRequisitoTecnico
from jobsync.curriculo import ContextoVaga, SecaoCurriculo, TipoSecao
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI

_NOME_IDIOMA = {"pt": "português do Brasil", "en": "inglês (formato americano de currículo)"}

_INSTRUCOES_POR_TIPO: dict[TipoSecao, str] = {
    TipoSecao.TECNOLOGIAS: (
        "Escreva uma categoria por linha, no formato 'Rótulo: item1, item2'. "
        "Se o original já tiver categorias, mantenha-as. "
        "Se o original for uma lista única, agrupe as tecnologias em categorias e use, de preferência, "
        "estes rótulos: Linguagens, Backend e APIs, IA no Desenvolvimento, Qualidade e Testes, "
        "Práticas de Engenharia, Bancos de Dados, Frontend, Ferramentas. "
        "Use só as categorias que tiverem itens, escreva os rótulos no idioma de saída e "
        "não repita a mesma tecnologia em duas categorias."
    ),
    TipoSecao.PERFIL: REGRA_RESUMO_ADERENTE_A_VAGA,
    TipoSecao.FORMACAO: (
        "Apenas traduza/adapte o idioma, se necessário. Não altere instituições, "
        "cursos ou datas."
    ),
    TipoSecao.CERTIFICACOES: "Apenas traduza/adapte o idioma, se necessário, sem alterar os fatos.",
    TipoSecao.IDIOMAS: "Apenas traduza/adapte o idioma, se necessário, sem alterar os fatos.",
}

def _instrucao_experiencias(rotulo_contexto: str) -> str:
    """Padrão de conquistas e contexto para a seção de experiências vinda de um PDF.

    A linha final no formato "Rótulo: ..." é a convenção que o gerador de PDF reconhece.
    """
    return (
        "Reescreva cada experiência no padrão de conquistas e contexto, com um bloco por experiência, "
        "separado do próximo por uma linha em branco. Em cada bloco: "
        "(1) mantenha a primeira linha de identificação (cargo, empresa e período) como no original; "
        '(2) liste de 2 a 6 conquistas, uma por linha, cada uma iniciada por "- ", em frases curtas '
        "que começam com verbo de ação e citam o resultado medido quando houver dado; "
        f'(3) termine com uma única linha "{rotulo_contexto}: ..." com de 1 a 3 frases sobre a empresa, '
        "a área e o papel, sem repetir as conquistas. "
        "Preserve empresas, cargos e datas exatamente como no original. "
        "Prefira sempre os números do original; quando ele não trouxer número, você pode propor "
        "métricas e volumes plausíveis e conservadores. "
        f"{REGRA_RESPONSABILIDADES_IMPLICITAS}"
    )


def _instrucao_de_tecnologias(itens_permitidos: Sequence[str] | None) -> str:
    """Competências: o domínio decide o que entra (JOB-0044); a IA só agrupa e ordena."""
    if itens_permitidos is None:
        return "Use só as tecnologias que já estão no conteúdo e não acrescente tecnologias da vaga."
    return (
        f"Itens permitidos: {', '.join(itens_permitidos) or 'nenhum'}. "
        "Organize e ordene com as mais relevantes para a vaga primeiro, "
        "use somente estes itens, sem remover nenhum, e não acrescente nenhum outro, "
        "mesmo que a vaga o peça."
    )


def _instrucao_da_secao(
    tipo: TipoSecao,
    idioma_alvo: str,
    ajustes: Sequence[EquivalenciaTecnologia],
    itens_permitidos: Sequence[str] | None = None,
) -> str:
    """Instrução específica do tipo de seção, com as trocas de tecnologia quando houver."""
    if tipo == TipoSecao.EXPERIENCIAS:
        return _instrucao_experiencias(ROTULO_CONTEXTO.get(idioma_alvo, ROTULO_CONTEXTO["pt"]))
    instrucao = _INSTRUCOES_POR_TIPO.get(tipo, "Traduza/adapte o idioma, mantendo os fatos originais.")
    if tipo == TipoSecao.TECNOLOGIAS:
        complementos = [
            _instrucao_de_tecnologias(itens_permitidos),
            *(f"Liste também {ajuste.alvo} ao lado de {ajuste.original}." for ajuste in ajustes),
        ]
    elif tipo == TipoSecao.PERFIL:
        complementos = [
            f"Pode citar {ajuste.alvo}, equivalente a {ajuste.original}, já usada pelo candidato."
            for ajuste in ajustes
        ]
    else:
        complementos = []
    return " ".join([instrucao, *complementos])


_NAO_INCLUIR_TECNOLOGIAS_AUSENTES_NO_RESUMO = (
    "Não inclua tecnologias da vaga que o histórico do candidato não sustenta; "
    "o resumo cita só as que o histórico mostra."
)


def _instrucao_de_tecnologias_da_vaga(tipo: TipoSecao) -> str:
    """Nenhuma seção recebe a ordem de listar todas as tecnologias da vaga (JOB-0044).

    O que entra em Competências é decidido pelo domínio; o resumo só cita o que o histórico mostra.
    """
    return _NAO_INCLUIR_TECNOLOGIAS_AUSENTES_NO_RESUMO if tipo == TipoSecao.PERFIL else ""


_PROMPT_SISTEMA = """\
Você é um especialista em redação de currículos (resume writer) que ajuda \
candidatos a adaptar seu currículo para vagas específicas, SEM jamais \
inventar experiência, empresa ou tecnologia que não exista no texto original, \
exceto as tecnologias equivalentes indicadas na instrução da seção. \
Quando houver cargo-alvo, use o cargo-alvo para escolher a ênfase e o vocabulário. \
O que fazer com números e métricas é definido na instrução específica de cada seção.

Responda ESTRITAMENTE em JSON no formato:
{"conteudo_ajustado": "texto da seção já reescrita"}
"""


class AjustadorTextoClient(AjustadorTextoPort):
    """Reescreve o conteúdo de uma seção do currículo usando GPT-6 Luna."""

    def __init__(self, cliente_openai: ClienteOpenAI | None = None) -> None:
        self._cliente_openai = cliente_openai or ClienteOpenAI()

    def ajustar_secao(
        self,
        secao: SecaoCurriculo,
        contexto: ContextoVaga,
        ajustes: Sequence[EquivalenciaTecnologia] = (),
        itens_permitidos: Sequence[str] | None = None,
    ) -> SecaoCurriculo:
        return self._solicitar(
            secao, contexto, ajustes, rotulo_texto="Conteúdo original", itens_permitidos=itens_permitidos
        )

    def refinar_secao(
        self, secao: SecaoCurriculo, contexto: ContextoVaga, refino: PedidoRefino
    ) -> SecaoCurriculo:
        return self._solicitar(
            secao,
            contexto,
            ajustes=(),
            rotulo_texto="Texto atual",
            instrucao_refino=f"{bloco_refino(refino, com_vaga=True)}\n\n",
        )

    def _solicitar(
        self,
        secao: SecaoCurriculo,
        contexto: ContextoVaga,
        ajustes: Sequence[EquivalenciaTecnologia],
        rotulo_texto: str,
        instrucao_refino: str = "",
        itens_permitidos: Sequence[str] | None = None,
    ) -> SecaoCurriculo:
        idioma_alvo = contexto.idioma_alvo
        analise_vaga = contexto.analise_vaga
        instrucao_especifica = _instrucao_da_secao(secao.tipo, idioma_alvo, ajustes, itens_permitidos)
        nome_idioma = _NOME_IDIOMA.get(idioma_alvo, idioma_alvo)
        instrucao_tecnologias_da_vaga = _instrucao_de_tecnologias_da_vaga(secao.tipo)
        bloco_tecnologias_da_vaga = f"{instrucao_tecnologias_da_vaga}\n\n" if instrucao_tecnologias_da_vaga else ""
        bloco_conquistas = bloco_conquistas_do_historico(contexto) if secao.tipo == TipoSecao.PERFIL else ""

        requisitos_explicitos = [
            requisito.nome for requisito in analise_vaga.requisitos
            if requisito.tipo == TipoRequisitoTecnico.EXPLICITO
        ]
        requisitos_implicitos = [
            requisito.nome for requisito in analise_vaga.requisitos
            if requisito.tipo == TipoRequisitoTecnico.IMPLICITO
        ]
        ambiguidade = analise_vaga.ambiguidade

        prompt_usuario = (
            f"Seção do currículo: {secao.titulo}\n\n"
            f"{rotulo_texto}:\n{secao.conteudo}\n\n"
            f"{instrucao_refino}"
            f"{linha_cargo_alvo(contexto)}"
            f"{bloco_conquistas}"
            f"Descrição da vaga-alvo:\n{contexto.descricao_vaga}\n\n"
            f"Análise de vaga estruturada:\n"
            f"- Requisitos explícitos: {', '.join(requisitos_explicitos) or 'nenhum'}\n"
            f"- Requisitos implícitos: {', '.join(requisitos_implicitos) or 'nenhum'}\n"
            f"- Trechos ambíguos: {', '.join(ambiguidade) or 'nenhum'}\n\n"
            f"Idioma de saída obrigatório: {nome_idioma}\n\n"
            f"Instrução específica para esta seção: {instrucao_especifica}\n\n"
            f"{bloco_tecnologias_da_vaga}"
            "Não inclua idiomas (ex.: inglês, espanhol, português) como se fossem tecnologias, "
            "mesmo que apareçam nos requisitos explícitos ou implícitos — idiomas pertencem a "
            "outra seção do currículo e devem ser ignorados aqui, independentemente da seção "
            "que está sendo reescrita. Não infira frameworks, ferramentas ou habilidades que não estejam no conteúdo original.\n\n"
            "Preserve a estrutura de linhas do conteúdo original: cada linha que começa com \"- \" no original "
            "continua sendo uma linha que começa com \"- \" na saída, e cada categoria ou item que estava em "
            "sua própria linha continua em sua própria linha. Nunca junte tópicos ou linhas em um parágrafo."
        )

        resposta = self._cliente_openai.solicitar_json(
            prompt_sistema=_PROMPT_SISTEMA,
            prompt_usuario=prompt_usuario,
        )
        conteudo_bruto = resposta.get("conteudo_ajustado")
        # O modelo às vezes devolve um objeto/lista estruturado em vez de texto puro,
        # apesar da instrução no prompt — normaliza pra string em vez de quebrar.
        novo_conteudo = str(conteudo_bruto).strip() if conteudo_bruto else ""
        if not novo_conteudo:
            raise ValueError(f"O modelo não retornou conteúdo ajustado para a seção '{secao.titulo}'.")

        return secao.com_novo_conteudo(novo_conteudo)
