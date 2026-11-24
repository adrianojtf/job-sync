"""Adapter (implementa ExtratorPerfilEstruturadoPort) que extrai o perfil estruturado via IA.

Fluxo: pdfplumber extrai o texto bruto -> o LLM devolve diretamente os campos
estruturados (experiências, formação, certificações, idiomas e tecnologias
como listas de objetos), em vez do texto livre por seção usado por
`ExtratorCurriculoSegmentadoPorIA`. O resultado é sempre um rascunho
revisável pelo usuário, nunca persistido automaticamente.
"""
from __future__ import annotations

from jobsync.shared_kernel.adapters.extrator_texto_pdfplumber_client import ExtratorTextoPdfPlumber
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI
from jobsync.perfil_estruturado.domain.extrator_perfil_estruturado_port import ExtratorPerfilEstruturadoPort
from jobsync.perfil_estruturado.domain.perfil_estruturado import (
    Certificacao,
    DadosPerfilExtraidos,
    ExperienciaProfissional,
    FormacaoAcademica,
    Idioma,
    NivelIdioma,
)

_PROMPT_SISTEMA = """\
Você é um assistente especializado em analisar currículos profissionais.
Sua tarefa é extrair os dados do currículo em formato estruturado,
SEM inventar informações que não estejam no texto original.

Responda ESTRITAMENTE em JSON no seguinte formato:
{
  "nome_completo": "string",
  "email": "string (vazio se não encontrado)",
  "linkedin": "string (vazio se não encontrado)",
  "resumo_profissional": "string (resumo/perfil profissional, vazio se não existir)",
  "experiencias": [
    {"empresa": "string", "cargo": "string", "periodo": "string, ex: 'Jan 2020 - Dez 2022' ou '2023 - Atual'", "descricao": "string, o texto da experiência exatamente como está no currículo"}
  ],
  "formacoes": [
    {"instituicao": "string", "curso": "string", "periodo": "string"}
  ],
  "certificacoes": [
    {"nome": "string", "instituicao": "string", "ano": "string"}
  ],
  "idiomas": [
    {"idioma": "string", "nivel": "um de: BASICO, INTERMEDIARIO, AVANCADO, FLUENTE, NATIVO"}
  ],
  "tecnologias": ["string", "string"]
}

Regras:
- Preserve o texto original o máximo possível (não parafraseie).
- Na descrição de cada experiência, copie o texto exatamente como está no currículo, em linhas separadas, mantendo os
  rótulos originais dos blocos (ex.: "Context:", "Key Responsibilities:", "Key Achievements:", "Technologies:",
  "Contexto:", "Principais realizações:", "Tecnologias:") e os marcadores das listas.
- Se uma lista não existir no currículo, retorne lista vazia para ela.
- Não invente informações que não estão no texto original.
"""


class ExtratorPerfilEstruturadoClient(ExtratorPerfilEstruturadoPort):
    """Extrai texto do PDF e usa IA para produzir os campos estruturados do perfil."""

    def __init__(
        self,
        extrator_texto: ExtratorTextoPdfPlumber | None = None,
        cliente_openai: ClienteOpenAI | None = None,
    ) -> None:
        self._extrator_texto = extrator_texto or ExtratorTextoPdfPlumber()
        self._cliente_openai = cliente_openai or ClienteOpenAI()

    def extrair(self, pdf_bytes: bytes) -> DadosPerfilExtraidos:
        texto_bruto = self._extrator_texto.extrair_texto(pdf_bytes)
        dados = self._cliente_openai.solicitar_json(
            prompt_sistema=_PROMPT_SISTEMA,
            prompt_usuario=f"Texto do currículo a extrair:\n\n{texto_bruto}",
        )
        return self._montar_dados_perfil(dados)

    @staticmethod
    def _texto_seguro(valor: object) -> str:
        return str(valor).strip() if valor else ""

    @staticmethod
    def _parsear_nivel(valor: object) -> NivelIdioma:
        texto = str(valor).strip().upper() if valor else ""
        try:
            return NivelIdioma[texto]
        except KeyError:
            return NivelIdioma.INTERMEDIARIO

    def _montar_dados_perfil(self, dados: dict) -> DadosPerfilExtraidos:
        experiencias: list[ExperienciaProfissional] = []
        for item in dados.get("experiencias") or []:
            if not isinstance(item, dict):
                continue
            empresa = self._texto_seguro(item.get("empresa"))
            cargo = self._texto_seguro(item.get("cargo"))
            if not empresa or not cargo:
                continue
            experiencias.append(
                ExperienciaProfissional(
                    empresa=empresa,
                    cargo=cargo,
                    periodo=self._texto_seguro(item.get("periodo")),
                    descricao=self._texto_seguro(item.get("descricao")),
                )
            )

        formacoes: list[FormacaoAcademica] = []
        for item in dados.get("formacoes") or []:
            if not isinstance(item, dict):
                continue
            instituicao = self._texto_seguro(item.get("instituicao"))
            curso = self._texto_seguro(item.get("curso"))
            if not instituicao or not curso:
                continue
            formacoes.append(
                FormacaoAcademica(
                    instituicao=instituicao, curso=curso, periodo=self._texto_seguro(item.get("periodo"))
                )
            )

        certificacoes: list[Certificacao] = []
        for item in dados.get("certificacoes") or []:
            if not isinstance(item, dict):
                continue
            nome = self._texto_seguro(item.get("nome"))
            if not nome:
                continue
            certificacoes.append(
                Certificacao(
                    nome=nome,
                    instituicao=self._texto_seguro(item.get("instituicao")),
                    ano=self._texto_seguro(item.get("ano")),
                )
            )

        idiomas: list[Idioma] = []
        for item in dados.get("idiomas") or []:
            if not isinstance(item, dict):
                continue
            nome_idioma = self._texto_seguro(item.get("idioma"))
            if not nome_idioma:
                continue
            idiomas.append(Idioma(idioma=nome_idioma, nivel=self._parsear_nivel(item.get("nivel"))))

        tecnologias_brutas = dados.get("tecnologias") or []
        tecnologias = tuple(
            self._texto_seguro(tecnologia) for tecnologia in tecnologias_brutas if self._texto_seguro(tecnologia)
        )

        return DadosPerfilExtraidos(
            nome_completo=self._texto_seguro(dados.get("nome_completo")),
            email=self._texto_seguro(dados.get("email")),
            linkedin=self._texto_seguro(dados.get("linkedin")),
            resumo_profissional=self._texto_seguro(dados.get("resumo_profissional")),
            experiencias=tuple(experiencias),
            formacoes=tuple(formacoes),
            certificacoes=tuple(certificacoes),
            idiomas=tuple(idiomas),
            tecnologias=tecnologias,
        )
