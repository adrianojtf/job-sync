"""Testes das entidades de domínio Curriculo e SecaoCurriculo."""
import pytest

from jobsync.curriculo import Curriculo, SecaoCurriculo, TipoSecao


class TestSecaoCurriculo:
    def test_cria_secao_com_tipo_e_conteudo(self):
        secao = SecaoCurriculo(tipo=TipoSecao.TECNOLOGIAS, titulo="Tecnologias", conteudo="Java, Python")

        assert secao.tipo == TipoSecao.TECNOLOGIAS
        assert secao.conteudo == "Java, Python"

    def test_secao_com_conteudo_vazio_gera_erro(self):
        with pytest.raises(ValueError, match="conteúdo"):
            SecaoCurriculo(tipo=TipoSecao.PERFIL, titulo="Perfil", conteudo="   ")

    def test_atualizar_conteudo_retorna_nova_secao_imutavel(self):
        secao_original = SecaoCurriculo(tipo=TipoSecao.PERFIL, titulo="Perfil", conteudo="texto original")

        secao_ajustada = secao_original.com_novo_conteudo("texto ajustado")

        assert secao_original.conteudo == "texto original"
        assert secao_ajustada.conteudo == "texto ajustado"
        assert secao_ajustada.tipo == secao_original.tipo


class TestCurriculo:
    def _criar_curriculo_valido(self) -> Curriculo:
        return Curriculo(
            nome_completo="Adriano João Teixeira Filho",
            email="adriano@example.com",
            linkedin="linkedin.com/in/adriano",
            secoes=(
                SecaoCurriculo(TipoSecao.TECNOLOGIAS, "Tecnologias", "Java, Go, Python"),
                SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Engenheiro de software backend."),
                SecaoCurriculo(TipoSecao.EXPERIENCIAS, "Experiências", "Starian - Engenheiro de Software"),
                SecaoCurriculo(TipoSecao.FORMACAO, "Formação acadêmica", "Estácio - ADS"),
            ),
        )

    def test_cria_curriculo_com_secoes(self):
        curriculo = self._criar_curriculo_valido()

        assert curriculo.nome_completo == "Adriano João Teixeira Filho"
        assert len(curriculo.secoes) == 4

    def test_curriculo_sem_nome_gera_erro(self):
        with pytest.raises(ValueError, match="nome"):
            Curriculo(nome_completo="", email="a@a.com", linkedin="", secoes=())

    def test_obter_secao_por_tipo(self):
        curriculo = self._criar_curriculo_valido()

        secao_perfil = curriculo.obter_secao(TipoSecao.PERFIL)

        assert secao_perfil is not None
        assert secao_perfil.conteudo == "Engenheiro de software backend."

    def test_obter_secao_inexistente_retorna_none(self):
        curriculo = self._criar_curriculo_valido()

        assert curriculo.obter_secao(TipoSecao.CERTIFICACOES) is None

    def test_substituir_secao_retorna_novo_curriculo_imutavel(self):
        curriculo_original = self._criar_curriculo_valido()
        nova_secao_perfil = SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Novo perfil ajustado para a vaga.")

        curriculo_ajustado = curriculo_original.substituir_secao(nova_secao_perfil)

        assert curriculo_original.obter_secao(TipoSecao.PERFIL).conteudo == "Engenheiro de software backend."
        assert curriculo_ajustado.obter_secao(TipoSecao.PERFIL).conteudo == "Novo perfil ajustado para a vaga."
        assert len(curriculo_ajustado.secoes) == 4

    def test_substituir_secao_de_tipo_nao_existente_adiciona_secao(self):
        curriculo_original = self._criar_curriculo_valido()
        nova_secao = SecaoCurriculo(TipoSecao.CERTIFICACOES, "Certificações", "AWS Certified")

        curriculo_ajustado = curriculo_original.substituir_secao(nova_secao)

        assert len(curriculo_ajustado.secoes) == 5
        assert curriculo_ajustado.obter_secao(TipoSecao.CERTIFICACOES).conteudo == "AWS Certified"
