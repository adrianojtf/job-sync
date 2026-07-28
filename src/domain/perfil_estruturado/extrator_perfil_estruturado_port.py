"""Porta para extração de dados de perfil estruturado a partir de um PDF (Fase 5)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from domain.perfil_estruturado import DadosPerfilExtraidos


class ExtratorPerfilEstruturadoPort(ABC):
    """Extrai os campos estruturados do perfil diretamente de um PDF, via IA.

    Usado para pré-preencher o formulário de perfil a partir de um currículo
    já existente (biblioteca da Fase 0, ou export "Salvar como PDF" do
    LinkedIn) — o resultado é sempre um rascunho revisável, nunca persistido
    automaticamente.
    """

    @abstractmethod
    def extrair(self, pdf_bytes: bytes) -> DadosPerfilExtraidos:
        raise NotImplementedError
