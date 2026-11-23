"""Porta (Port) para o serviço de ajuste de texto de uma seção do currículo via LLM."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jobsync.curriculo import ContextoVaga, EquivalenciaTecnologia, PedidoRefino, SecaoCurriculo


class AjustadorTextoPort(ABC):
    """Reescreve o conteúdo de uma seção do currículo, adaptando-o à vaga e ao idioma alvo."""

    @abstractmethod
    def ajustar_secao(
        self,
        secao: SecaoCurriculo,
        contexto: ContextoVaga,
        ajustes: Sequence[EquivalenciaTecnologia] = (),
        itens_permitidos: Sequence[str] | None = None,
    ) -> SecaoCurriculo:
        """Retorna uma nova SecaoCurriculo com o conteúdo reescrito.

            Args:
                secao: seção original extraída do currículo (ex.: TECNOLOGIAS, PERFIL).
                contexto: vaga-alvo (descrição, idioma "pt" ou "en", análise estruturada
                e cargo-alvo) que orienta o ajuste.
                ajustes: tecnologias equivalentes trocadas nas experiências (JOB-0037). A seção
                de tecnologias lista a original e a equivalente; o resumo pode citar a equivalente.
                itens_permitidos: só para a seção de tecnologias (JOB-0044). Os únicos itens que
                podem aparecer; a IA agrupa e ordena, sem acrescentar outros. Sem ela, a seção
                usa só o que já está no conteúdo.

            Regras de reescrita:
                - Preservar fatos verificáveis: empresas e datas do currículo original
                não podem ser alteradas.
                - Priorizar e reformular a ênfase e o idioma conforme a vaga-alvo, sem
                copiar trechos da vaga.
                - Tecnologias da vaga só entram na seção de tecnologias se o domínio as
                permitiu (`itens_permitidos`); a vaga não obriga a citar tudo.

            Returns:
                Nova instância de SecaoCurriculo com o conteúdo ajustado.
        """
        raise NotImplementedError

    @abstractmethod
    def refinar_secao(
        self, secao: SecaoCurriculo, contexto: ContextoVaga, refino: PedidoRefino
    ) -> SecaoCurriculo:
        """Refina o texto atual da seção para a vaga, com o foco da tentativa (JOB-0037).

        Parte do texto atual do usuário, e não da geração inicial, e não repete as
        `refino.sugestoes_anteriores`.
        """
        raise NotImplementedError
