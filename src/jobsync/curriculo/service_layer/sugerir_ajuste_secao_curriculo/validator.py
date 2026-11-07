"""Validator de input para o caso de uso SugerirAjusteSecaoCurriculo."""
from jobsync.curriculo.domain.curriculo import SecaoCurriculo, TipoSecao
from jobsync.curriculo.service_layer.validacoes_sugestao import validar_tamanho_do_texto

SECOES_COM_SUGESTAO = (TipoSecao.PERFIL, TipoSecao.TECNOLOGIAS, TipoSecao.EXPERIENCIAS)


class SugerirAjusteSecaoCurriculoInputValidator:
    @staticmethod
    def validar(secao: SecaoCurriculo) -> None:
        if secao.tipo not in SECOES_COM_SUGESTAO:
            raise ValueError(f"A seção {secao.tipo.name} não tem sugestão de IA.")
        validar_tamanho_do_texto(secao.conteudo)
