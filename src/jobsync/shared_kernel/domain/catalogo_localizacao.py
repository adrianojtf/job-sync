"""Catálogo de localização para seções e categorias de tecnologia do currículo.

O contrato desta camada é simples e previsível: mapear chaves semânticas para
rótulos em português e inglês e aplicar fallback consistente para idiomas não
mapeados, preservando rótulos desconhecidos sem alterar o conteúdo factual.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CatalogoLocalizacao:
    """Centraliza os rótulos de apresentação usados no gerador de PDF."""

    secoes: dict[str, dict[str, str]]
    categorias_tecnologia: dict[str, dict[str, str]]

    def __init__(
        self,
        secoes: dict[str, dict[str, str]] | None = None,
        categorias_tecnologia: dict[str, dict[str, str]] | None = None,
    ) -> None:
        self.secoes = secoes or self._secoes_padrao()
        self.categorias_tecnologia = categorias_tecnologia or self._categorias_padrao()

    @staticmethod
    def _secoes_padrao() -> dict[str, dict[str, str]]:
        return {
            "tecnologias": {"pt": "Competências", "en": "Skills"},
            "perfil": {"pt": "Perfil", "en": "Profile"},
            "experiencias": {"pt": "Experiências", "en": "Experience"},
            "formacao": {"pt": "Formação", "en": "Education"},
            "certificacoes": {"pt": "Certificações", "en": "Certifications"},
            "idiomas": {"pt": "Idiomas", "en": "Languages"},
        }

    @staticmethod
    def _categorias_padrao() -> dict[str, dict[str, str]]:
        return {
            "linguagens": {"pt": "Linguagens", "en": "Languages"},
            "frameworks": {"pt": "Frameworks", "en": "Frameworks"},
            "desenvolvimento_web": {"pt": "Desenvolvimento Web", "en": "Web Development"},
            "devops": {"pt": "DevOps", "en": "DevOps"},
            "bancos_de_dados": {"pt": "Bancos de Dados", "en": "Databases"},
            "controle_de_versao": {"pt": "Controle de Versão", "en": "Version Control"},
            "outros": {"pt": "Outros", "en": "Other"},
        }

    def normalizar_idioma(self, idioma: str) -> str:
        idioma_limpo = (idioma or "pt").strip().lower()
        if idioma_limpo.startswith("pt"):
            return "pt"
        if idioma_limpo.startswith("en"):
            return "en"
        return "pt"

    def localizar_secao(self, idioma: str, chave: str, fallback: str | None = None) -> str:
        idioma_normalizado = self.normalizar_idioma(idioma)
        mapeamento = self.secoes.get(chave.lower())
        if mapeamento and idioma_normalizado in mapeamento:
            return mapeamento[idioma_normalizado]
        if fallback is not None:
            return fallback
        if mapeamento and "pt" in mapeamento:
            return mapeamento["pt"]
        return fallback or chave

    def localizar_categoria(self, idioma: str, rotulo: str, fallback: str | None = None) -> str:
        idioma_normalizado = self.normalizar_idioma(idioma)
        chave = self._identificar_chave_categoria(rotulo)
        if chave:
            mapeamento = self.categorias_tecnologia.get(chave)
            if mapeamento and idioma_normalizado in mapeamento:
                return mapeamento[idioma_normalizado]
            if fallback is not None:
                return fallback
            if mapeamento and "pt" in mapeamento:
                return mapeamento["pt"]
        if fallback is not None:
            return fallback
        return rotulo

    def _identificar_chave_categoria(self, rotulo: str) -> str | None:
        rotulo_normalizado = self._normalizar_texto(rotulo)
        for chave, mapeamento in self.categorias_tecnologia.items():
            for valor in mapeamento.values():
                if self._normalizar_texto(valor) == rotulo_normalizado:
                    return chave
        return None

    @staticmethod
    def _normalizar_texto(valor: str) -> str:
        return "".join(ch.lower() for ch in valor if ch.isalnum())
