"""Testes do adapter MelhoradorTextoCurriculoOpenAIClient."""
from unittest.mock import Mock

import pytest

from jobsync.curriculo import ExperienciaParaAvaliacao, PedidoRefino, SecaoCurriculo, TipoSecao
from jobsync.curriculo.adapters.melhorador_texto_curriculo_openai_client import (
    MelhoradorTextoCurriculoOpenAIClient,
)
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI


def _cliente(resposta: dict) -> Mock:
    cliente = Mock(spec=ClienteOpenAI)
    cliente.solicitar_json.return_value = resposta
    return cliente


def _experiencia() -> ExperienciaParaAvaliacao:
    return ExperienciaParaAvaliacao(
        cargo="Dev", empresa="TechCorp", periodo="2022 - Atual", descricao="Fiz APIs."
    )


class TestMelhoradorTextoCurriculoOpenAIClient:
    def test_melhorar_secao_devolve_secao_com_texto_sugerido(self):
        cliente = _cliente({"texto_sugerido": "  Engenheira backend com foco em APIs.  "})
        secao = SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Trabalho com backend.")

        sugerida = MelhoradorTextoCurriculoOpenAIClient(cliente).melhorar_secao(secao, PedidoRefino())

        assert sugerida == SecaoCurriculo(
            TipoSecao.PERFIL, "Perfil", "Engenheira backend com foco em APIs."
        )

    def test_prompt_pede_para_manter_idioma_e_nao_inventar_fatos(self):
        cliente = _cliente({"texto_sugerido": "Texto"})
        secao = SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Trabalho com backend.")

        MelhoradorTextoCurriculoOpenAIClient(cliente).melhorar_secao(secao, PedidoRefino())

        argumentos = cliente.solicitar_json.call_args.kwargs
        assert "idioma" in argumentos["prompt_sistema"].lower()
        assert "não invente" in argumentos["prompt_sistema"].lower()
        assert "Trabalho com backend." in argumentos["prompt_usuario"]

    def test_melhorar_experiencia_preserva_cargo_empresa_e_periodo(self):
        cliente = _cliente({"texto_sugerido": "Desenvolvi APIs REST em Python."})

        sugerida = MelhoradorTextoCurriculoOpenAIClient(cliente).melhorar_experiencia(
            _experiencia(), PedidoRefino()
        )

        assert sugerida == ExperienciaParaAvaliacao(
            cargo="Dev",
            empresa="TechCorp",
            periodo="2022 - Atual",
            descricao="Desenvolvi APIs REST em Python.",
        )

    @pytest.mark.parametrize("resposta", [{}, {"texto_sugerido": "  "}, {"texto_sugerido": 3}])
    def test_resposta_sem_texto_utilizavel_gera_erro(self, resposta):
        cliente = _cliente(resposta)
        secao = SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Trabalho com backend.")

        with pytest.raises(ValueError, match="texto sugerido"):
            MelhoradorTextoCurriculoOpenAIClient(cliente).melhorar_secao(secao, PedidoRefino())


class TestMelhoradorTextoCurriculoOpenAIClientRefino:
    def test_secao_usa_o_foco_sem_vaga_da_tentativa_e_as_sugestoes_anteriores(self):
        cliente = _cliente({"texto_sugerido": "Texto"})
        secao = SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Trabalho com backend.")
        refino = PedidoRefino(tentativa=2, sugestoes_anteriores=("Versão anterior.",))

        MelhoradorTextoCurriculoOpenAIClient(cliente).melhorar_secao(secao, refino)

        usuario = cliente.solicitar_json.call_args.kwargs["prompt_usuario"]
        assert "Parta do texto atual" in usuario
        assert "Foco desta versão: clareza e concisão" in usuario
        assert "Não repita estas versões já sugeridas" in usuario
        assert "Versão anterior." in usuario

    def test_experiencia_usa_o_foco_sem_vaga_da_tentativa(self):
        cliente = _cliente({"texto_sugerido": "Texto"})

        MelhoradorTextoCurriculoOpenAIClient(cliente).melhorar_experiencia(
            _experiencia(), PedidoRefino(tentativa=3)
        )

        usuario = cliente.solicitar_json.call_args.kwargs["prompt_usuario"]
        assert "Foco desta versão: ênfase técnica" in usuario
        assert "Não repita" not in usuario
