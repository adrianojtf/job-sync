"""Porta (Port) para o serviço de ajuste de texto de uma seção do currículo via LLM."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.curriculo import SecaoCurriculo
    from domain.vaga import AnaliseVaga


class AjustadorTextoPort(ABC):
    """Reescreve o conteúdo de uma seção do currículo, adaptando-o à vaga e ao idioma alvo."""

    @abstractmethod
    def ajustar_secao(
        self,
        secao: SecaoCurriculo,
        descricao_vaga: str,
        idioma_alvo: str,
        analise_vaga: AnaliseVaga,
    ) -> SecaoCurriculo:
        """Retorna uma nova SecaoCurriculo com o conteúdo reescrito.

            Args:
                secao: seção original extraída do currículo (ex.: TECNOLOGIAS, PERFIL).
                descricao_vaga: texto livre com a descrição da vaga-alvo.
                idioma_alvo: "pt" ou "en".
                analise_vaga: análise estruturada da descrição de vaga para orientar o ajuste.

            Regras de reescrita:
                - Preservar fatos verificáveis: empresas e datas do currículo original
                não podem ser alteradas.
                - Priorizar e reformular a ênfase e o idioma conforme a vaga-alvo.
                - Sempre extrair todas as tecnologias, ferramentas, frameworks e metodologias
                mencionadas em `analise_vaga` como DESCRICAO_VAGA e incluir cada
                uma delas na seção de tecnologias reescrita, mesmo que não constem
                na secao.
                - Objetivo: maximizar a correspondência de palavras-chave com a vaga
                para otimizar a leitura por sistemas ATS (Applicant Tracking System).

            Returns:
                Nova instância de SecaoCurriculo com o conteúdo ajustado.
        """
        raise NotImplementedError
