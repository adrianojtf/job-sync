"""Validator de input para o caso de uso GerarPdfCurriculoRevisado."""

from jobsync.curriculo.service_layer.gerar_pdf_curriculo_revisado.dtos import (
    GerarPdfCurriculoRevisadoInputDto,
)
from jobsync.curriculo.service_layer.validacoes_vaga_alvo import (
    validar_cargo_e_empresa_alvo,
    validar_idioma_alvo,
)


class GerarPdfCurriculoRevisadoInputValidator:
    """Valida os dados da vaga-alvo; o rascunho já garante as próprias invariantes."""

    @staticmethod
    def validar(input_dto: GerarPdfCurriculoRevisadoInputDto) -> None:
        validar_idioma_alvo(input_dto.idioma_alvo)
        validar_cargo_e_empresa_alvo(input_dto.cargo_alvo, input_dto.empresa_alvo)
