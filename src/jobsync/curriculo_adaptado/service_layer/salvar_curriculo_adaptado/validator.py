"""Validator de input do caso de uso SalvarCurriculoAdaptado."""
from jobsync.curriculo.service_layer.validacoes_vaga_alvo import (
    validar_cargo_e_empresa_alvo,
    validar_idioma_alvo,
)
from jobsync.curriculo_adaptado.service_layer.salvar_curriculo_adaptado.dtos import (
    SalvarCurriculoAdaptadoInputDto,
)


class SalvarCurriculoAdaptadoInputValidator:
    @staticmethod
    def validar(input_dto: SalvarCurriculoAdaptadoInputDto) -> None:
        if not input_dto.perfil_identificador or not input_dto.perfil_identificador.strip():
            raise ValueError("O identificador do perfil é obrigatório.")
        validar_idioma_alvo(input_dto.idioma_alvo)
        validar_cargo_e_empresa_alvo(input_dto.cargo_alvo, input_dto.empresa_alvo)
        if not input_dto.descricao_vaga or not input_dto.descricao_vaga.strip():
            raise ValueError("A descrição da vaga é obrigatória.")
