"""Domínio Vaga: captura e análise de descrições de vaga."""

from jobsync.vaga.domain.analise_vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from jobsync.vaga.domain.avaliacao_descricao_vaga import AvaliacaoDescricaoVaga
from jobsync.vaga.domain.avaliador_descricao_vaga_port import (
    AvaliadorDescricaoVagaPort,
)
from jobsync.vaga.domain.dados_vaga import DadosVaga
from jobsync.vaga.domain.exceptions import (
    FonteVagaNaoSuportada,
    LeituraVagaIndisponivel,
    LimiteLeituraVagaExcedido,
    LinkVagaInvalido,
    MotivoLeituraIndisponivel,
)
from jobsync.vaga.domain.extrator_dados_vaga_de_texto_port import (
    ExtratorDadosVagaDeTextoPort,
)
from jobsync.vaga.domain.leitor_vaga_por_link_port import LeitorVagaPorLinkPort
from jobsync.vaga.domain.limitador_leitura_vaga_port import LimitadorLeituraVagaPort
from jobsync.vaga.domain.link_vaga import FonteVaga, LinkVaga
from jobsync.vaga.domain.vaga import Vaga
from jobsync.vaga.domain.vaga_repository import VagaRepository

__all__ = [
    "AnaliseVaga",
    "AvaliacaoDescricaoVaga",
    "AvaliadorDescricaoVagaPort",
    "CategoriaRequisitoTecnico",
    "DadosVaga",
    "ExtratorDadosVagaDeTextoPort",
    "FonteVaga",
    "FonteVagaNaoSuportada",
    "LeituraVagaIndisponivel",
    "LeitorVagaPorLinkPort",
    "LimitadorLeituraVagaPort",
    "LimiteLeituraVagaExcedido",
    "LinkVaga",
    "LinkVagaInvalido",
    "MotivoLeituraIndisponivel",
    "OrigemRequisitoTecnico",
    "RequisitoTecnico",
    "TipoRequisitoTecnico",
    "Vaga",
    "VagaRepository",
]
