"""Validator de input para o caso de uso SugerirAjusteExperienciaAdaptada."""
from jobsync.curriculo.domain.experiencia_adaptada import ExperienciaAdaptada
from jobsync.curriculo.domain.refino import PedidoRefino
from jobsync.curriculo.service_layer.validacoes_sugestao import validar_refino, validar_tamanho_do_texto


MENSAGEM_SEM_CONTEUDO = (
    "Preencha ao menos uma conquista ou o contexto da experiência para pedir sugestões."
)


class SugerirAjusteExperienciaAdaptadaInputValidator:
    @staticmethod
    def validar(experiencia: ExperienciaAdaptada, refino: PedidoRefino) -> None:
        if not experiencia.tem_conteudo:
            raise ValueError(MENSAGEM_SEM_CONTEUDO)
        validar_tamanho_do_texto(experiencia.como_descricao())
        validar_refino(refino)
