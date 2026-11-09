"""Adapter (implementa ExtratorCurriculoPort) que segmenta o currículo em seções via IA.

Fluxo: pdfplumber extrai o texto bruto -> o LLM identifica e separa o texto em
seções do domínio (Tecnologias, Perfil, Experiências, Formação, etc.), cada
uma podendo ser ajustada de forma independente pelo AjustadorTextoPort.
"""
from __future__ import annotations

from jobsync.curriculo.domain.extrator_curriculo_port import ExtratorCurriculoPort
from jobsync.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from jobsync.shared_kernel.adapters.extrator_texto_pdfplumber_client import ExtratorTextoPdfPlumber
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI

_MAPA_CHAVE_PARA_TIPO_SECAO: dict[str, TipoSecao] = {
    "tecnologias": TipoSecao.TECNOLOGIAS,
    "perfil": TipoSecao.PERFIL,
    "experiencias": TipoSecao.EXPERIENCIAS,
    "formacao": TipoSecao.FORMACAO,
    "certificacoes": TipoSecao.CERTIFICACOES,
    "idiomas": TipoSecao.IDIOMAS,
}

_TITULOS_PADRAO: dict[TipoSecao, str] = {
    TipoSecao.TECNOLOGIAS: "Tecnologias",
    TipoSecao.PERFIL: "Perfil",
    TipoSecao.EXPERIENCIAS: "Experiências",
    TipoSecao.FORMACAO: "Formação acadêmica",
    TipoSecao.CERTIFICACOES: "Certificações",
    TipoSecao.IDIOMAS: "Idiomas",
}

_PROMPT_SISTEMA = """\
Você é um assistente especializado em analisar currículos profissionais.
Sua tarefa é segmentar o texto de um currículo em seções estruturadas,
SEM alterar, resumir ou traduzir o conteúdo original — apenas organizá-lo.

Responda ESTRITAMENTE em JSON no seguinte formato:
{
  "nome_completo": "string",
  "email": "string (vazio se não encontrado)",
  "linkedin": "string (vazio se não encontrado)",
  "secoes": {
    "tecnologias": "texto completo da seção de tecnologias/skills, ou vazio se não existir",
    "perfil": "texto completo do resumo/perfil profissional, ou vazio se não existir",
    "experiencias": "texto completo de todas as experiências profissionais, ou vazio se não existir",
    "formacao": "texto completo da formação acadêmica, ou vazio se não existir",
    "certificacoes": "texto completo de certificações, ou vazio se não existir",
    "idiomas": "texto completo de idiomas, ou vazio se não existir"
  }
}

Regras:
- Preserve o texto original de cada seção o máximo possível (não parafraseie).
- Preserve as quebras de linha originais de cada seção (use \\n no texto JSON).
- Converta marcadores de tópico no início da linha ('●', '•' ou '*') em '- ', sem alterar o texto do tópico.
- Se uma seção não existir no currículo, retorne string vazia para ela.
- Não invente informações que não estão no texto original.
"""


class ExtratorCurriculoClient(ExtratorCurriculoPort):
    """Extrai texto do PDF e usa IA para segmentar em seções do domínio."""

    def __init__(
        self,
        extrator_texto: ExtratorTextoPdfPlumber | None = None,
        cliente_openai: ClienteOpenAI | None = None,
    ) -> None:
        self._extrator_texto = extrator_texto or ExtratorTextoPdfPlumber()
        self._cliente_openai = cliente_openai or ClienteOpenAI()

    def extrair(self, conteudo_pdf: bytes) -> Curriculo:
        texto_bruto = self._extrator_texto.extrair_texto(conteudo_pdf)
        dados_segmentados = self._cliente_openai.solicitar_json(
            prompt_sistema=_PROMPT_SISTEMA,
            prompt_usuario=f"Texto do currículo a segmentar:\n\n{texto_bruto}",
        )
        return self._montar_curriculo(dados_segmentados)

    def _montar_curriculo(self, dados: dict) -> Curriculo:
        nome_completo = (dados.get("nome_completo") or "").strip()
        if not nome_completo:
            raise ValueError("Não foi possível identificar o nome do candidato no currículo enviado.")

        secoes_brutas: dict = dados.get("secoes") or {}
        secoes: list[SecaoCurriculo] = []
        for chave, tipo in _MAPA_CHAVE_PARA_TIPO_SECAO.items():
            conteudo = (secoes_brutas.get(chave) or "").strip()
            if conteudo:
                secoes.append(SecaoCurriculo(tipo=tipo, titulo=_TITULOS_PADRAO[tipo], conteudo=conteudo))

        if not secoes:
            raise ValueError("Não foi possível identificar nenhuma seção reconhecível no currículo enviado.")

        return Curriculo(
            nome_completo=nome_completo,
            email=(dados.get("email") or "").strip(),
            linkedin=(dados.get("linkedin") or "").strip(),
            secoes=tuple(secoes),
        )
