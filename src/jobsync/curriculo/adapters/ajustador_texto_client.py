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
        "Reordene e destaque as tecnologias mais relevantes para a vaga primeiro, "
        "mantendo TODAS as tecnologias originais (não remova nenhuma)."
    ),
    TipoSecao.PERFIL: (
        "Reescreva o resumo profissional para enfatizar a experiência e competências "
        "mais alinhadas à vaga, mantendo-se fiel aos fatos originais (não invente "
        "anos de experiência ou cargos que não constam no texto original)."
    ),
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


def _instrucao_da_secao(
    tipo: TipoSecao, idioma_alvo: str, ajustes: Sequence[EquivalenciaTecnologia]
) -> str:
    """Instrução específica do tipo de seção, com as trocas de tecnologia quando houver."""
    if tipo == TipoSecao.EXPERIENCIAS:
        return _instrucao_experiencias(ROTULO_CONTEXTO.get(idioma_alvo, ROTULO_CONTEXTO["pt"]))
    instrucao = _INSTRUCOES_POR_TIPO.get(tipo, "Traduza/adapte o idioma, mantendo os fatos originais.")
    if tipo == TipoSecao.TECNOLOGIAS:
        complementos = [f"Liste também {ajuste.alvo} ao lado de {ajuste.original}." for ajuste in ajustes]
    elif tipo == TipoSecao.PERFIL:
        complementos = [
            f"Pode citar {ajuste.alvo}, equivalente a {ajuste.original}, já usada pelo candidato."
            for ajuste in ajustes
        ]
    else:
        complementos = []
    return " ".join([instrucao, *complementos])


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
    ) -> SecaoCurriculo:
        return self._solicitar(secao, contexto, ajustes, rotulo_texto="Conteúdo original")

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
    ) -> SecaoCurriculo:
        idioma_alvo = contexto.idioma_alvo
        analise_vaga = contexto.analise_vaga
        instrucao_especifica = _instrucao_da_secao(secao.tipo, idioma_alvo, ajustes)
        nome_idioma = _NOME_IDIOMA.get(idioma_alvo, idioma_alvo)

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
            f"Descrição da vaga-alvo:\n{contexto.descricao_vaga}\n\n"
            f"Análise de vaga estruturada:\n"
            f"- Requisitos explícitos: {', '.join(requisitos_explicitos) or 'nenhum'}\n"
            f"- Requisitos implícitos: {', '.join(requisitos_implicitos) or 'nenhum'}\n"
            f"- Trechos ambíguos: {', '.join(ambiguidade) or 'nenhum'}\n\n"
            f"Idioma de saída obrigatório: {nome_idioma}\n\n"
            f"Instrução específica para esta seção: {instrucao_especifica}\n\n"
            "Inclua explicitamente na seção reescrita todas as tecnologias listadas acima "
            "em requisitos explícitos e implícitos, mesmo que não estejam no conteúdo original. "
            "Cada tecnologia da análise de vaga deve aparecer no texto final.\n\n"
            "Não inclua idiomas (ex.: inglês, espanhol, português) como se fossem tecnologias, "
            "mesmo que apareçam nos requisitos explícitos ou implícitos — idiomas pertencem a "
            "outra seção do currículo e devem ser ignorados aqui, independentemente da seção "
            "que está sendo reescrita. Não infira frameworks, ferramentas ou habilidades que não estejam no conteúdo original."
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
