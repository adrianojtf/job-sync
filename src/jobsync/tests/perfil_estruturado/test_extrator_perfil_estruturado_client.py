"""Testes para o adaptador ExtratorPerfilEstruturadoClient."""

from jobsync.perfil_estruturado import NivelIdioma
from jobsync.perfil_estruturado.adapters.extrator_perfil_estruturado_client import ExtratorPerfilEstruturadoClient


class ClienteOpenAIFake:
    def __init__(self, resposta):
        self.resposta = resposta

    def solicitar_json(self, prompt_sistema: str, prompt_usuario: str) -> dict:
        return self.resposta


class ExtratorTextoFake:
    def __init__(self, texto: str = "texto do pdf"):
        self._texto = texto

    def extrair_texto(self, conteudo_pdf: bytes) -> str:
        return self._texto


class TestExtratorPerfilEstruturadoClient:
    def test_extrai_dados_bem_formados(self):
        resposta = {
            "nome_completo": "Matheus Henrique Moreira",
            "email": "matheus@example.com",
            "linkedin": "linkedin.com/in/matheus",
            "resumo_profissional": "Product Manager com experiência em SaaS.",
            "experiencias": [
                {"empresa": "TechCorp", "cargo": "Eng.", "periodo": "2020-2022", "descricao": "Backend."},
                {"empresa": "OutraEmpresa", "cargo": "PM", "periodo": "2022-Atual", "descricao": "Produto."},
            ],
            "formacoes": [{"instituicao": "USP", "curso": "Ciência da Computação", "periodo": "2016-2020"}],
            "certificacoes": [{"nome": "AWS Certified", "instituicao": "Amazon", "ano": "2023"}],
            "idiomas": [{"idioma": "Inglês", "nivel": "FLUENTE"}],
            "tecnologias": ["Python", "Docker"],
        }
        extrator = ExtratorPerfilEstruturadoClient(
            extrator_texto=ExtratorTextoFake(), cliente_openai=ClienteOpenAIFake(resposta)
        )

        dados = extrator.extrair(b"%PDF-fake")

        assert dados.nome_completo == "Matheus Henrique Moreira"
        assert len(dados.experiencias) == 2
        assert dados.experiencias[0].empresa == "TechCorp"
        assert dados.formacoes[0].instituicao == "USP"
        assert dados.certificacoes[0].nome == "AWS Certified"
        assert dados.idiomas[0].nivel == NivelIdioma.FLUENTE
        assert dados.tecnologias == ("Python", "Docker")

    def test_campos_ausentes_nao_quebram_e_viram_valores_vazios(self):
        resposta = {"nome_completo": "Fulano"}
        extrator = ExtratorPerfilEstruturadoClient(
            extrator_texto=ExtratorTextoFake(), cliente_openai=ClienteOpenAIFake(resposta)
        )

        dados = extrator.extrair(b"%PDF-fake")

        assert dados.nome_completo == "Fulano"
        assert dados.email == ""
        assert dados.experiencias == ()
        assert dados.idiomas == ()
        assert dados.tecnologias == ()

    def test_experiencia_sem_empresa_ou_cargo_e_descartada(self):
        resposta = {
            "experiencias": [
                {"empresa": "", "cargo": "Eng.", "periodo": "2020", "descricao": "x"},
                {"empresa": "TechCorp", "cargo": "", "periodo": "2020", "descricao": "x"},
                {"empresa": "TechCorp", "cargo": "Eng.", "periodo": "2020", "descricao": "x"},
            ]
        }
        extrator = ExtratorPerfilEstruturadoClient(
            extrator_texto=ExtratorTextoFake(), cliente_openai=ClienteOpenAIFake(resposta)
        )

        dados = extrator.extrair(b"%PDF-fake")

        assert len(dados.experiencias) == 1

    def test_nivel_idioma_invalido_usa_intermediario_como_fallback(self):
        resposta = {"idiomas": [{"idioma": "Francês", "nivel": "valor-invalido"}]}
        extrator = ExtratorPerfilEstruturadoClient(
            extrator_texto=ExtratorTextoFake(), cliente_openai=ClienteOpenAIFake(resposta)
        )

        dados = extrator.extrair(b"%PDF-fake")

        assert dados.idiomas[0].nivel == NivelIdioma.INTERMEDIARIO

    def test_resposta_com_tipos_inesperados_nao_quebra(self):
        resposta = {
            "nome_completo": {"objeto": "inesperado"},
            "tecnologias": [{"objeto": "inesperado"}, "Python"],
        }
        extrator = ExtratorPerfilEstruturadoClient(
            extrator_texto=ExtratorTextoFake(), cliente_openai=ClienteOpenAIFake(resposta)
        )

        dados = extrator.extrair(b"%PDF-fake")

        assert isinstance(dados.nome_completo, str)
        assert "Python" in dados.tecnologias


class TestExtratorPerfilEstruturadoClientPrompt:
    def test_o_prompt_pede_a_descricao_literal_com_os_rotulos_preservados(self):
        prompts = []

        class ClienteQueGuarda(ClienteOpenAIFake):
            def solicitar_json(self, prompt_sistema: str, prompt_usuario: str) -> dict:
                prompts.append(prompt_sistema)
                return super().solicitar_json(prompt_sistema, prompt_usuario)

        extrator = ExtratorPerfilEstruturadoClient(
            extrator_texto=ExtratorTextoFake(),
            cliente_openai=ClienteQueGuarda({"nome_completo": "Fulano", "experiencias": []}),
        )

        extrator.extrair(b"%PDF-fake")

        assert "exatamente como está no currículo" in prompts[0]
        assert "Key Achievements" in prompts[0]
