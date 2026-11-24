import logging

import pytest

from jobsync.vaga import (
    DadosVaga,
    FonteVaga,
    FonteVagaNaoSuportada,
    LeituraVagaIndisponivel,
    LimiteLeituraVagaExcedido,
    LinkVagaInvalido,
    MotivoLeituraIndisponivel,
)
from jobsync.vaga.service_layer.extrair_dados_vaga import ExtrairDadosVaga, ExtrairDadosVagaInputDto

URL_LINKEDIN = "https://br.linkedin.com/jobs/view/engenheiro-at-barte-4484559483?trk=public_jobs_topcard-title"
URL_LINKEDIN_CANONICA = "https://www.linkedin.com/jobs/view/4484559483/"
URL_GUPY = "https://empresa.gupy.io/jobs/123456?utm_source=x"
URL_GUPY_CANONICA = "https://empresa.gupy.io/jobs/123456"
TEXTO = "Engenheiro de Software na Empresa X. Remoto. Python e FastAPI."


class LeitorFake:
    def __init__(self, dados: DadosVaga | None = None, erro: Exception | None = None):
        self.dados = dados or DadosVaga(descricao="Descrição lida", cargo="Cargo lido", empresa="Empresa lida")
        self.erro = erro
        self.links: list = []

    def ler(self, link):
        self.links.append(link)
        if self.erro:
            raise self.erro
        return self.dados


class ExtratorTextoFake:
    def __init__(self):
        self.textos: list[str] = []

    def extrair(self, texto: str) -> DadosVaga:
        self.textos.append(texto)
        return DadosVaga(descricao=texto, cargo="Cargo da IA")


class LimitadorFake:
    def __init__(self, erro: Exception | None = None):
        self.erro = erro
        self.usuarios: list[str] = []

    def registrar(self, usuario_id: str) -> None:
        if self.erro:
            raise self.erro
        self.usuarios.append(usuario_id)


def _criar_servico(linkedin_habilitado: bool = True, limitador=None, leitor_linkedin=None, leitor_generico=None):
    leitor_linkedin = leitor_linkedin or LeitorFake()
    leitor_generico = leitor_generico or LeitorFake()
    extrator = ExtratorTextoFake()
    limitador = limitador or LimitadorFake()
    servico = ExtrairDadosVaga(
        leitores={FonteVaga.LINKEDIN: leitor_linkedin, FonteVaga.OUTRA: leitor_generico},
        extrator_texto=extrator,
        limitador=limitador,
        linkedin_habilitado=linkedin_habilitado,
    )
    return servico, leitor_linkedin, leitor_generico, extrator, limitador


class TestExtrairDadosVaga:
    def test_extrai_dados_do_texto_informado(self):
        servico, leitor_linkedin, leitor_generico, extrator, limitador = _criar_servico()

        dados = servico.executar(ExtrairDadosVagaInputDto(usuario_id="u1", texto=TEXTO))

        assert dados.cargo == "Cargo da IA"
        assert dados.descricao == TEXTO
        assert extrator.textos == [TEXTO]
        assert limitador.usuarios == ["u1"]
        assert leitor_linkedin.links == []
        assert leitor_generico.links == []

    def test_le_link_do_linkedin_pelo_leitor_do_linkedin(self):
        servico, leitor_linkedin, leitor_generico, _, limitador = _criar_servico()

        dados = servico.executar(ExtrairDadosVagaInputDto(usuario_id="u1", url=URL_LINKEDIN))

        assert dados.cargo == "Cargo lido"
        assert dados.url == URL_LINKEDIN_CANONICA
        assert leitor_linkedin.links[0].id_vaga == "4484559483"
        assert leitor_generico.links == []
        assert limitador.usuarios == ["u1"]

    def test_le_link_de_outro_site_pelo_leitor_generico(self):
        servico, leitor_linkedin, leitor_generico, _, _ = _criar_servico()

        dados = servico.executar(ExtrairDadosVagaInputDto(usuario_id="u1", url=URL_GUPY))

        assert dados.url == URL_GUPY_CANONICA
        assert leitor_generico.links[0].url == URL_GUPY_CANONICA
        assert leitor_linkedin.links == []

    def test_texto_prevalece_sobre_o_link_e_mantem_a_url_normalizada(self):
        servico, leitor_linkedin, leitor_generico, extrator, _ = _criar_servico()

        dados = servico.executar(ExtrairDadosVagaInputDto(usuario_id="u1", url=URL_LINKEDIN, texto=TEXTO))

        assert extrator.textos == [TEXTO]
        assert dados.url == URL_LINKEDIN_CANONICA
        assert leitor_linkedin.links == []
        assert leitor_generico.links == []

    def test_texto_prevalece_e_ignora_link_invalido(self):
        servico, _, _, extrator, _ = _criar_servico()

        dados = servico.executar(ExtrairDadosVagaInputDto(usuario_id="u1", url="isto não é link", texto=TEXTO))

        assert extrator.textos == [TEXTO]
        assert dados.url is None

    def test_texto_funciona_com_o_linkedin_desligado(self):
        servico, _, _, extrator, _ = _criar_servico(linkedin_habilitado=False)

        servico.executar(ExtrairDadosVagaInputDto(usuario_id="u1", url=URL_LINKEDIN, texto=TEXTO))

        assert extrator.textos == [TEXTO]

    def test_link_do_linkedin_com_a_fonte_desligada_nao_e_suportado(self):
        servico, leitor_linkedin, _, _, limitador = _criar_servico(linkedin_habilitado=False)

        with pytest.raises(FonteVagaNaoSuportada):
            servico.executar(ExtrairDadosVagaInputDto(usuario_id="u1", url=URL_LINKEDIN))

        assert leitor_linkedin.links == []
        assert limitador.usuarios == []

    def test_outros_sites_continuam_funcionando_com_o_linkedin_desligado(self):
        servico, _, leitor_generico, _, _ = _criar_servico(linkedin_habilitado=False)

        servico.executar(ExtrairDadosVagaInputDto(usuario_id="u1", url=URL_GUPY))

        assert len(leitor_generico.links) == 1

    def test_link_invalido_nao_consome_o_limite(self):
        servico, _, _, _, limitador = _criar_servico()

        with pytest.raises(LinkVagaInvalido):
            servico.executar(ExtrairDadosVagaInputDto(usuario_id="u1", url="https://www.linkedin.com/jobs/search/"))

        assert limitador.usuarios == []

    def test_propaga_limite_excedido_sem_ler_a_vaga(self):
        limitador = LimitadorFake(erro=LimiteLeituraVagaExcedido(segundos_para_nova_tentativa=30))
        servico, leitor_linkedin, _, extrator, _ = _criar_servico(limitador=limitador)

        with pytest.raises(LimiteLeituraVagaExcedido):
            servico.executar(ExtrairDadosVagaInputDto(usuario_id="u1", url=URL_LINKEDIN))
        with pytest.raises(LimiteLeituraVagaExcedido):
            servico.executar(ExtrairDadosVagaInputDto(usuario_id="u1", texto=TEXTO))

        assert leitor_linkedin.links == []
        assert extrator.textos == []

    def test_propaga_leitura_indisponivel(self):
        leitor = LeitorFake(erro=LeituraVagaIndisponivel(MotivoLeituraIndisponivel.BLOQUEADA))
        servico, _, _, _, limitador = _criar_servico(leitor_linkedin=leitor)

        with pytest.raises(LeituraVagaIndisponivel) as erro:
            servico.executar(ExtrairDadosVagaInputDto(usuario_id="u1", url=URL_LINKEDIN))

        assert erro.value.motivo is MotivoLeituraIndisponivel.BLOQUEADA
        assert limitador.usuarios == ["u1"]

    @pytest.mark.parametrize(
        "entrada",
        [
            ExtrairDadosVagaInputDto(usuario_id="u1"),
            ExtrairDadosVagaInputDto(usuario_id="u1", url="  ", texto="  "),
            ExtrairDadosVagaInputDto(usuario_id="", texto=TEXTO),
            ExtrairDadosVagaInputDto(usuario_id="u1", texto="a" * 50_001),
        ],
    )
    def test_recusa_entrada_invalida_sem_consumir_o_limite(self, entrada):
        servico, _, _, _, limitador = _criar_servico()

        with pytest.raises(ValueError):
            servico.executar(entrada)

        assert limitador.usuarios == []

    def test_registra_leitura_concluida_sem_conteudo_nem_caminho_da_url(self, caplog):
        servico, _, _, _, _ = _criar_servico()

        with caplog.at_level(logging.INFO, logger="jobsync.vaga"):
            servico.executar(ExtrairDadosVagaInputDto(usuario_id="u1", url=URL_LINKEDIN))

        mensagens = " ".join(registro.getMessage() for registro in caplog.records)
        assert "linkedin" in mensagens
        assert "www.linkedin.com" in mensagens
        assert "cargo" in mensagens and "empresa" in mensagens
        assert "4484559483" not in mensagens
        assert "Descrição lida" not in mensagens
        assert "Cargo lido" not in mensagens

    def test_registra_aviso_com_o_motivo_quando_a_leitura_falha(self, caplog):
        leitor = LeitorFake(erro=LeituraVagaIndisponivel(MotivoLeituraIndisponivel.TEMPO_ESGOTADO))
        servico, _, _, _, _ = _criar_servico(leitor_linkedin=leitor)

        with caplog.at_level(logging.INFO, logger="jobsync.vaga"):
            with pytest.raises(LeituraVagaIndisponivel):
                servico.executar(ExtrairDadosVagaInputDto(usuario_id="u1", url=URL_LINKEDIN))

        avisos = [registro for registro in caplog.records if registro.levelno == logging.WARNING]
        assert len(avisos) == 1
        assert "tempo_esgotado" in avisos[0].getMessage()
        assert "linkedin" in avisos[0].getMessage()

    def test_registra_aviso_quando_o_limite_e_excedido(self, caplog):
        limitador = LimitadorFake(erro=LimiteLeituraVagaExcedido(segundos_para_nova_tentativa=30))
        servico, _, _, _, _ = _criar_servico(limitador=limitador)

        with caplog.at_level(logging.INFO, logger="jobsync.vaga"):
            with pytest.raises(LimiteLeituraVagaExcedido):
                servico.executar(ExtrairDadosVagaInputDto(usuario_id="u1", texto=TEXTO))

        avisos = [registro for registro in caplog.records if registro.levelno == logging.WARNING]
        assert len(avisos) == 1
        assert "u1" in avisos[0].getMessage()
