"""Validator de input para o caso de uso ExtrairDadosVaga."""

from jobsync.vaga.service_layer.extrair_dados_vaga.dtos import ExtrairDadosVagaInputDto

_TAMANHO_MAXIMO_TEXTO = 50_000


class ExtrairDadosVagaInputValidator:
    """Valida os dados de entrada do caso de uso."""

    @staticmethod
    def validar(input_dto: ExtrairDadosVagaInputDto) -> None:
        """Valida o DTO de entrada e levanta ValueError se inválido."""
        if not input_dto.usuario_id or not input_dto.usuario_id.strip():
            raise ValueError("A pessoa que solicita a leitura da vaga é obrigatória.")
        tem_url = bool(input_dto.url and input_dto.url.strip())
        tem_texto = bool(input_dto.texto and input_dto.texto.strip())
        if not tem_url and not tem_texto:
            raise ValueError("Informe o link da vaga ou o texto da vaga.")
        if tem_texto and len(input_dto.texto.strip()) > _TAMANHO_MAXIMO_TEXTO:
            raise ValueError(f"O texto da vaga excede {_TAMANHO_MAXIMO_TEXTO} caracteres.")
