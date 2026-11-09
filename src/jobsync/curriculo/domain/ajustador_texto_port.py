"""Porta (Port) para o serviço de ajuste de texto de uma seção do currículo via LLM."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jobsync.curriculo import ContextoVaga, EquivalenciaTecnologia, SecaoCurriculo


class AjustadorTextoPort(ABC):
    """Reescreve o conteúdo de uma seção do currículo, adaptando-o à vaga e ao idioma alvo."""

    @abstractmethod
    def ajustar_secao(
        self,
        secao: SecaoCurriculo,
        contexto: ContextoVaga,
        ajustes: Sequence[EquivalenciaTecnologia] = (),
    ) -> SecaoCurriculo:
        """Retorna uma nova SecaoCurriculo com o conteúdo reescrito.

            Args:
                secao: seção original extraída do currículo (ex.: TECNOLOGIAS, PERFIL).
                contexto: vaga-alvo (descrição, idioma "pt" ou "en", análise estruturada
                e cargo-alvo) que orienta o ajuste.
                ajustes: tecnologias equivalentes trocadas nas experiências (JOB-0037). A seção
                de tecnologias lista a original e a equivalente; o resumo pode citar a equivalente.

            Regras de reescrita:
                - Preservar fatos verificáveis: empresas e datas do currículo original
                não podem ser alteradas.
                - Priorizar e reformular a ênfase e o idioma conforme a vaga-alvo.
                - Sempre extrair todas as tecnologias, ferramentas, frameworks e metodologias
                mencionadas em `contexto.analise_vaga` como DESCRICAO_VAGA e incluir cada
                uma delas na seção de tecnologias reescrita, mesmo que não constem
                na secao.
                - Objetivo: maximizar a correspondência de palavras-chave com a vaga
                para otimizar a leitura por sistemas ATS (Applicant Tracking System).

            Returns:
                Nova instância de SecaoCurriculo com o conteúdo ajustado.
        """
        raise NotImplementedError
