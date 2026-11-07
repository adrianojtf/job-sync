"""Testes do adapter MelhoradorTextoCurriculoOpenAIClient."""
from unittest.mock import Mock

import pytest

from jobsync.curriculo import ExperienciaParaAvaliacao, SecaoCurriculo, TipoSecao
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

        sugerida = MelhoradorTextoCurriculoOpenAIClient(cliente).melhorar_secao(secao)

        assert sugerida == SecaoCurriculo(
            TipoSecao.PERFIL, "Perfil", "Engenheira backend com foco em APIs."
        )

    def test_prompt_pede_para_manter_idioma_e_nao_inventar_fatos(self):
        cliente = _cliente({"texto_sugerido": "Texto"})
        secao = SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Trabalho com backend.")

        MelhoradorTextoCurriculoOpenAIClient(cliente).melhorar_secao(secao)

        argumentos = cliente.solicitar_json.call_args.kwargs
        assert "idioma" in argumentos["prompt_sistema"].lower()
        assert "não invente" in argumentos["prompt_sistema"].lower()
        assert "Trabalho com backend." in argumentos["prompt_usuario"]

    def test_melhorar_experiencia_preserva_cargo_empresa_e_periodo(self):
        cliente = _cliente({"texto_sugerido": "Desenvolvi APIs REST em Python."})

        sugerida = MelhoradorTextoCurriculoOpenAIClient(cliente).melhorar_experiencia(
            _experiencia()
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
            MelhoradorTextoCurriculoOpenAIClient(cliente).melhorar_secao(secao)
