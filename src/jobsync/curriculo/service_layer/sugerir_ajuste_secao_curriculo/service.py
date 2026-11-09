"""Caso de uso: sugerir, via IA, uma nova versão de uma seção de texto do currículo.

Com contexto de vaga (revisão do currículo adaptado), adapta o texto à vaga; sem
contexto (tela Meu perfil), apenas melhora a escrita. Nada é persistido.
"""
from __future__ import annotations

from time import perf_counter

from jobsync.curriculo.domain.ajustador_texto_port import AjustadorTextoPort
from jobsync.curriculo.domain.contexto_vaga import ContextoVaga
from jobsync.curriculo.domain.curriculo import SecaoCurriculo
from jobsync.curriculo.domain.melhorador_texto_curriculo_port import MelhoradorTextoCurriculoPort
from jobsync.curriculo.service_layer.sugerir_ajuste_secao_curriculo.validator import (
    SugerirAjusteSecaoCurriculoInputValidator,
)
from jobsync.curriculo.service_layer.sugestao_ia_indisponivel import SugestaoIAIndisponivel
from jobsync.curriculo.service_layer.validacoes_sugestao import registrar_sugestao


class SugerirAjusteSecaoCurriculo:
    def __init__(
        self,
        ajustador_texto: AjustadorTextoPort,
        melhorador: MelhoradorTextoCurriculoPort,
    ) -> None:
        self._ajustador_texto = ajustador_texto
        self._melhorador = melhorador

    def executar(self, secao: SecaoCurriculo, contexto: ContextoVaga | None) -> SecaoCurriculo:
        SugerirAjusteSecaoCurriculoInputValidator.validar(secao)
        inicio = perf_counter()
        try:
            sugerida = self._sugerir(secao, contexto)
        except (RuntimeError, ValueError) as erro:
            raise SugestaoIAIndisponivel() from erro
        registrar_sugestao(
            "vaga" if contexto else "perfil",
            secao.tipo.name,
            len(secao.conteudo),
            len(sugerida.conteudo),
            inicio,
        )
        return sugerida

    def _sugerir(self, secao: SecaoCurriculo, contexto: ContextoVaga | None) -> SecaoCurriculo:
        if contexto is None:
            return self._melhorador.melhorar_secao(secao)
        return self._ajustador_texto.ajustar_secao(secao=secao, contexto=contexto)
