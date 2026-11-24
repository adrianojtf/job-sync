from unittest.mock import Mock

import pytest

from jobsync.perfil_estruturado.adapters.completador_blocos_experiencia_openai_client import (
    CompletadorBlocosExperienciaOpenAIClient,
)
from jobsync.perfil_estruturado.domain.blocos_experiencia import BlocosExperiencia, ExperienciaParaCompletar
from jobsync.perfil_estruturado.domain.exceptions import CompletarBlocosIndisponivel
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI

RESPOSTA = {
    "contexto": "Na Starian, atuei em um ERP financeiro para a construção civil.",
    "responsabilidades": ["Projetar telas", "Testar entregas", "Revisar código"],
    "realizacoes": ["Atendi mais de 1.000 usuários", "Reduzi o tempo de fechamento em 30%", "Entreguei o módulo"],
    "skills": ["Java", "SQL"],
}


def _cliente(resposta) -> Mock:
    cliente = Mock(spec=ClienteOpenAI)
    cliente.solicitar_json.return_value = resposta
    return cliente


def _pedido(reconhecidos: BlocosExperiencia = BlocosExperiencia(), resto: str = "Atuei com ERP.") -> ExperienciaParaCompletar:
    return ExperienciaParaCompletar(
        cargo="Dev", empresa="Starian", periodo="2024 - Atual", resto=resto, reconhecidos=reconhecidos
    )


class TestCompletadorBlocosExperienciaOpenAIClient:
    def test_devolve_os_quatro_blocos_quando_todos_faltam(self):
        completador = CompletadorBlocosExperienciaOpenAIClient(_cliente(RESPOSTA))

        blocos = completador.completar(_pedido(), "pt")

        assert blocos == BlocosExperiencia(
            contexto=RESPOSTA["contexto"],
            responsabilidades=tuple(RESPOSTA["responsabilidades"]),
            realizacoes=tuple(RESPOSTA["realizacoes"]),
            skills=("Java", "SQL"),
        )

    def test_o_prompt_pede_so_os_blocos_ausentes_e_traz_os_reconhecidos(self):
        cliente = _cliente({"contexto": "Contexto gerado."})
        reconhecidos = BlocosExperiencia(
            responsabilidades=("Projetar telas",), realizacoes=("Atendi 1.000 usuários",), skills=("Java",)
        )

        blocos = CompletadorBlocosExperienciaOpenAIClient(cliente).completar(_pedido(reconhecidos), "en")

        prompt = cliente.solicitar_json.call_args.kwargs["prompt_usuario"]
        assert "Blocos a gerar: contexto" in prompt
        assert "Projetar telas" in prompt
        assert "inglês" in prompt
        assert blocos == BlocosExperiencia(contexto="Contexto gerado.")

    def test_sem_idioma_o_prompt_pede_o_mesmo_idioma_do_texto(self):
        cliente = _cliente(RESPOSTA)

        CompletadorBlocosExperienciaOpenAIClient(cliente).completar(_pedido())

        assert "mesmo idioma do texto" in cliente.solicitar_json.call_args.kwargs["prompt_usuario"]

    def test_o_prompt_de_sistema_traz_as_regras_de_conteudo(self):
        cliente = _cliente(RESPOSTA)

        CompletadorBlocosExperienciaOpenAIClient(cliente).completar(_pedido())

        sistema = cliente.solicitar_json.call_args.kwargs["prompt_sistema"]
        assert "de 3 a 5" in sistema
        assert "de 1 a 3 frases" in sistema
        assert "plausíveis" in sistema
        assert "Não altere" in sistema

    def test_listas_com_mais_de_cinco_itens_sao_cortadas_em_cinco(self):
        resposta = {**RESPOSTA, "responsabilidades": [f"Item {n}" for n in range(8)]}

        blocos = CompletadorBlocosExperienciaOpenAIClient(_cliente(resposta)).completar(_pedido())

        assert blocos.responsabilidades == tuple(f"Item {n}" for n in range(5))

    @pytest.mark.parametrize(
        "resposta",
        [
            {**RESPOSTA, "contexto": 10},
            {**RESPOSTA, "responsabilidades": "texto solto"},
            {**RESPOSTA, "realizacoes": []},
            {**RESPOSTA, "skills": ["Java", ""]},
            {"contexto": "Só isto."},
            ["não é um objeto"],
        ],
    )
    def test_resposta_fora_do_formato_e_rejeitada(self, resposta):
        completador = CompletadorBlocosExperienciaOpenAIClient(_cliente(resposta))

        with pytest.raises(CompletarBlocosIndisponivel):
            completador.completar(_pedido(), "pt")

    def test_falha_da_api_vira_indisponivel(self):
        cliente = Mock(spec=ClienteOpenAI)
        cliente.solicitar_json.side_effect = RuntimeError("falha")

        with pytest.raises(CompletarBlocosIndisponivel):
            CompletadorBlocosExperienciaOpenAIClient(cliente).completar(_pedido(), "pt")
