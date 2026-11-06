"""Validator de input para o caso de uso SugerirAjusteExperienciaAdaptada."""
from jobsync.curriculo.domain.experiencia_adaptada import ExperienciaAdaptada
from jobsync.curriculo.service_layer.validacoes_sugestao import validar_tamanho_do_texto


class SugerirAjusteExperienciaAdaptadaInputValidator:
    @staticmethod
    def validar(experiencia: ExperienciaAdaptada) -> None:
        texto = experiencia.como_descricao()
        if not texto.strip():
            raise ValueError(
                "Preencha ao menos uma conquista ou o contexto da experiência para pedir sugestões."
            )
        validar_tamanho_do_texto(texto)
