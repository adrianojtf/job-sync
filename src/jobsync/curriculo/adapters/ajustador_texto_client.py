"""Adapter (implementa AjustadorTextoPort) que reescreve uma seção do currículo via IA.

Cada seção é processada de forma isolada e independente: o prompt varia
conforme o tipo de seção (Tecnologias, Perfil, Experiências, Formação),
priorizando o conteúdo mais relevante para a vaga-alvo e traduzindo/adaptando
para o idioma solicitado, sem inventar fatos que não constam no original.
"""
from __future__ import annotations

from jobsync.curriculo.domain.ajustador_texto_port import AjustadorTextoPort
from jobsync.curriculo.domain.rotulos_experiencia import ROTULO_CONTEXTO
from jobsync.vaga import AnaliseVaga, TipoRequisitoTecnico
from jobsync.curriculo import SecaoCurriculo, TipoSecao
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI

_NOME_IDIOMA = {"pt": "português do Brasil", "en": "inglês (formato americano de currículo)"}

_INSTRUCOES_POR_TIPO: dict[TipoSecao, str] = {
    TipoSecao.TECNOLOGIAS: (
        "Reordene e destaque as tecnologias mais relevantes para a vaga primeiro, "
        "mantendo TODAS as tecnologias originais (não remova nenhuma). "
        "Se o original tiver categorias no formato 'Rótulo: itens', mantenha uma categoria por linha, "
        "no formato 'Rótulo: item1, item2'; se não tiver, não crie categorias."
    ),
    TipoSecao.PERFIL: (
        "Reescreva o resumo profissional para enfatizar a experiência e competências "
        "mais alinhadas à vaga, mantendo-se fiel aos fatos originais (não invente "
        "anos de experiência, cargos ou tecnologias que não constam no texto original)."
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
        "métricas e volumes plausíveis e conservadores."
    )


_PROMPT_SISTEMA = """\
Você é um especialista em redação de currículos (resume writer) que ajuda \
candidatos a adaptar seu currículo para vagas específicas, SEM jamais \
inventar experiência, empresa ou tecnologia que não exista no texto original. \
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
        descricao_vaga: str,
        idioma_alvo: str,
        analise_vaga: AnaliseVaga,
    ) -> SecaoCurriculo:
        instrucao_especifica = (
            _instrucao_experiencias(ROTULO_CONTEXTO.get(idioma_alvo, ROTULO_CONTEXTO["pt"]))
            if secao.tipo == TipoSecao.EXPERIENCIAS
            else _INSTRUCOES_POR_TIPO.get(
                secao.tipo, "Traduza/adapte o idioma, mantendo os fatos originais."
            )
        )
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
            f"Conteúdo original:\n{secao.conteudo}\n\n"
            f"Descrição da vaga-alvo:\n{descricao_vaga}\n\n"
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
