"""Adapter (implementa AjustadorTextoPort) que reescreve uma seção do currículo via IA.

Cada seção é processada de forma isolada e independente: o prompt varia
conforme o tipo de seção (Tecnologias, Perfil, Experiências, Formação),
priorizando o conteúdo mais relevante para a vaga-alvo e traduzindo/adaptando
para o idioma solicitado, sem inventar fatos que não constam no original.
"""
from __future__ import annotations

from domain.curriculo.ajustador_texto_port import AjustadorTextoPort
from domain.vaga import AnaliseVaga, TipoRequisitoTecnico
from domain.curriculo import SecaoCurriculo, TipoSecao
from infrastructure.llm.cliente_groq import ClienteGroq

_NOME_IDIOMA = {"pt": "português do Brasil", "en": "inglês (formato americano de currículo)"}

_INSTRUCOES_POR_TIPO: dict[TipoSecao, str] = {
    TipoSecao.TECNOLOGIAS: (
        "Reordene e destaque as tecnologias mais relevantes para a vaga primeiro, "
        "mantendo TODAS as tecnologias originais (não remova nenhuma)."
    ),
    TipoSecao.PERFIL: (
        "Reescreva o resumo profissional para enfatizar a experiência e competências "
        "mais alinhadas à vaga, mantendo-se fiel aos fatos originais (não invente "
        "anos de experiência, cargos ou tecnologias que não constam no texto original)."
    ),
    TipoSecao.EXPERIENCIAS: (
        "Ajuste a ênfase de cada experiência para destacar responsabilidades e "
        "resultados mais relevantes à vaga. Preserve empresas, cargos, datas e "
        "métricas/números exatamente como no original — não invente resultados."
    ),
    TipoSecao.FORMACAO: (
        "Apenas traduza/adapte o idioma, se necessário. Não altere instituições, "
        "cursos ou datas."
    ),
    TipoSecao.CERTIFICACOES: "Apenas traduza/adapte o idioma, se necessário, sem alterar os fatos.",
    TipoSecao.IDIOMAS: "Apenas traduza/adapte o idioma, se necessário, sem alterar os fatos.",
}

_PROMPT_SISTEMA = """\
Você é um especialista em redação de currículos (resume writer) que ajuda \
candidatos a adaptar seu currículo para vagas específicas, SEM jamais \
inventar experiência, tecnologia ou resultado que não exista no texto original.

Responda ESTRITAMENTE em JSON no formato:
{"conteudo_ajustado": "texto da seção já reescrita"}
"""


class AjustadorTextoGroq(AjustadorTextoPort):
    """Reescreve o conteúdo de uma seção do currículo usando o modelo Groq."""

    def __init__(self, cliente_groq: ClienteGroq | None = None) -> None:
        self._cliente_groq = cliente_groq or ClienteGroq()

    def ajustar_secao(
        self,
        secao: SecaoCurriculo,
        descricao_vaga: str,
        idioma_alvo: str,
        analise_vaga: AnaliseVaga,
    ) -> SecaoCurriculo:
        instrucao_especifica = _INSTRUCOES_POR_TIPO.get(
            secao.tipo, "Traduza/adapte o idioma, mantendo os fatos originais."
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
            "Use apenas as informações da vaga original e da análise estruturada acima. "
            "Não infira frameworks, ferramentas ou habilidades que não estejam listados "
            "como requisitos explícitos ou implícitos."
        )

        resposta = self._cliente_groq.solicitar_json(
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
