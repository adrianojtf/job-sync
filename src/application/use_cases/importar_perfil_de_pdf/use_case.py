"""Caso de uso: importar um rascunho de perfil estruturado a partir de um PDF.

O resultado é sempre um rascunho (DadosPerfilExtraidos) para revisão do
usuário — nunca persistido automaticamente. Salvar de fato é responsabilidade
do caso de uso SalvarPerfilEstruturado, chamado separadamente pela UI depois
que o usuário revisar/editar os campos.
"""
from __future__ import annotations

from application.use_cases.importar_perfil_de_pdf.dtos import ImportarPerfilDePdfInputDto
from application.use_cases.importar_perfil_de_pdf.validator import ImportarPerfilDePdfInputValidator
from domain.perfil_estruturado import DadosPerfilExtraidos
from domain.perfil_estruturado.extrator_perfil_estruturado_port import ExtratorPerfilEstruturadoPort


class ImportarPerfilDePdf:
    """Extrai um rascunho de perfil estruturado a partir de um PDF, via IA."""

    def __init__(self, extrator: ExtratorPerfilEstruturadoPort) -> None:
        self._extrator = extrator

    def executar(self, input_dto: ImportarPerfilDePdfInputDto) -> DadosPerfilExtraidos:
        ImportarPerfilDePdfInputValidator.validar(input_dto)
        return self._extrator.extrair(input_dto.pdf_curriculo)
