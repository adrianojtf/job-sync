"""Testes do adapter IdentificadorEquivalenciasOpenAIClient."""
from unittest.mock import Mock

import pytest

from jobsync.curriculo import ContextoVaga, EquivalenciaTecnologia, ExperienciaParaAvaliacao
from jobsync.curriculo.adapters.identificador_equivalencias_openai_client import (
    IdentificadorEquivalenciasOpenAIClient,
)
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI
from jobsync.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)

RESPOSTA = {"equivalencias": [{"original": "React", "alvo": "Angular"}]}


def _requisito(nome: str, tipo: TipoRequisitoTecnico) -> RequisitoTecnico:
    return RequisitoTecnico(
        nome=nome,
        categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
        tipo=tipo,
        origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
    )


def _contexto(requisitos: tuple[RequisitoTecnico, ...] | None = None) -> ContextoVaga:
    if requisitos is None:
        requisitos = (
            _requisito("Angular", TipoRequisitoTecnico.EXPLICITO),
            _requisito("RxJS", TipoRequisitoTecnico.IMPLICITO),
        )
    return ContextoVaga(
        descricao_vaga="Vaga Java e Angular",
        idioma_alvo="pt",
        analise_vaga=AnaliseVaga(requisitos=requisitos, ambiguidade=(), texto_original="Vaga Java e Angular"),
        cargo_alvo="Desenvolvedor Full Stack",
    )


def _experiencias() -> tuple[ExperienciaParaAvaliacao, ...]:
    return (
        ExperienciaParaAvaliacao(
            descricao="Front-end em React e APIs em Java.", cargo="Dev Full Stack", empresa="Empresa X"
        ),
        ExperienciaParaAvaliacao(descricao="  ", cargo="Estagiário", empresa="Empresa Y"),
    )


def _cliente(resposta: dict) -> Mock:
    cliente = Mock(spec=ClienteOpenAI)
    cliente.solicitar_json.return_value = resposta
    return cliente


def _identificar(cliente: Mock, contexto: ContextoVaga | None = None, experiencias=None):
    return IdentificadorEquivalenciasOpenAIClient(cliente).identificar(
        experiencias=_experiencias() if experiencias is None else experiencias,
        contexto=contexto or _contexto(),
    )


class TestIdentificadorEquivalenciasOpenAIClient:
    def test_devolve_as_equivalencias_do_modelo(self):
        resultado = _identificar(_cliente(RESPOSTA))

        assert resultado == (EquivalenciaTecnologia(original="React", alvo="Angular"),)

    def test_lista_vazia_e_valida(self):
        resultado = _identificar(_cliente({"equivalencias": []}))

        assert resultado == ()

    def test_prompt_de_sistema_define_as_regras_e_o_formato(self):
        cliente = _cliente(RESPOSTA)

        _identificar(cliente)

        sistema = cliente.solicitar_json.call_args.kwargs["prompt_sistema"]
        assert "mesma categoria" in sistema
        assert "aparece nas experiências" in sistema
        assert "pedida pela vaga" in sistema
        assert "idiomas" in sistema
        assert '"equivalencias"' in sistema

    def test_prompt_do_usuario_traz_as_experiencias_com_descricao_e_os_requisitos(self):
        cliente = _cliente(RESPOSTA)

        _identificar(cliente)

        usuario = cliente.solicitar_json.call_args.kwargs["prompt_usuario"]
        assert "Front-end em React e APIs em Java." in usuario
        assert "Estagiário" not in usuario
        assert "Requisitos explícitos da vaga: Angular" in usuario
        assert "Requisitos implícitos da vaga: RxJS" in usuario
        assert "Cargo-alvo (título da vaga): Desenvolvedor Full Stack" in usuario

    def test_sem_requisitos_na_vaga_nao_chama_o_modelo(self):
        cliente = _cliente(RESPOSTA)

        resultado = _identificar(cliente, contexto=_contexto(requisitos=()))

        assert resultado == ()
        cliente.solicitar_json.assert_not_called()

    def test_sem_experiencias_com_descricao_nao_chama_o_modelo(self):
        cliente = _cliente(RESPOSTA)

        resultado = _identificar(cliente, experiencias=(ExperienciaParaAvaliacao(descricao=" "),))

        assert resultado == ()
        cliente.solicitar_json.assert_not_called()

    @pytest.mark.parametrize(
        "resposta",
        [
            {},
            {"equivalencias": "React -> Angular"},
            {"equivalencias": ["React"]},
            {"equivalencias": [{"original": "React"}]},
            {"equivalencias": [{"original": "React", "alvo": 1}]},
            {"equivalencias": [{"original": "React", "alvo": " "}]},
        ],
    )
    def test_formato_invalido_gera_erro(self, resposta):
        with pytest.raises(ValueError):
            _identificar(_cliente(resposta))
