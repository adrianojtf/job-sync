"""Testes do adapter ExtratorCurriculoClient (sem rede e sem LLM)."""
from jobsync.curriculo import TipoSecao
from jobsync.curriculo.adapters.extrator_curriculo_client import ExtratorCurriculoClient


class ExtratorTextoFake:
    def extrair_texto(self, conteudo_pdf: bytes) -> str:
        return "Ana Silva\n● Criei APIs\n• Reduzi custos"


class ClienteOpenAIFake:
    def __init__(self, resposta: dict) -> None:
        self.resposta = resposta
        self.prompt_sistema: str | None = None
        self.prompt_usuario: str | None = None

    def solicitar_json(self, prompt_sistema: str, prompt_usuario: str) -> dict:
        self.prompt_sistema = prompt_sistema
        self.prompt_usuario = prompt_usuario
        return self.resposta


def _extrair(resposta: dict) -> tuple[ClienteOpenAIFake, object]:
    cliente = ClienteOpenAIFake(resposta)
    extrator = ExtratorCurriculoClient(extrator_texto=ExtratorTextoFake(), cliente_openai=cliente)

    curriculo = extrator.extrair(b"%PDF-conteudo")

    return cliente, curriculo


def test_prompt_pede_para_preservar_quebras_de_linha_das_secoes() -> None:
    cliente, _ = _extrair({"nome_completo": "Ana Silva", "secoes": {"perfil": "Texto"}})

    assert cliente.prompt_sistema is not None
    assert "Preserve as quebras de linha originais de cada seção" in cliente.prompt_sistema


def test_prompt_pede_para_converter_marcadores_de_topico_em_hifen() -> None:
    cliente, _ = _extrair({"nome_completo": "Ana Silva", "secoes": {"perfil": "Texto"}})

    assert cliente.prompt_sistema is not None
    assert "'●'" in cliente.prompt_sistema
    assert "'•'" in cliente.prompt_sistema
    assert "'- '" in cliente.prompt_sistema


def test_monta_curriculo_mantendo_o_texto_com_quebras_de_linha_devolvido_pela_ia() -> None:
    conteudo = "Starian — Engenheiro\n- Criei APIs\n- Reduzi custos"

    _, curriculo = _extrair({"nome_completo": "Ana Silva", "secoes": {"experiencias": conteudo}})

    assert curriculo.obter_secao(TipoSecao.EXPERIENCIAS).conteudo == conteudo
