"""Caso de uso: importar um rascunho de perfil estruturado a partir de um PDF.

O resultado é sempre um rascunho (DadosPerfilExtraidos) para revisão do
usuário — nunca persistido automaticamente. Salvar de fato é responsabilidade
do caso de uso SalvarPerfilEstruturado, chamado separadamente pela UI depois
que o usuário revisar/editar os campos.
"""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.perfil_estruturado.domain.extrator_perfil_estruturado_port import ExtratorPerfilEstruturadoPort
from jobsync.perfil_estruturado.domain.perfil_estruturado import DadosPerfilExtraidos
from jobsync.perfil_estruturado.service_layer.importar_perfil_de_pdf.dtos import ImportarPerfilDePdfInputDto
from jobsync.perfil_estruturado.service_layer.importar_perfil_de_pdf.validator import ImportarPerfilDePdfInputValidator


@dataclass
class ImportarPerfilDePdf:
    """Extrai um rascunho de perfil estruturado a partir de um PDF, via IA."""

    extrator: ExtratorPerfilEstruturadoPort

    def executar(self, input_dto: ImportarPerfilDePdfInputDto) -> DadosPerfilExtraidos:
        ImportarPerfilDePdfInputValidator.validar(input_dto)
        return self.extrator.extrair(input_dto.pdf_curriculo)
