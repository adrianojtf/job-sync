"""Testes do caso de uso SugerirAjusteSecaoCurriculo."""
from unittest.mock import Mock

import pytest

from jobsync.curriculo import (
    AjustadorTextoPort,
    ContextoVaga,
    FocoRefino,
    MelhoradorTextoCurriculoPort,
    PedidoRefino,
    SecaoCurriculo,
    TipoSecao,
)
from jobsync.curriculo.service_layer.sugerir_ajuste_secao_curriculo import (
    SugerirAjusteSecaoCurriculo,
)
from jobsync.curriculo.service_layer.sugestao_ia_indisponivel import SugestaoIAIndisponivel
from jobsync.vaga import AnaliseVaga


def _contexto() -> ContextoVaga:
    return ContextoVaga(
        descricao_vaga="Vaga Python",
        idioma_alvo="en",
        analise_vaga=AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="Vaga Python"),
    )


def _secao(tipo: TipoSecao = TipoSecao.PERFIL, conteudo: str = "Texto atual editado.") -> SecaoCurriculo:
    return SecaoCurriculo(tipo, "Perfil", conteudo)


def _caso_de_uso() -> tuple[SugerirAjusteSecaoCurriculo, Mock, Mock]:
    ajustador = Mock(spec=AjustadorTextoPort)
    melhorador = Mock(spec=MelhoradorTextoCurriculoPort)
    return SugerirAjusteSecaoCurriculo(ajustador, melhorador), ajustador, melhorador


class TestSugerirAjusteSecaoCurriculo:
    def test_com_contexto_ajusta_o_texto_recebido_para_a_vaga(self):
        caso_de_uso, ajustador, melhorador = _caso_de_uso()
        contexto = _contexto()
        sugerida = _secao(conteudo="Sugestão da IA.")
        ajustador.refinar_secao.return_value = sugerida

        resultado = caso_de_uso.executar(_secao(), contexto)

        ajustador.refinar_secao.assert_called_once_with(
            secao=_secao(), contexto=contexto, refino=PedidoRefino()
        )
        ajustador.ajustar_secao.assert_not_called()
        melhorador.melhorar_secao.assert_not_called()
        assert resultado.valor == sugerida
        assert resultado.foco == FocoRefino.ADERENCIA_VAGA

    def test_sem_contexto_melhora_a_escrita_sem_vaga(self):
        caso_de_uso, ajustador, melhorador = _caso_de_uso()
        sugerida = _secao(conteudo="Sugestão sem vaga.")
        melhorador.melhorar_secao.return_value = sugerida

        resultado = caso_de_uso.executar(_secao(), None)

        melhorador.melhorar_secao.assert_called_once_with(_secao(), PedidoRefino())
        ajustador.refinar_secao.assert_not_called()
        assert resultado.valor == sugerida
        assert resultado.foco == FocoRefino.IMPACTO

    @pytest.mark.parametrize(
        "tipo", [TipoSecao.PERFIL, TipoSecao.TECNOLOGIAS, TipoSecao.EXPERIENCIAS]
    )
    def test_aceita_perfil_tecnologias_e_experiencias(self, tipo):
        caso_de_uso, _, melhorador = _caso_de_uso()
        melhorador.melhorar_secao.return_value = _secao(tipo)

        resultado = caso_de_uso.executar(_secao(tipo), None)

        assert resultado.valor.tipo == tipo

    @pytest.mark.parametrize(
        "tipo", [TipoSecao.FORMACAO, TipoSecao.CERTIFICACOES, TipoSecao.IDIOMAS]
    )
    def test_outras_secoes_nao_geram_sugestao(self, tipo):
        caso_de_uso, ajustador, melhorador = _caso_de_uso()

        with pytest.raises(ValueError, match="sugestão"):
            caso_de_uso.executar(_secao(tipo), None)

        ajustador.refinar_secao.assert_not_called()
        melhorador.melhorar_secao.assert_not_called()

    def test_texto_acima_do_limite_nao_chama_a_ia(self):
        caso_de_uso, ajustador, melhorador = _caso_de_uso()

        with pytest.raises(ValueError, match="5000"):
            caso_de_uso.executar(_secao(conteudo="a" * 5001), _contexto())

        ajustador.refinar_secao.assert_not_called()
        melhorador.melhorar_secao.assert_not_called()

    @pytest.mark.parametrize("erro", [RuntimeError("falha"), ValueError("resposta inválida")])
    def test_falha_do_provedor_vira_sugestao_indisponivel(self, erro):
        caso_de_uso, ajustador, _ = _caso_de_uso()
        ajustador.refinar_secao.side_effect = erro

        with pytest.raises(SugestaoIAIndisponivel):
            caso_de_uso.executar(_secao(), _contexto())


class TestSugerirAjusteSecaoCurriculoRefino:
    def test_repassa_o_refino_e_devolve_o_foco_da_tentativa(self):
        caso_de_uso, ajustador, _ = _caso_de_uso()
        contexto = _contexto()
        refino = PedidoRefino(tentativa=2, sugestoes_anteriores=("Versão 1.",))
        ajustador.refinar_secao.return_value = _secao(conteudo="Versão 2.")

        resultado = caso_de_uso.executar(_secao(), contexto, refino)

        ajustador.refinar_secao.assert_called_once_with(secao=_secao(), contexto=contexto, refino=refino)
        assert resultado.foco == FocoRefino.IMPACTO

    def test_sem_vaga_usa_o_rodizio_sem_vaga(self):
        caso_de_uso, _, melhorador = _caso_de_uso()
        melhorador.melhorar_secao.return_value = _secao()

        resultado = caso_de_uso.executar(_secao(), None, PedidoRefino(tentativa=3))

        assert resultado.foco == FocoRefino.ENFASE_TECNICA

    def test_sugestao_anterior_acima_do_limite_nao_chama_a_ia(self):
        caso_de_uso, ajustador, _ = _caso_de_uso()

        with pytest.raises(ValueError, match="5000"):
            caso_de_uso.executar(
                _secao(), _contexto(), PedidoRefino(tentativa=2, sugestoes_anteriores=("a" * 5001,))
            )

        ajustador.refinar_secao.assert_not_called()
