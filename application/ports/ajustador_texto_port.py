"""Porta (Port) para o serviço de ajuste de texto de uma seção do currículo via LLM."""
from abc import ABC, abstractmethod

from domain.analise_vaga import AnaliseVaga
from domain.curriculo import SecaoCurriculo


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

        - secao: seção original extraída do currículo (ex.: TECNOLOGIAS, PERFIL).
        - descricao_vaga: texto livre com a descrição da vaga-alvo.
        - idioma_alvo: "pt" ou "en".
        - analise_vaga: análise estruturada da descrição de vaga para orientar o ajuste.

        A reescrita deve preservar fatos (empresas, datas, tecnologias
        realmente utilizadas) e apenas priorizar/reformular a ênfase e o
        idioma — nunca inventar experiência que não exista no currículo original.
        """
        raise NotImplementedError
