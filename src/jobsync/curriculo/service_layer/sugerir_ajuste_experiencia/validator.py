"""Validator de input para o caso de uso SugerirAjusteExperiencia."""
from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.refino import PedidoRefino
from jobsync.curriculo.service_layer.validacoes_sugestao import validar_refino, validar_tamanho_do_texto


class SugerirAjusteExperienciaInputValidator:
    @staticmethod
    def validar(experiencia: ExperienciaParaAvaliacao, refino: PedidoRefino) -> None:
        if not experiencia.texto_completo:
            raise ValueError("A descrição da experiência é obrigatória para pedir sugestões.")
        validar_tamanho_do_texto(experiencia.texto_completo)
        validar_refino(refino)
