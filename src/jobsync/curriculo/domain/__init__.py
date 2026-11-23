"""Camada de domínio do Currículo."""

from jobsync.curriculo.domain.competencias import (
    CategoriaCompetencia,
    categorias_de_texto,
    categorias_para_texto,
)
from jobsync.curriculo.domain.contexto_vaga import ContextoVaga
from jobsync.curriculo.domain.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from jobsync.curriculo.domain.experiencia_adaptada import ExperienciaAdaptada
from jobsync.curriculo.domain.equivalencia_tecnologia import (
    AjusteTecnologia,
    DiretrizesExperiencia,
    EquivalenciaTecnologia,
    ManutencaoTecnologia,
)
from jobsync.curriculo.domain.plano_adaptacao import PlanoAdaptacao
from jobsync.curriculo.domain.avaliacao_experiencia import (
    AvaliacaoExperiencia,
    ExperienciaParaAvaliacao,
)
from jobsync.curriculo.domain.avaliador_experiencia_port import (
    AvaliadorExperienciaPort,
)
from jobsync.curriculo.domain.ajustador_texto_port import AjustadorTextoPort
from jobsync.curriculo.domain.ajustador_experiencia_port import AjustadorExperienciaPort
from jobsync.curriculo.domain.extrator_curriculo_port import ExtratorCurriculoPort
from jobsync.curriculo.domain.identificador_equivalencias_port import IdentificadorEquivalenciasPort
from jobsync.curriculo.domain.gerador_pdf_port import GeradorPdfPort
from jobsync.curriculo.domain.gerar_carta_apresentacao_port import GerarCartaApresentacaoPort
from jobsync.curriculo.domain.gerar_sugestoes_ats_port import GerarSugestoesAtsPort
from jobsync.curriculo.domain.melhorador_texto_curriculo_port import MelhoradorTextoCurriculoPort
from jobsync.curriculo.domain.rascunho_curriculo_adaptado import RascunhoCurriculoAdaptado
from jobsync.curriculo.domain.refino import FocoRefino, PedidoRefino, SugestaoRefinada

__all__ = [
    "CategoriaCompetencia",
    "categorias_de_texto",
    "categorias_para_texto",
    "ContextoVaga",
    "Curriculo",
    "ExperienciaAdaptada",
    "AjusteTecnologia",
    "DiretrizesExperiencia",
    "EquivalenciaTecnologia",
    "ManutencaoTecnologia",
    "PlanoAdaptacao",
    "SecaoCurriculo",
    "TipoSecao",
    "AvaliacaoExperiencia",
    "ExperienciaParaAvaliacao",
    "AvaliadorExperienciaPort",
    "AjustadorTextoPort",
    "AjustadorExperienciaPort",
    "ExtratorCurriculoPort",
    "IdentificadorEquivalenciasPort",
    "GeradorPdfPort",
    "GerarCartaApresentacaoPort",
    "GerarSugestoesAtsPort",
    "MelhoradorTextoCurriculoPort",
    "RascunhoCurriculoAdaptado",
    "FocoRefino",
    "PedidoRefino",
    "SugestaoRefinada",
]
