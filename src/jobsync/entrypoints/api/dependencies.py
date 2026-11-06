"""Dependências FastAPI (Depends) para repositórios e services."""

from __future__ import annotations

import os
from typing import Annotated

from fastapi import Depends

from jobsync.ats_score import CalcularAtsScore
from jobsync.candidatura.domain.candidatura_repository import CandidaturaRepository
from jobsync.candidatura.service_layer.criar_candidatura import CriarCandidatura
from jobsync.candidatura.service_layer.listar_candidaturas_por_status import (
    ListarCandidaturasPorStatus,
)
from jobsync.candidatura.service_layer.mover_candidatura import MoverCandidatura
from jobsync.curriculo.adapters.ajustador_experiencia_openai_client import (
    AjustadorExperienciaOpenAIClient,
)
from jobsync.curriculo.adapters.ajustador_texto_client import AjustadorTextoClient
from jobsync.curriculo.adapters.extrator_curriculo_client import ExtratorCurriculoClient
from jobsync.curriculo.adapters.avaliador_experiencia_jev_client import (
    AvaliadorExperienciaJevClient,
)
from jobsync.curriculo.adapters.gerador_pdf_client import GeradorPdfClient
from jobsync.curriculo.adapters.gerar_sugestoes_ats_client import GerarSugestoesAtsClient
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga import (
    AdaptarCurriculoParaVaga,
)
from jobsync.curriculo.service_layer.analisar_ats_vaga import AnalisarAtsVaga
from jobsync.curriculo.service_layer.avaliar_experiencia import AvaliarExperiencia
from jobsync.curriculo.service_layer.gerar_carta_apresentacao.service import GerarCartaApresentacao
from jobsync.curriculo.adapters.gerar_carta_apresentacao_client import GerarCartaApresentacaoClient
from jobsync.curriculo_salvo.domain.curriculo_salvo_repository import (
    CurriculoSalvoRepository,
)
from jobsync.curriculo_salvo.service_layer.salvar_curriculo import SalvarCurriculo
from jobsync.curriculo_salvo.service_layer.listar_curriculos_salvos.service import ListarCurriculosSalvos
from jobsync.curriculo_salvo.service_layer.remover_curriculo_salvo.service import RemoverCurriculoSalvo
from jobsync.entrypoints.dependencies import (
    obter_caminho_banco,
    obter_repositorio_candidatura,
    obter_repositorio_curriculo_salvo,
    obter_repositorio_perfil,
    obter_repositorio_perfil_estruturado,
    obter_repositorio_token,
    obter_repositorio_vaga,
)
from jobsync.perfil.domain.perfil_repository import PerfilRepository
from jobsync.perfil.service_layer.entrar_ou_criar_perfil import EntrarOuCriarPerfil
from jobsync.perfil_estruturado.domain.perfil_estruturado_repository import PerfilEstruturadoRepository
from jobsync.perfil_estruturado.service_layer.buscar_perfil_estruturado.service import BuscarPerfilEstruturado
from jobsync.perfil_estruturado.service_layer.importar_perfil_de_pdf.service import ImportarPerfilDePdf
from jobsync.perfil_estruturado.adapters.extrator_perfil_estruturado_client import ExtratorPerfilEstruturadoClient
from jobsync.perfil_estruturado.service_layer.salvar_perfil_estruturado.service import SalvarPerfilEstruturado
from jobsync.vaga.adapters.job_description_analyzer_client import (
    JobDescriptionAnalyzerClient,
)
from jobsync.vaga.adapters.avaliador_descricao_vaga_jev_client import (
    AvaliadorDescricaoVagaJevClient,
)
from jobsync.vaga.domain.vaga_repository import VagaRepository
from jobsync.shared_kernel.adapters.cliente_jev_client import ClienteJev
from jobsync.vaga.service_layer.capturar_vaga import CapturarVaga
from jobsync.vaga.service_layer.avaliar_descricao_vaga import AvaliarDescricaoVaga
from jobsync.vaga.service_layer.listar_vagas_capturadas import ListarVagasCapturadas
from jobsync.vaga_externa.adapters.buscador_adzuna_client import BuscadorAdzunaClient
from jobsync.vaga_externa.adapters.buscador_arbeitnow_client import (
    BuscadorArbeitnowClient,
)
from jobsync.vaga_externa.adapters.buscador_google_custom_search_client import (
    BuscadorGoogleCustomSearchClient,
)
from jobsync.vaga_externa.adapters.buscador_remoteok_client import BuscadorRemoteOkClient
from jobsync.vaga_externa.adapters.buscador_wwr_client import BuscadorWeWorkRemotelyClient
from jobsync.vaga_externa.adapters.extrator_texto_pagina_client import (
    ExtratorTextoPaginaClient,
)
from jobsync.vaga_externa.domain.buscador_vagas_externo_port import BuscadorVagasExternoPort
from jobsync.vaga_externa.service_layer.descobrir_vagas_com_match import (
    DescobrirVagasComMatch,
)

CaminhoBancoDep = Annotated[str, Depends(obter_caminho_banco)]
RepositorioVagaDep = Annotated[VagaRepository, Depends(obter_repositorio_vaga)]
RepositorioCandidaturaDep = Annotated[
    CandidaturaRepository, Depends(obter_repositorio_candidatura)
]
RepositorioCurriculoSalvoDep = Annotated[
    CurriculoSalvoRepository, Depends(obter_repositorio_curriculo_salvo)
]
RepositorioPerfilDep = Annotated[PerfilRepository, Depends(obter_repositorio_perfil)]
RepositorioPerfilEstruturadoDep = Annotated[
    PerfilEstruturadoRepository, Depends(obter_repositorio_perfil_estruturado)
]
RepositorioTokenDep = Annotated[object, Depends(obter_repositorio_token)]


def obter_service_salvar_curriculo(
    repositorio: Annotated[
        CurriculoSalvoRepository, Depends(obter_repositorio_curriculo_salvo)
    ],
) -> SalvarCurriculo:
    return SalvarCurriculo(_repositorio_curriculo_salvo=repositorio)


ServiceSalvarCurriculoDep = Annotated[
    SalvarCurriculo, Depends(obter_service_salvar_curriculo)
]


def _obter_avaliadores_jev():
    """Instancia os avaliadores Jev, ou `None` se o provedor não estiver configurado."""
    try:
        cliente_jev = ClienteJev()
    except (RuntimeError, ValueError):
        return None, None
    return (
        AvaliadorDescricaoVagaJevClient(cliente_jev=cliente_jev),
        AvaliadorExperienciaJevClient(cliente_jev=cliente_jev),
    )


def obter_service_adaptar_curriculo() -> AdaptarCurriculoParaVaga:
    """Monta o caso de uso de adaptação de currículo com adapters concretos."""
    avaliador_vaga, avaliador_experiencia = _obter_avaliadores_jev()
    return AdaptarCurriculoParaVaga(
        extrator=ExtratorCurriculoClient(),
        analisador_vaga=JobDescriptionAnalyzerClient(),
        ajustador_texto=AjustadorTextoClient(),
        gerador_pdf=GeradorPdfClient(),
        avaliador_descricao_vaga=avaliador_vaga,
        ajustador_experiencia=AjustadorExperienciaOpenAIClient(),
        avaliador_experiencia=avaliador_experiencia,
    )


ServiceAdaptarCurriculoDep = Annotated[
    AdaptarCurriculoParaVaga, Depends(obter_service_adaptar_curriculo)
]


def obter_service_analisar_ats_vaga() -> AnalisarAtsVaga:
    """Monta o caso de uso de análise ATS com adapters concretos."""
    return AnalisarAtsVaga(
        extrator=ExtratorCurriculoClient(),
        analisador_vaga=JobDescriptionAnalyzerClient(),
        calcular_ats_score=CalcularAtsScore(),
        gerador_sugestoes=GerarSugestoesAtsClient(),
    )


ServiceAnalisarAtsVagaDep = Annotated[
    AnalisarAtsVaga, Depends(obter_service_analisar_ats_vaga)
]


def obter_service_avaliar_descricao_vaga() -> AvaliarDescricaoVaga:
    """Monta o caso de uso de avaliação de descrição usando Jev."""
    return AvaliarDescricaoVaga(
        avaliador=AvaliadorDescricaoVagaJevClient(cliente_jev=ClienteJev())
    )


ServiceAvaliarDescricaoVagaDep = Annotated[
    AvaliarDescricaoVaga, Depends(obter_service_avaliar_descricao_vaga)
]


def obter_service_avaliar_experiencia() -> AvaliarExperiencia:
    """Monta o caso de uso de avaliação de experiência usando Jev."""
    return AvaliarExperiencia(
        avaliador=AvaliadorExperienciaJevClient(cliente_jev=ClienteJev())
    )


ServiceAvaliarExperienciaDep = Annotated[
    AvaliarExperiencia, Depends(obter_service_avaliar_experiencia)
]


def obter_service_capturar_vaga(
    repositorio: Annotated[VagaRepository, Depends(obter_repositorio_vaga)],
) -> CapturarVaga:
    return CapturarVaga(_repositorio_vaga=repositorio)


ServiceCapturarVagaDep = Annotated[CapturarVaga, Depends(obter_service_capturar_vaga)]


def obter_service_listar_vagas_capturadas(
    repositorio: Annotated[VagaRepository, Depends(obter_repositorio_vaga)],
) -> ListarVagasCapturadas:
    return ListarVagasCapturadas(_repositorio_vaga=repositorio)


ServiceListarVagasCapturadasDep = Annotated[
    ListarVagasCapturadas, Depends(obter_service_listar_vagas_capturadas)
]


def _obter_buscadores_vagas_externo() -> tuple[BuscadorVagasExternoPort, ...]:
    buscadores: list[BuscadorVagasExternoPort] = [
        BuscadorRemoteOkClient(),
        BuscadorWeWorkRemotelyClient(),
        BuscadorArbeitnowClient(),
    ]

    adzuna_app_id = os.getenv("ADZUNA_APP_ID")
    adzuna_app_key = os.getenv("ADZUNA_APP_KEY")
    if adzuna_app_id and adzuna_app_key:
        buscadores.append(
            BuscadorAdzunaClient(app_id=adzuna_app_id, app_key=adzuna_app_key)
        )

    google_api_key = os.getenv("GOOGLE_CSE_API_KEY")
    google_cse_id = os.getenv("GOOGLE_CSE_ID")
    if google_api_key and google_cse_id:
        buscadores.append(
            BuscadorGoogleCustomSearchClient(
                api_key=google_api_key,
                search_engine_id=google_cse_id,
                extrator_texto_pagina=ExtratorTextoPaginaClient(),
            )
        )
    return tuple(buscadores)


def obter_service_descobrir_vagas_com_match() -> DescobrirVagasComMatch:
    """Monta o caso de uso de descoberta de vagas externas com match."""
    return DescobrirVagasComMatch(
        buscadores=_obter_buscadores_vagas_externo(),
        analisador_vaga=JobDescriptionAnalyzerClient(),
        extrator_curriculo=ExtratorCurriculoClient(),
        calcular_score=CalcularAtsScore(),
    )


ServiceDescobrirVagasComMatchDep = Annotated[
    DescobrirVagasComMatch, Depends(obter_service_descobrir_vagas_com_match)
]


def obter_service_criar_candidatura(
    repositorio_candidatura: Annotated[
        CandidaturaRepository, Depends(obter_repositorio_candidatura)
    ],
    repositorio_vaga: Annotated[VagaRepository, Depends(obter_repositorio_vaga)],
) -> CriarCandidatura:
    return CriarCandidatura(
        repositorio_candidatura=repositorio_candidatura,
        repositorio_vaga=repositorio_vaga,
    )


ServiceCriarCandidaturaDep = Annotated[
    CriarCandidatura, Depends(obter_service_criar_candidatura)
]


def obter_service_listar_candidaturas_por_status(
    repositorio: Annotated[
        CandidaturaRepository, Depends(obter_repositorio_candidatura)
    ],
) -> ListarCandidaturasPorStatus:
    return ListarCandidaturasPorStatus(repositorio_candidatura=repositorio)


ServiceListarCandidaturasDep = Annotated[
    ListarCandidaturasPorStatus, Depends(obter_service_listar_candidaturas_por_status)
]


def obter_service_mover_candidatura(
    repositorio: Annotated[
        CandidaturaRepository, Depends(obter_repositorio_candidatura)
    ],
) -> MoverCandidatura:
    return MoverCandidatura(repositorio_candidatura=repositorio)


ServiceMoverCandidaturaDep = Annotated[
    MoverCandidatura, Depends(obter_service_mover_candidatura)
]


def obter_service_entrar_ou_criar_perfil(
    repositorio: Annotated[PerfilRepository, Depends(obter_repositorio_perfil)],
) -> EntrarOuCriarPerfil:
    return EntrarOuCriarPerfil(_repositorio_perfil=repositorio)


ServiceEntrarOuCriarPerfilDep = Annotated[
    EntrarOuCriarPerfil, Depends(obter_service_entrar_ou_criar_perfil)
]


def obter_service_salvar_perfil_estruturado(
    repositorio: Annotated[
        PerfilEstruturadoRepository, Depends(obter_repositorio_perfil_estruturado)
    ],
) -> SalvarPerfilEstruturado:
    return SalvarPerfilEstruturado(repositorio=repositorio)


ServiceSalvarPerfilEstruturadoDep = Annotated[
    SalvarPerfilEstruturado, Depends(obter_service_salvar_perfil_estruturado)
]


def obter_service_buscar_perfil_estruturado(
    repositorio: Annotated[
        PerfilEstruturadoRepository, Depends(obter_repositorio_perfil_estruturado)
    ],
) -> BuscarPerfilEstruturado:
    return BuscarPerfilEstruturado(repositorio=repositorio)


ServiceBuscarPerfilEstruturadoDep = Annotated[
    BuscarPerfilEstruturado, Depends(obter_service_buscar_perfil_estruturado)
]


def obter_service_listar_curriculos_salvos(
    repositorio: Annotated[
        CurriculoSalvoRepository, Depends(obter_repositorio_curriculo_salvo)
    ],
) -> ListarCurriculosSalvos:
    return ListarCurriculosSalvos(_repositorio_curriculo_salvo=repositorio)


ServiceListarCurriculosSalvosDep = Annotated[
    ListarCurriculosSalvos, Depends(obter_service_listar_curriculos_salvos)
]


def obter_service_remover_curriculo_salvo(
    repositorio: Annotated[
        CurriculoSalvoRepository, Depends(obter_repositorio_curriculo_salvo)
    ],
) -> RemoverCurriculoSalvo:
    return RemoverCurriculoSalvo(_repositorio_curriculo_salvo=repositorio)


ServiceRemoverCurriculoSalvoDep = Annotated[
    RemoverCurriculoSalvo, Depends(obter_service_remover_curriculo_salvo)
]


def obter_service_importar_perfil_de_pdf() -> ImportarPerfilDePdf:
    return ImportarPerfilDePdf(extrator=ExtratorPerfilEstruturadoClient())


ServiceImportarPerfilDePdfDep = Annotated[
    ImportarPerfilDePdf, Depends(obter_service_importar_perfil_de_pdf)
]


def obter_service_gerar_carta_apresentacao() -> GerarCartaApresentacao:
    return GerarCartaApresentacao(gerador_carta=GerarCartaApresentacaoClient())


ServiceGerarCartaApresentacaoDep = Annotated[
    GerarCartaApresentacao, Depends(obter_service_gerar_carta_apresentacao)
]
