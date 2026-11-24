import pytest

from jobsync.vaga import FonteVaga, LinkVaga, LinkVagaInvalido


class TestLinkVaga:
    def test_normaliza_link_direto_do_linkedin_para_forma_canonica(self):
        link = LinkVaga.criar(
            "https://br.linkedin.com/jobs/view/forward-deployed-enginneer-senior-at-barte-4484559483?trk=public_jobs_topcard-title"
        )

        assert link.url == "https://www.linkedin.com/jobs/view/4484559483/"
        assert link.fonte is FonteVaga.LINKEDIN
        assert link.id_vaga == "4484559483"

    def test_aceita_link_do_linkedin_apenas_com_id(self):
        link = LinkVaga.criar("https://www.linkedin.com/jobs/view/4484559483/")

        assert link.url == "https://www.linkedin.com/jobs/view/4484559483/"
        assert link.id_vaga == "4484559483"

    def test_remove_rastreamento_de_link_vindo_de_email_do_linkedin(self):
        link = LinkVaga.criar(
            "https://www.linkedin.com/jobs/view/4484559483/?trk=eml-email_jobs_saved_job_reminder_01-saved~jobs-0-company_logo&trackingId=abc&refId=xyz&midToken=1&midSig=2"
        )

        assert link.url == "https://www.linkedin.com/jobs/view/4484559483/"

    def test_identifica_vaga_em_link_de_busca_com_current_job_id(self):
        link = LinkVaga.criar(
            "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4484559483&discover=recommended"
        )

        assert link.url == "https://www.linkedin.com/jobs/view/4484559483/"
        assert link.id_vaga == "4484559483"
        assert link.fonte is FonteVaga.LINKEDIN

    def test_levanta_erro_para_link_do_linkedin_sem_vaga_especifica(self):
        with pytest.raises(LinkVagaInvalido):
            LinkVaga.criar("https://www.linkedin.com/jobs/search/?keywords=python")

    def test_link_de_outro_site_e_classificado_como_outra_fonte(self):
        link = LinkVaga.criar("https://empresa.gupy.io/jobs/123456")

        assert link.fonte is FonteVaga.OUTRA
        assert link.id_vaga is None
        assert link.url == "https://empresa.gupy.io/jobs/123456"

    def test_remove_parametros_de_rastreamento_e_fragmento_de_outros_sites(self):
        link = LinkVaga.criar(
            "https://boards.greenhouse.io/empresa/jobs/123?gh_jid=123&utm_source=x&utm_medium=y&fbclid=z#apply"
        )

        assert link.url == "https://boards.greenhouse.io/empresa/jobs/123?gh_jid=123"

    def test_normaliza_host_para_minusculas_e_remove_espacos(self):
        link = LinkVaga.criar("  HTTPS://Empresa.Gupy.IO/jobs/1  ")

        assert link.url == "https://empresa.gupy.io/jobs/1"

    def test_assume_https_quando_link_vem_sem_esquema(self):
        link = LinkVaga.criar("empresa.gupy.io/jobs/1")

        assert link.url == "https://empresa.gupy.io/jobs/1"

    @pytest.mark.parametrize(
        "entrada",
        [
            "",
            "   ",
            "ftp://exemplo.com/vaga",
            "javascript:alert(1)",
            "file:///etc/passwd",
            "mailto:alguem@exemplo.com",
            "https://",
            "https://usuario:senha@exemplo.com/vaga",
            "não é um link",
        ],
    )
    def test_levanta_erro_para_entradas_invalidas(self, entrada):
        with pytest.raises(LinkVagaInvalido):
            LinkVaga.criar(entrada)

    def test_levanta_erro_para_link_acima_do_tamanho_maximo(self):
        with pytest.raises(LinkVagaInvalido):
            LinkVaga.criar("https://exemplo.com/" + "a" * 3000)

    def test_link_vaga_invalido_e_um_value_error(self):
        with pytest.raises(ValueError):
            LinkVaga.criar("")
