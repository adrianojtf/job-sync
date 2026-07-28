"""Interface web do MVP (Streamlit).

Responsabilidade única desta camada: coletar entrada do usuário, montar
solicitações (DTOs) para os casos de uso e apresentar o resultado. Toda a
lógica de negócio vive nas camadas domain/application; aqui só há
orquestração de UI e composição de dependências (Composition Root), conforme
Hexagonal Architecture.

A navegação é organizada por um menu lateral (`st.sidebar`) com três páginas:
"Adaptar Currículo", "Analisar ATS" (diagnóstico rápido, sem gerar PDF
adaptado) e "Vagas & Candidaturas" (captura de vagas + Kanban). O visual é
Streamlit padrão com uma camada de CSS customizado inspirada no shadcn/ui
(cantos arredondados, paleta neutra, cards com borda sutil) — não há
migração para React/Next.js, apenas estética aproximada dentro do Streamlit.
"""
from __future__ import annotations

import os
import sys
import uuid
from datetime import date
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from application.use_cases.adaptar_curriculo_para_vaga import (
    AdaptarCurriculoParaVaga,
    AdaptarCurriculoParaVagaInputDto,
)
from application.use_cases.analisar_ats_vaga import AnalisarAtsVaga, AnalisarAtsVagaInputDto
from application.use_cases.candidatar_na_vaga_externa import (
    CandidatarNaVagaExterna,
    CandidatarNaVagaExternaInputDto,
)
from application.use_cases.capturar_vaga import CapturarVaga, CapturarVagaInputDto
from application.use_cases.criar_candidatura import CriarCandidatura, CriarCandidaturaInputDto
from application.use_cases.buscar_perfil_estruturado import BuscarPerfilEstruturado
from application.use_cases.descobrir_vagas_com_match import DescobrirVagasComMatch
from application.use_cases.entrar_ou_criar_perfil import EntrarOuCriarPerfil
from application.use_cases.gerar_carta_apresentacao import GerarCartaApresentacao
from application.use_cases.importar_perfil_de_pdf import ImportarPerfilDePdf, ImportarPerfilDePdfInputDto
from application.use_cases.listar_candidaturas_por_status import ListarCandidaturasPorStatus
from application.use_cases.listar_curriculos_salvos import ListarCurriculosSalvos
from application.use_cases.listar_vagas_capturadas import ListarVagasCapturadas
from application.use_cases.mover_candidatura import MoverCandidatura
from application.use_cases.remover_curriculo_salvo import (
    CurriculoSalvoNaoEncontrado,
    RemoverCurriculoSalvo,
)
from application.use_cases.salvar_curriculo import (
    LimiteCurriculosSalvosExcedido,
    SalvarCurriculo,
    SalvarCurriculoInputDto,
)
from application.use_cases.salvar_perfil_estruturado import (
    SalvarPerfilEstruturado,
    SalvarPerfilEstruturadoInputDto,
)
from domain.ats_score.calcular_ats_score_service import CalcularAtsScore
from domain.candidatura import StatusCandidatura
from domain.curriculo import Curriculo
from domain.curriculo_salvo import CurriculoSalvo
from domain.perfil_estruturado import (
    Certificacao,
    ExperienciaProfissional,
    FormacaoAcademica,
    Idioma,
    NivelIdioma,
)
from domain.perfil_estruturado.montar_curriculo_do_perfil_estruturado_service import (
    MontarCurriculoDoPerfilEstruturado,
)
from domain.vaga_externa import VagaComScore
from domain.vaga_externa.buscador_vagas_externo_port import BuscadorVagasExternoPort
from infrastructure.extractors.extrator_curriculo_segmentado_ia import (
    ExtratorCurriculoSegmentadoPorIA,
)
from infrastructure.fontes_vagas.buscador_adzuna import BuscadorAdzuna
from infrastructure.fontes_vagas.buscador_arbeitnow import BuscadorArbeitnow
from infrastructure.fontes_vagas.buscador_google_custom_search import BuscadorGoogleCustomSearch
from infrastructure.fontes_vagas.buscador_remoteok import BuscadorRemoteOk
from infrastructure.fontes_vagas.buscador_wwr import BuscadorWeWorkRemotely
from infrastructure.fontes_vagas.extrator_texto_pagina import ExtratorTextoPagina
from infrastructure.llm.ajustador_texto_groq import AjustadorTextoGroq
from infrastructure.llm.cliente_groq import ClienteGroq
from infrastructure.llm.gerador_carta_apresentacao_groq import GeradorCartaApresentacaoGroq
from infrastructure.llm.gerador_sugestoes_ats_groq import GeradorSugestoesAtsGroq
from infrastructure.llm.extrator_perfil_estruturado_groq import ExtratorPerfilEstruturadoGroq
from infrastructure.llm.job_description_analyzer_groq import JobDescriptionAnalyzerGroq
from infrastructure.pdf.gerador_pdf_reportlab import GeradorPdfReportLab
from infrastructure.persistence.candidatura_repository_impl import CandidaturaRepositoryImpl
from infrastructure.persistence.curriculo_salvo_repository_impl import CurriculoSalvoRepositoryImpl
from infrastructure.persistence.perfil_estruturado_repository_impl import (
    PerfilEstruturadoRepositoryImpl,
)
from infrastructure.persistence.perfil_repository_impl import PerfilRepositoryImpl
from infrastructure.persistence.token_captura_repository_impl import TokenCapturaRepositoryImpl
from infrastructure.persistence.vaga_repository_impl import VagaRepositoryImpl

load_dotenv()

DIRETORIO_ARMAZENAMENTO = Path(__file__).resolve().parent.parent.parent / "storage"
DIRETORIO_ARMAZENAMENTO.mkdir(exist_ok=True)
_CAMINHO_BANCO = str(DIRETORIO_ARMAZENAMENTO / "job_sync.db")

_ORDEM_STATUS = (
    StatusCandidatura.APLICADO,
    StatusCandidatura.ENTREVISTA,
    StatusCandidatura.OFERTA,
    StatusCandidatura.REJEITADO,
)
_LABEL_STATUS = {
    StatusCandidatura.APLICADO: "Aplicado",
    StatusCandidatura.ENTREVISTA: "Entrevista",
    StatusCandidatura.OFERTA: "Oferta",
    StatusCandidatura.REJEITADO: "Rejeitado",
}

_ROTULO_NIVEL_IDIOMA = {
    NivelIdioma.BASICO: "Básico",
    NivelIdioma.INTERMEDIARIO: "Intermediário",
    NivelIdioma.AVANCADO: "Avançado",
    NivelIdioma.FLUENTE: "Fluente",
    NivelIdioma.NATIVO: "Nativo",
}
_NIVEL_IDIOMA_POR_ROTULO = {rotulo: nivel for nivel, rotulo in _ROTULO_NIVEL_IDIOMA.items()}

_PAGINA_MEU_PERFIL = "Meu Perfil"
_PAGINA_ADAPTAR_CURRICULO = "Adaptar Currículo"
_PAGINA_ANALISAR_ATS = "Analisar ATS"
_PAGINA_VAGAS = "Vagas"
_PAGINA_VAGAS_E_CANDIDATURAS = "Vagas & Candidaturas"


# --- Composition Root -------------------------------------------------------

def _montar_caso_de_uso() -> AdaptarCurriculoParaVaga:
    """Monta os adapters concretos e injeta nas portas do caso de uso de adaptação."""
    cliente_groq = ClienteGroq()
    extrator = ExtratorCurriculoSegmentadoPorIA(cliente_groq=cliente_groq)
    analisador_vaga = JobDescriptionAnalyzerGroq(cliente_groq=cliente_groq)
    ajustador_texto = AjustadorTextoGroq(cliente_groq=cliente_groq)
    gerador_pdf = GeradorPdfReportLab()
    return AdaptarCurriculoParaVaga(extrator, analisador_vaga, ajustador_texto, gerador_pdf)


def _montar_gerador_carta_apresentacao() -> GerarCartaApresentacao:
    gerador_carta_groq = GeradorCartaApresentacaoGroq(cliente_groq=ClienteGroq())
    return GerarCartaApresentacao(gerador_carta=gerador_carta_groq)


def _montar_analisar_ats_vaga() -> AnalisarAtsVaga:
    """Monta o caso de uso de diagnóstico de ATS (sem adaptar seções — mais rápido e barato)."""
    cliente_groq = ClienteGroq()
    extrator = ExtratorCurriculoSegmentadoPorIA(cliente_groq=cliente_groq)
    analisador_vaga = JobDescriptionAnalyzerGroq(cliente_groq=cliente_groq)
    gerador_sugestoes = GeradorSugestoesAtsGroq(cliente_groq=cliente_groq)
    return AnalisarAtsVaga(
        extrator=extrator,
        analisador_vaga=analisador_vaga,
        calcular_ats_score=CalcularAtsScore(),
        gerador_sugestoes=gerador_sugestoes,
    )


def _montar_buscadores_vagas_externo() -> tuple[BuscadorVagasExternoPort, ...]:
    """Monta apenas as fontes cujas credenciais (quando exigidas) estão configuradas no .env."""
    buscadores: list[BuscadorVagasExternoPort] = [
        BuscadorRemoteOk(),
        BuscadorWeWorkRemotely(),
        BuscadorArbeitnow(),
    ]

    adzuna_app_id = os.getenv("ADZUNA_APP_ID")
    adzuna_app_key = os.getenv("ADZUNA_APP_KEY")
    if adzuna_app_id and adzuna_app_key:
        buscadores.append(BuscadorAdzuna(app_id=adzuna_app_id, app_key=adzuna_app_key))

    google_api_key = os.getenv("GOOGLE_CSE_API_KEY")
    google_cse_id = os.getenv("GOOGLE_CSE_ID")
    if google_api_key and google_cse_id:
        buscadores.append(
            BuscadorGoogleCustomSearch(
                api_key=google_api_key,
                search_engine_id=google_cse_id,
                extrator_texto_pagina=ExtratorTextoPagina(),
            )
        )
    return tuple(buscadores)


def _montar_descobrir_vagas_com_match() -> DescobrirVagasComMatch:
    cliente_groq = ClienteGroq()
    return DescobrirVagasComMatch(
        buscadores=_montar_buscadores_vagas_externo(),
        analisador_vaga=JobDescriptionAnalyzerGroq(cliente_groq=cliente_groq),
        extrator_curriculo=ExtratorCurriculoSegmentadoPorIA(cliente_groq=cliente_groq),
        calcular_score=CalcularAtsScore(),
    )


def _montar_candidatar_na_vaga_externa() -> CandidatarNaVagaExterna:
    cliente_groq = ClienteGroq()
    return CandidatarNaVagaExterna(
        extrator=ExtratorCurriculoSegmentadoPorIA(cliente_groq=cliente_groq),
        analisador_vaga=JobDescriptionAnalyzerGroq(cliente_groq=cliente_groq),
        ajustador_texto=AjustadorTextoGroq(cliente_groq=cliente_groq),
        gerador_pdf=GeradorPdfReportLab(),
        calcular_ats_score=CalcularAtsScore(),
        gerador_carta=GeradorCartaApresentacaoGroq(cliente_groq=cliente_groq),
    )


@st.cache_resource
def _montar_repositorio_perfil() -> PerfilRepositoryImpl:
    return PerfilRepositoryImpl(caminho_banco=_CAMINHO_BANCO)


@st.cache_resource
def _montar_repositorio_curriculo_salvo() -> CurriculoSalvoRepositoryImpl:
    return CurriculoSalvoRepositoryImpl(caminho_banco=_CAMINHO_BANCO)


@st.cache_resource
def _montar_repositorio_vaga() -> VagaRepositoryImpl:
    return VagaRepositoryImpl(caminho_banco=_CAMINHO_BANCO)


@st.cache_resource
def _montar_repositorio_candidatura() -> CandidaturaRepositoryImpl:
    return CandidaturaRepositoryImpl(caminho_banco=_CAMINHO_BANCO)


@st.cache_resource
def _montar_repositorio_token_captura() -> TokenCapturaRepositoryImpl:
    return TokenCapturaRepositoryImpl(caminho_banco=_CAMINHO_BANCO)


@st.cache_resource
def _montar_repositorio_perfil_estruturado() -> PerfilEstruturadoRepositoryImpl:
    return PerfilEstruturadoRepositoryImpl(caminho_banco=_CAMINHO_BANCO)


def _montar_importar_perfil_de_pdf() -> ImportarPerfilDePdf:
    cliente_groq = ClienteGroq()
    return ImportarPerfilDePdf(extrator=ExtratorPerfilEstruturadoGroq(cliente_groq=cliente_groq))


def _carregar_secrets_para_env() -> None:
    """Repassa st.secrets (produção) para os.environ, usado por ClienteGroq via os.getenv().

    Precisa ser chamada DEPOIS de st.set_page_config() — acessar st.secrets
    antes conta como "primeiro comando Streamlit" e quebra a exigência de
    set_page_config ser sempre o primeiro comando da página.
    """
    try:
        for chave, valor in st.secrets.items():
            os.environ.setdefault(chave, str(valor))
    except Exception:  # noqa: BLE001 - sem secrets.toml em dev local; .env já cobre esse caso
        pass


def _salvar_no_armazenamento(nome_arquivo: str, pdf_bytes: bytes) -> Path:
    caminho = DIRETORIO_ARMAZENAMENTO / nome_arquivo
    caminho.write_bytes(pdf_bytes)
    return caminho


def _obter_curriculo_do_perfil(
    repositorio_perfil_estruturado: PerfilEstruturadoRepositoryImpl, perfil_identificador: str
) -> Curriculo | None:
    """Retorna o Curriculo montado a partir do perfil estruturado, ou None.

    None cobre tanto "perfil não existe" quanto "perfil existe mas está vazio"
    (sem conteúdo mínimo) — nos dois casos a UI deve cair no fluxo de upload
    de PDF já existente, como se o perfil não existisse.
    """
    perfil = BuscarPerfilEstruturado(repositorio=repositorio_perfil_estruturado).executar(perfil_identificador)
    if perfil is None:
        return None
    return MontarCurriculoDoPerfilEstruturado().executar(perfil)


# --- Estilo (inspirado no shadcn/ui, sem sair do Streamlit) -----------------

def _injetar_estilo_shadcn() -> None:
    st.markdown(
        """
        <style>
        :root { --radius: 0.6rem; }
        .stButton > button, .stDownloadButton > button {
            border-radius: var(--radius);
            border: 1px solid #e4e4e7;
        }
        .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
            background-color: #18181b;
            color: #fafafa;
            border-color: #18181b;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: var(--radius) !important;
            border: 1px solid #e4e4e7 !important;
        }
        section[data-testid="stSidebar"] {
            border-right: 1px solid #e4e4e7;
        }
        div[data-testid="stMetric"] {
            border: 1px solid #e4e4e7;
            border-radius: var(--radius);
            padding: 0.75rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --- Autenticação ------------------------------------------------------------

def _renderizar_tela_de_entrada(repositorio_perfil: PerfilRepositoryImpl) -> None:
    st.title("job-sync")
    st.caption("Informe um identificador para acessar seu espaço pessoal (sem necessidade de senha).")

    identificador = st.text_input("Identificador (ex: seu nome ou apelido)")
    if st.button("Entrar", type="primary") and identificador.strip():
        use_case = EntrarOuCriarPerfil(repositorio_perfil=repositorio_perfil)
        perfil = use_case.executar(identificador.strip())
        st.session_state["perfil_identificador"] = perfil.identificador
        st.rerun()


# --- Página: Meu Perfil (currículo mestre estruturado) ----------------------

def _ids_lista(chave_ids: str) -> list[str]:
    if chave_ids not in st.session_state:
        st.session_state[chave_ids] = []
    return st.session_state[chave_ids]


def _carregar_dados_no_estado(dados) -> None:
    """Popula o session_state a partir de um PerfilEstruturado ou DadosPerfilExtraidos.

    Os dois tipos têm os mesmos nomes de campo (exceto perfil_identificador),
    então a mesma função funciona para os dois casos (carregar do banco, ou
    pré-preencher a partir de uma importação de PDF).
    """
    st.session_state["perfil_nome_completo"] = dados.nome_completo
    st.session_state["perfil_email"] = dados.email
    st.session_state["perfil_linkedin"] = dados.linkedin
    st.session_state["perfil_resumo"] = dados.resumo_profissional
    st.session_state["perfil_tecnologias_texto"] = ", ".join(dados.tecnologias)

    ids_exp = [str(uuid.uuid4()) for _ in dados.experiencias]
    st.session_state["perfil_exp_ids"] = ids_exp
    for id_linha, exp in zip(ids_exp, dados.experiencias):
        st.session_state[f"perfil_exp_empresa_{id_linha}"] = exp.empresa
        st.session_state[f"perfil_exp_cargo_{id_linha}"] = exp.cargo
        st.session_state[f"perfil_exp_periodo_{id_linha}"] = exp.periodo
        st.session_state[f"perfil_exp_descricao_{id_linha}"] = exp.descricao

    ids_form = [str(uuid.uuid4()) for _ in dados.formacoes]
    st.session_state["perfil_form_ids"] = ids_form
    for id_linha, formacao in zip(ids_form, dados.formacoes):
        st.session_state[f"perfil_form_instituicao_{id_linha}"] = formacao.instituicao
        st.session_state[f"perfil_form_curso_{id_linha}"] = formacao.curso
        st.session_state[f"perfil_form_periodo_{id_linha}"] = formacao.periodo

    ids_cert = [str(uuid.uuid4()) for _ in dados.certificacoes]
    st.session_state["perfil_cert_ids"] = ids_cert
    for id_linha, cert in zip(ids_cert, dados.certificacoes):
        st.session_state[f"perfil_cert_nome_{id_linha}"] = cert.nome
        st.session_state[f"perfil_cert_instituicao_{id_linha}"] = cert.instituicao
        st.session_state[f"perfil_cert_ano_{id_linha}"] = cert.ano

    ids_idioma = [str(uuid.uuid4()) for _ in dados.idiomas]
    st.session_state["perfil_idioma_ids"] = ids_idioma
    for id_linha, idioma in zip(ids_idioma, dados.idiomas):
        st.session_state[f"perfil_idioma_nome_{id_linha}"] = idioma.idioma
        st.session_state[f"perfil_idioma_nivel_{id_linha}"] = _ROTULO_NIVEL_IDIOMA[idioma.nivel]


def _renderizar_lista_experiencias() -> None:
    ids = _ids_lista("perfil_exp_ids")
    for id_linha in list(ids):
        with st.container(border=True):
            col_empresa, col_cargo, col_periodo, col_remover = st.columns([3, 3, 2, 1])
            with col_empresa:
                st.text_input("Empresa", key=f"perfil_exp_empresa_{id_linha}")
            with col_cargo:
                st.text_input("Cargo", key=f"perfil_exp_cargo_{id_linha}")
            with col_periodo:
                st.text_input(
                    "Período", key=f"perfil_exp_periodo_{id_linha}", placeholder="Ex: 2020 - Atual"
                )
            with col_remover:
                st.write("")
                if st.button("Remover", key=f"perfil_exp_remover_{id_linha}"):
                    ids.remove(id_linha)
                    st.rerun()
            st.text_area("Descrição", key=f"perfil_exp_descricao_{id_linha}", height=80)
    if st.button("Adicionar experiência", key="perfil_exp_adicionar"):
        ids.append(str(uuid.uuid4()))
        st.rerun()


def _coletar_experiencias() -> tuple[ExperienciaProfissional, ...]:
    experiencias = []
    for id_linha in _ids_lista("perfil_exp_ids"):
        empresa = st.session_state.get(f"perfil_exp_empresa_{id_linha}", "").strip()
        cargo = st.session_state.get(f"perfil_exp_cargo_{id_linha}", "").strip()
        if not empresa or not cargo:
            continue
        experiencias.append(
            ExperienciaProfissional(
                empresa=empresa,
                cargo=cargo,
                periodo=st.session_state.get(f"perfil_exp_periodo_{id_linha}", "").strip(),
                descricao=st.session_state.get(f"perfil_exp_descricao_{id_linha}", "").strip(),
            )
        )
    return tuple(experiencias)


def _renderizar_lista_formacoes() -> None:
    ids = _ids_lista("perfil_form_ids")
    for id_linha in list(ids):
        with st.container(border=True):
            col_instituicao, col_curso, col_periodo, col_remover = st.columns([3, 3, 2, 1])
            with col_instituicao:
                st.text_input("Instituição", key=f"perfil_form_instituicao_{id_linha}")
            with col_curso:
                st.text_input("Curso", key=f"perfil_form_curso_{id_linha}")
            with col_periodo:
                st.text_input("Período", key=f"perfil_form_periodo_{id_linha}")
            with col_remover:
                st.write("")
                if st.button("Remover", key=f"perfil_form_remover_{id_linha}"):
                    ids.remove(id_linha)
                    st.rerun()
    if st.button("Adicionar formação", key="perfil_form_adicionar"):
        ids.append(str(uuid.uuid4()))
        st.rerun()


def _coletar_formacoes() -> tuple[FormacaoAcademica, ...]:
    formacoes = []
    for id_linha in _ids_lista("perfil_form_ids"):
        instituicao = st.session_state.get(f"perfil_form_instituicao_{id_linha}", "").strip()
        curso = st.session_state.get(f"perfil_form_curso_{id_linha}", "").strip()
        if not instituicao or not curso:
            continue
        formacoes.append(
            FormacaoAcademica(
                instituicao=instituicao,
                curso=curso,
                periodo=st.session_state.get(f"perfil_form_periodo_{id_linha}", "").strip(),
            )
        )
    return tuple(formacoes)


def _renderizar_lista_certificacoes() -> None:
    ids = _ids_lista("perfil_cert_ids")
    for id_linha in list(ids):
        with st.container(border=True):
            col_nome, col_instituicao, col_ano, col_remover = st.columns([3, 3, 2, 1])
            with col_nome:
                st.text_input("Nome", key=f"perfil_cert_nome_{id_linha}")
            with col_instituicao:
                st.text_input("Instituição", key=f"perfil_cert_instituicao_{id_linha}")
            with col_ano:
                st.text_input("Ano", key=f"perfil_cert_ano_{id_linha}")
            with col_remover:
                st.write("")
                if st.button("Remover", key=f"perfil_cert_remover_{id_linha}"):
                    ids.remove(id_linha)
                    st.rerun()
    if st.button("Adicionar certificação", key="perfil_cert_adicionar"):
        ids.append(str(uuid.uuid4()))
        st.rerun()


def _coletar_certificacoes() -> tuple[Certificacao, ...]:
    certificacoes = []
    for id_linha in _ids_lista("perfil_cert_ids"):
        nome = st.session_state.get(f"perfil_cert_nome_{id_linha}", "").strip()
        if not nome:
            continue
        certificacoes.append(
            Certificacao(
                nome=nome,
                instituicao=st.session_state.get(f"perfil_cert_instituicao_{id_linha}", "").strip(),
                ano=st.session_state.get(f"perfil_cert_ano_{id_linha}", "").strip(),
            )
        )
    return tuple(certificacoes)


def _renderizar_lista_idiomas() -> None:
    ids = _ids_lista("perfil_idioma_ids")
    for id_linha in list(ids):
        with st.container(border=True):
            col_idioma, col_nivel, col_remover = st.columns([3, 2, 1])
            with col_idioma:
                st.text_input("Idioma", key=f"perfil_idioma_nome_{id_linha}")
            with col_nivel:
                st.selectbox(
                    "Nível",
                    list(_ROTULO_NIVEL_IDIOMA.values()),
                    key=f"perfil_idioma_nivel_{id_linha}",
                )
            with col_remover:
                st.write("")
                if st.button("Remover", key=f"perfil_idioma_remover_{id_linha}"):
                    ids.remove(id_linha)
                    st.rerun()
    if st.button("Adicionar idioma", key="perfil_idioma_adicionar"):
        ids.append(str(uuid.uuid4()))
        st.rerun()


def _coletar_idiomas() -> tuple[Idioma, ...]:
    idiomas = []
    for id_linha in _ids_lista("perfil_idioma_ids"):
        nome_idioma = st.session_state.get(f"perfil_idioma_nome_{id_linha}", "").strip()
        if not nome_idioma:
            continue
        rotulo_nivel = st.session_state.get(f"perfil_idioma_nivel_{id_linha}", "Intermediário")
        idiomas.append(
            Idioma(idioma=nome_idioma, nivel=_NIVEL_IDIOMA_POR_ROTULO.get(rotulo_nivel, NivelIdioma.INTERMEDIARIO))
        )
    return tuple(idiomas)


def _pagina_meu_perfil(
    repositorio_perfil_estruturado: PerfilEstruturadoRepositoryImpl,
    repositorio_curriculo_salvo: CurriculoSalvoRepositoryImpl,
    perfil_identificador: str,
) -> None:
    st.title("Meu Perfil")
    st.caption(
        "Preencha seu currículo diretamente aqui, como já faz no LinkedIn ou na Gupy — sem "
        "precisar fazer upload de PDF toda vez que for adaptar seu currículo, analisar ATS "
        "ou se candidatar a uma vaga descoberta."
    )

    if "perfil_carregado" not in st.session_state:
        perfil_existente = BuscarPerfilEstruturado(repositorio=repositorio_perfil_estruturado).executar(
            perfil_identificador
        )
        if perfil_existente is not None:
            _carregar_dados_no_estado(perfil_existente)
        st.session_state["perfil_carregado"] = True

    with st.expander("Importar de um PDF (opcional)"):
        st.caption(
            "Pré-preenche os campos abaixo a partir de um currículo em PDF — pode ser um "
            "currículo já salvo na biblioteca, ou um export \"Salvar como PDF\" do seu "
            "próprio perfil do LinkedIn. Os campos continuam editáveis antes de salvar."
        )
        curriculos_salvos = ListarCurriculosSalvos(
            repositorio_curriculo_salvo=repositorio_curriculo_salvo
        ).executar(perfil_identificador)

        pdf_para_importar: bytes | None = None
        if curriculos_salvos:
            opcoes = {c.nome_referencia: c for c in curriculos_salvos}
            nome_escolhido = st.selectbox(
                "Usar um currículo da biblioteca",
                ["Nenhum — enviar novo PDF abaixo"] + list(opcoes.keys()),
                key="perfil_import_biblioteca",
            )
            if nome_escolhido != "Nenhum — enviar novo PDF abaixo":
                pdf_para_importar = opcoes[nome_escolhido].pdf_bytes

        if pdf_para_importar is None:
            arquivo = st.file_uploader("PDF do currículo", type=["pdf"], key="perfil_import_upload")
            if arquivo is not None:
                pdf_para_importar = arquivo.read()

        if st.button("Importar e pré-preencher") and pdf_para_importar is not None:
            try:
                with st.spinner("Extraindo dados do PDF..."):
                    dados = _montar_importar_perfil_de_pdf().executar(
                        ImportarPerfilDePdfInputDto(pdf_curriculo=pdf_para_importar)
                    )
                _carregar_dados_no_estado(dados)
                st.success("Dados importados! Revise os campos abaixo antes de salvar.")
                st.rerun()
            except ValueError as erro:
                st.error(str(erro))
            except Exception as erro:  # noqa: BLE001 - fronteira de UI
                st.error(f"Ocorreu um erro inesperado ao importar o PDF: {erro}")

    st.subheader("Dados pessoais")
    nome_completo = st.text_input("Nome completo", key="perfil_nome_completo")
    col_email, col_linkedin = st.columns(2)
    with col_email:
        email = st.text_input("Email", key="perfil_email")
    with col_linkedin:
        linkedin = st.text_input("LinkedIn (URL)", key="perfil_linkedin")
    resumo_profissional = st.text_area("Resumo profissional", key="perfil_resumo", height=120)

    st.subheader("Experiências profissionais")
    _renderizar_lista_experiencias()

    st.subheader("Formação acadêmica")
    _renderizar_lista_formacoes()

    st.subheader("Certificações")
    _renderizar_lista_certificacoes()

    st.subheader("Idiomas")
    _renderizar_lista_idiomas()

    st.subheader("Tecnologias")
    tecnologias_texto = st.text_input("Tecnologias (separadas por vírgula)", key="perfil_tecnologias_texto")

    if st.button("Salvar perfil", type="primary"):
        try:
            input_dto = SalvarPerfilEstruturadoInputDto(
                perfil_identificador=perfil_identificador,
                nome_completo=nome_completo,
                email=email,
                linkedin=linkedin,
                resumo_profissional=resumo_profissional,
                experiencias=_coletar_experiencias(),
                formacoes=_coletar_formacoes(),
                certificacoes=_coletar_certificacoes(),
                idiomas=_coletar_idiomas(),
                tecnologias=tuple(t.strip() for t in tecnologias_texto.split(",") if t.strip()),
            )
            SalvarPerfilEstruturado(repositorio=repositorio_perfil_estruturado).executar(input_dto)
            st.success("Perfil salvo com sucesso!")
        except ValueError as erro:
            st.error(str(erro))
        except Exception as erro:  # noqa: BLE001 - fronteira de UI
            st.error(f"Ocorreu um erro inesperado ao salvar o perfil: {erro}")


# --- Página: Adaptar Currículo -----------------------------------------------

def _renderizar_biblioteca_curriculos(
    repositorio_curriculo_salvo: CurriculoSalvoRepositoryImpl, perfil_identificador: str
) -> tuple[bytes | None, str | None]:
    """Renderiza upload + lista da biblioteca. Retorna (pdf_bytes, nome_referencia) do currículo selecionado."""
    st.subheader("Biblioteca de Currículos")

    listar_use_case = ListarCurriculosSalvos(repositorio_curriculo_salvo=repositorio_curriculo_salvo)
    curriculos_salvos = listar_use_case.executar(perfil_identificador)

    curriculo_selecionado: CurriculoSalvo | None = None
    if curriculos_salvos:
        opcoes = {c.nome_referencia: c for c in curriculos_salvos}
        nome_escolhido = st.selectbox(
            "Usar um currículo já salvo (opcional)",
            ["Nenhum — enviar novo PDF abaixo"] + list(opcoes.keys()),
        )
        if nome_escolhido != "Nenhum — enviar novo PDF abaixo":
            curriculo_selecionado = opcoes[nome_escolhido]
            if st.button(f"Remover '{nome_escolhido}' da biblioteca"):
                remover_use_case = RemoverCurriculoSalvo(repositorio_curriculo_salvo=repositorio_curriculo_salvo)
                try:
                    remover_use_case.executar(curriculo_selecionado.id, perfil_identificador)
                    st.success("Currículo removido da biblioteca.")
                    st.rerun()
                except CurriculoSalvoNaoEncontrado as erro:
                    st.error(str(erro))

    with st.expander("Salvar um novo currículo na biblioteca"):
        novo_pdf = st.file_uploader("PDF do currículo", type=["pdf"], key="upload_biblioteca")
        nome_referencia = st.text_input(
            "Nome de referência", placeholder="Ex: Currículo Backend Sênior", key="nome_referencia_biblioteca"
        )
        if st.button("Salvar na biblioteca") and novo_pdf is not None and nome_referencia.strip():
            salvar_use_case = SalvarCurriculo(repositorio_curriculo_salvo=repositorio_curriculo_salvo)
            try:
                salvar_use_case.executar(
                    SalvarCurriculoInputDto(
                        perfil_identificador=perfil_identificador,
                        nome_referencia=nome_referencia.strip(),
                        pdf_bytes=novo_pdf.read(),
                    )
                )
                st.success("Currículo salvo na biblioteca.")
                st.rerun()
            except LimiteCurriculosSalvosExcedido as erro:
                st.error(str(erro))

    if curriculo_selecionado is not None:
        return curriculo_selecionado.pdf_bytes, curriculo_selecionado.nome_referencia
    return None, None


def _renderizar_formulario(
    pdf_pre_selecionado: bytes | None, pular_upload: bool = False
) -> tuple[bytes | None, str, str, str, str]:
    conteudo_pdf: bytes | None = None
    if not pular_upload:
        if pdf_pre_selecionado is not None:
            st.caption("Usando currículo selecionado da biblioteca acima.")
            conteudo_pdf = pdf_pre_selecionado
        else:
            arquivo_pdf = st.file_uploader("Currículo em PDF", type=["pdf"], key="upload_adaptacao")
            conteudo_pdf = arquivo_pdf.read() if arquivo_pdf is not None else None

    descricao_vaga = st.text_area(
        "Descrição da vaga",
        height=200,
        placeholder="Cole aqui o texto completo da descrição da vaga...",
    )

    col_idioma, col_cargo, col_empresa = st.columns(3)
    with col_idioma:
        idioma_label = st.selectbox("Idioma de saída", ["Português", "Inglês"])
    with col_cargo:
        cargo_alvo = st.text_input("Cargo da vaga", placeholder="Ex: Engenheiro de Software Sênior")
    with col_empresa:
        empresa_alvo = st.text_input("Empresa", placeholder="Ex: TechCorp")

    idioma_alvo = "pt" if idioma_label == "Português" else "en"
    return conteudo_pdf, descricao_vaga, idioma_alvo, cargo_alvo, empresa_alvo


def _validar_formulario(
    conteudo_pdf: bytes | None,
    descricao_vaga: str,
    cargo_alvo: str,
    empresa_alvo: str,
    tem_curriculo_do_perfil: bool = False,
) -> str | None:
    if conteudo_pdf is None and not tem_curriculo_do_perfil:
        return "Anexe um arquivo PDF do currículo ou selecione um da biblioteca."
    if not descricao_vaga or not descricao_vaga.strip():
        return "Informe a descrição da vaga."
    if not cargo_alvo or not cargo_alvo.strip():
        return "Informe o cargo da vaga."
    if not empresa_alvo or not empresa_alvo.strip():
        return "Informe o nome da empresa."
    return None


def _pagina_adaptar_curriculo(
    repositorio_curriculo_salvo: CurriculoSalvoRepositoryImpl,
    repositorio_perfil_estruturado: PerfilEstruturadoRepositoryImpl,
    perfil_identificador: str,
) -> None:
    st.title("Adaptador de Currículo para Vagas")
    st.caption(
        "Anexe seu currículo em PDF, cole a descrição da vaga e gere uma versão "
        "adaptada, seção por seção, no idioma desejado."
    )

    curriculo_do_perfil = _obter_curriculo_do_perfil(repositorio_perfil_estruturado, perfil_identificador)

    if curriculo_do_perfil is not None:
        st.caption("Usando os dados do seu perfil salvo (página 'Meu Perfil').")
        pdf_biblioteca = None
    else:
        pdf_biblioteca, _ = _renderizar_biblioteca_curriculos(repositorio_curriculo_salvo, perfil_identificador)

    conteudo_pdf, descricao_vaga, idioma_alvo, cargo_alvo, empresa_alvo = _renderizar_formulario(
        pdf_biblioteca, pular_upload=curriculo_do_perfil is not None
    )

    if st.button("Gerar currículo adaptado", type="primary"):
        erro_validacao = _validar_formulario(
            conteudo_pdf, descricao_vaga, cargo_alvo, empresa_alvo, tem_curriculo_do_perfil=curriculo_do_perfil is not None
        )
        if erro_validacao:
            st.error(erro_validacao)
            return

        try:
            with st.spinner("Analisando currículo e adaptando cada seção para a vaga..."):
                caso_de_uso = _montar_caso_de_uso()
                input_dto = AdaptarCurriculoParaVagaInputDto(
                    pdf_curriculo=conteudo_pdf,
                    curriculo_pre_montado=curriculo_do_perfil,
                    descricao_vaga=descricao_vaga,
                    idioma_alvo=idioma_alvo,
                    cargo_alvo=cargo_alvo,
                    empresa_alvo=empresa_alvo,
                    data_referencia=date.today(),
                )
                resultado = caso_de_uso.executar(input_dto)
                caminho_salvo = _salvar_no_armazenamento(resultado.nome_arquivo.valor, resultado.pdf_bytes)

            st.success(f"Currículo gerado e salvo em: {caminho_salvo}")
            st.download_button(
                label="Baixar PDF adaptado",
                data=resultado.pdf_bytes,
                file_name=resultado.nome_arquivo.valor,
                mime="application/pdf",
            )

            resultado_ats = CalcularAtsScore().executar(resultado.curriculo_adaptado, resultado.analise_vaga)
            st.metric("ATS Score", f"{resultado_ats.nota}/100")
            if resultado_ats.requisitos_faltantes:
                st.warning("Requisitos da vaga não encontrados no currículo adaptado:")
                for requisito in resultado_ats.requisitos_faltantes:
                    st.write(f"- {requisito.nome}")
            else:
                st.success("Todos os requisitos explícitos da vaga foram encontrados no currículo.")

            try:
                with st.spinner("Gerando carta de apresentação..."):
                    gerador_carta = _montar_gerador_carta_apresentacao()
                    carta = gerador_carta.executar(
                        resultado.curriculo_adaptado, resultado.analise_vaga, idioma_alvo
                    )
                nome_arquivo_carta = f"carta-apresentacao-{resultado.nome_arquivo.valor.replace('.pdf', '.txt')}"
                st.download_button(
                    label="Baixar carta de apresentação",
                    data=carta,
                    file_name=nome_arquivo_carta,
                    mime="text/plain",
                )
            except Exception as erro_carta:  # noqa: BLE001 - falha na carta não deve impedir o download do PDF
                st.warning(f"Não foi possível gerar a carta de apresentação agora: {erro_carta}")
        except ValueError as erro:
            st.error(str(erro))
        except Exception as erro:  # noqa: BLE001 - fronteira de UI: captura e exibe qualquer falha inesperada
            st.error(f"Ocorreu um erro inesperado ao processar o currículo: {erro}")


# --- Página: Analisar ATS ----------------------------------------------------

def _selecionar_descricao_vaga(repositorio_vaga: VagaRepositoryImpl, perfil_identificador: str) -> str:
    """Permite escolher entre colar a descrição ou usar uma vaga já capturada pela extensão."""
    listar_vagas_use_case = ListarVagasCapturadas(repositorio_vaga=repositorio_vaga)
    vagas_capturadas = listar_vagas_use_case.executar(perfil_identificador)

    if vagas_capturadas:
        opcoes = {f"{v.texto_descricao[:60].strip()}...": v for v in vagas_capturadas}
        escolha = st.selectbox(
            "Usar uma vaga capturada (opcional)",
            ["Nenhuma — colar descrição abaixo"] + list(opcoes.keys()),
        )
        if escolha != "Nenhuma — colar descrição abaixo":
            return opcoes[escolha].texto_descricao

    return st.text_area(
        "Descrição da vaga",
        height=200,
        placeholder="Cole aqui o texto completo da descrição da vaga...",
        key="descricao_vaga_ats",
    )


def _pagina_analisar_ats(
    repositorio_curriculo_salvo: CurriculoSalvoRepositoryImpl,
    repositorio_perfil_estruturado: PerfilEstruturadoRepositoryImpl,
    repositorio_vaga: VagaRepositoryImpl,
    perfil_identificador: str,
) -> None:
    st.title("Analisar ATS")
    st.caption(
        "Veja a aderência do seu currículo à vaga e o que mudar para aumentar a pontuação — "
        "sem gerar um currículo adaptado (mais rápido e barato que 'Adaptar Currículo')."
    )

    curriculo_do_perfil = _obter_curriculo_do_perfil(repositorio_perfil_estruturado, perfil_identificador)
    conteudo_pdf: bytes | None = None

    if curriculo_do_perfil is not None:
        st.caption("Usando os dados do seu perfil salvo (página 'Meu Perfil').")
    else:
        pdf_biblioteca, _ = _renderizar_biblioteca_curriculos(repositorio_curriculo_salvo, perfil_identificador)
        if pdf_biblioteca is not None:
            st.caption("Usando currículo selecionado da biblioteca acima.")
            conteudo_pdf = pdf_biblioteca
        else:
            arquivo_pdf = st.file_uploader("Currículo em PDF", type=["pdf"], key="upload_ats")
            conteudo_pdf = arquivo_pdf.read() if arquivo_pdf is not None else None

    descricao_vaga = _selecionar_descricao_vaga(repositorio_vaga, perfil_identificador)

    if st.button("Analisar ATS", type="primary"):
        if conteudo_pdf is None and curriculo_do_perfil is None:
            st.error("Anexe um currículo em PDF ou selecione um da biblioteca.")
            return
        if not descricao_vaga or not descricao_vaga.strip():
            st.error("Informe a descrição da vaga ou selecione uma vaga capturada.")
            return

        try:
            with st.spinner("Analisando aderência do currículo à vaga..."):
                use_case = _montar_analisar_ats_vaga()
                resultado = use_case.executar(
                    AnalisarAtsVagaInputDto(
                        pdf_curriculo=conteudo_pdf,
                        curriculo_pre_montado=curriculo_do_perfil,
                        descricao_vaga=descricao_vaga,
                    )
                )

            st.metric("ATS Score", f"{resultado.resultado_ats.nota}/100")
            if resultado.resultado_ats.requisitos_faltantes:
                st.warning("Requisitos da vaga não encontrados no currículo:")
                for requisito in resultado.resultado_ats.requisitos_faltantes:
                    st.write(f"- {requisito.nome}")
            else:
                st.success("Todos os requisitos explícitos da vaga foram encontrados no currículo.")

            st.subheader("O que mudar para aumentar a pontuação")
            for sugestao in resultado.sugestoes:
                st.markdown(f"- {sugestao}")
        except ValueError as erro:
            st.error(str(erro))
        except Exception as erro:  # noqa: BLE001 - fronteira de UI: captura e exibe qualquer falha inesperada
            st.error(f"Ocorreu um erro inesperado ao analisar o currículo: {erro}")


# --- Página: Vagas (descoberta externa + candidatura em um clique) ----------

def _renderizar_vaga_descoberta(
    vaga_com_score: VagaComScore,
    pdf_curriculo: bytes,
    idioma_alvo: str,
    curriculo_do_perfil: Curriculo | None = None,
) -> None:
    vaga = vaga_com_score.vaga
    resultado_ats = vaga_com_score.resultado_score
    chave = f"{vaga.fonte.name}-{vaga.url}"

    with st.container(border=True):
        col_info, col_score = st.columns([4, 1])
        with col_info:
            st.write(f"**{vaga.titulo}**")
            st.caption(f"{vaga.empresa} · {vaga.fonte.name.replace('_', ' ').title()}")
            if vaga.data_publicacao is not None:
                st.caption(f"Publicada em {vaga.data_publicacao.strftime('%d/%m/%Y')}")
            else:
                st.caption("Data de publicação desconhecida")
            if vaga.descricao_incompleta:
                st.caption("⚠️ Descrição incompleta (apenas trecho disponível desta fonte)")
        with col_score:
            st.metric("Match", f"{resultado_ats.nota}/100")

        with st.expander("Ver requisitos"):
            if resultado_ats.requisitos_faltantes:
                st.write("Requisitos não encontrados no currículo:")
                for requisito in resultado_ats.requisitos_faltantes:
                    st.write(f"- {requisito.nome}")
            else:
                st.write("Todos os requisitos explícitos foram encontrados no currículo.")

        if st.button("Candidatar", key=f"candidatar_{chave}"):
            try:
                with st.spinner("Adaptando currículo, calculando ATS e gerando carta de apresentação..."):
                    use_case = _montar_candidatar_na_vaga_externa()
                    resultado_candidatura = use_case.executar(
                        CandidatarNaVagaExternaInputDto(
                            pdf_curriculo=pdf_curriculo,
                            curriculo_pre_montado=curriculo_do_perfil,
                            vaga=vaga,
                            idioma_alvo=idioma_alvo,
                            cargo_alvo=vaga.titulo,
                            empresa_alvo=vaga.empresa,
                            data_referencia=date.today(),
                        )
                    )
                st.session_state[f"candidatura_{chave}"] = resultado_candidatura
            except ValueError as erro:
                st.error(str(erro))
            except Exception as erro:  # noqa: BLE001 - fronteira de UI: captura e exibe qualquer falha inesperada
                st.error(f"Ocorreu um erro inesperado ao candidatar: {erro}")

        resultado_candidatura = st.session_state.get(f"candidatura_{chave}")
        if resultado_candidatura is not None:
            st.success("Currículo adaptado e carta de apresentação prontos!")
            st.metric("ATS Score (currículo adaptado)", f"{resultado_candidatura.resultado_ats.nota}/100")
            st.download_button(
                "Baixar PDF adaptado",
                data=resultado_candidatura.pdf_bytes,
                file_name=resultado_candidatura.nome_arquivo.valor,
                mime="application/pdf",
                key=f"download_pdf_{chave}",
            )
            nome_arquivo_carta = (
                f"carta-apresentacao-{resultado_candidatura.nome_arquivo.valor.replace('.pdf', '.txt')}"
            )
            st.download_button(
                "Baixar carta de apresentação",
                data=resultado_candidatura.carta_apresentacao,
                file_name=nome_arquivo_carta,
                mime="text/plain",
                key=f"download_carta_{chave}",
            )
            st.link_button("Abrir vaga original para se candidatar", resultado_candidatura.url_vaga)


def _pagina_vagas(
    repositorio_curriculo_salvo: CurriculoSalvoRepositoryImpl,
    repositorio_perfil_estruturado: PerfilEstruturadoRepositoryImpl,
    perfil_identificador: str,
) -> None:
    st.title("Vagas")
    st.caption(
        "Busque vagas em fontes externas (RemoteOK, We Work Remotely, Arbeitnow, Adzuna, "
        "Google Custom Search) e veja a aderência ao seu currículo salvo. O botão "
        "'Candidatar' adapta o currículo e gera a carta de apresentação para a vaga em um "
        "clique, e abre a página original para você aplicar — sem preenchimento automático "
        "de formulários de terceiros."
    )

    listar_curriculos_use_case = ListarCurriculosSalvos(repositorio_curriculo_salvo=repositorio_curriculo_salvo)
    curriculos_salvos = listar_curriculos_use_case.executar(perfil_identificador)

    if not curriculos_salvos:
        st.warning("Salve um currículo na página 'Adaptar Currículo' para poder buscar vagas com match.")
        return

    col_termo, col_curriculo, col_idioma, col_periodo = st.columns([3, 2, 2, 2])
    with col_termo:
        termo = st.text_input("Termo de busca", placeholder="Ex: engenheiro de software backend")
    with col_curriculo:
        nome_curriculo_escolhido = st.selectbox(
            "Currículo de referência", [c.nome_referencia for c in curriculos_salvos]
        )
    with col_idioma:
        idioma_label = st.selectbox("Idioma da candidatura", ["Português", "Inglês"])
    with col_periodo:
        periodo_label = st.selectbox(
            "Publicada nos últimos", ["Qualquer período", "7 dias", "15 dias", "30 dias"]
        )
    idioma_alvo = "pt" if idioma_label == "Português" else "en"
    dias_maximo = {"Qualquer período": None, "7 dias": 7, "15 dias": 15, "30 dias": 30}[periodo_label]

    if st.button("Buscar vagas", type="primary"):
        if not termo.strip():
            st.error("Informe um termo de busca.")
            return

        curriculo_escolhido = next(
            c for c in curriculos_salvos if c.nome_referencia == nome_curriculo_escolhido
        )
        try:
            with st.spinner("Buscando vagas nas fontes externas..."):
                use_case = _montar_descobrir_vagas_com_match()
                resultado = use_case.executar(termo.strip(), curriculo_escolhido.pdf_bytes, dias_maximo)
            st.session_state["vagas_descobertas"] = resultado
            st.session_state["curriculo_vagas_pdf"] = curriculo_escolhido.pdf_bytes
        except ValueError as erro:
            st.error(str(erro))
            return
        except Exception as erro:  # noqa: BLE001 - fronteira de UI: captura e exibe qualquer falha inesperada
            st.error(f"Ocorreu um erro inesperado ao buscar vagas: {erro}")
            return

    vagas_descobertas: tuple[VagaComScore, ...] = st.session_state.get("vagas_descobertas", ())
    if not vagas_descobertas:
        return

    curriculo_do_perfil = _obter_curriculo_do_perfil(repositorio_perfil_estruturado, perfil_identificador)
    if curriculo_do_perfil is not None:
        st.caption("Candidatar-se vai usar os dados do seu perfil salvo (página 'Meu Perfil').")

    st.subheader(f"{len(vagas_descobertas)} vagas encontradas")
    for vaga_com_score in vagas_descobertas:
        _renderizar_vaga_descoberta(
            vaga_com_score,
            st.session_state["curriculo_vagas_pdf"],
            idioma_alvo,
            curriculo_do_perfil=curriculo_do_perfil,
        )


# --- Página: Vagas & Candidaturas --------------------------------------------

def _renderizar_token_captura(repositorio_token: TokenCapturaRepositoryImpl, perfil_identificador: str) -> None:
    with st.expander("Token de captura (extensão de navegador)"):
        st.caption(
            "Gere um token e cole-o no popup da extensão Chrome (`extensao-chrome/`) para "
            "capturar vagas diretamente das páginas que você visita, sem copiar e colar."
        )
        if st.button("Gerar novo token de captura"):
            token = repositorio_token.criar(perfil_identificador)
            st.session_state["ultimo_token_captura"] = token.token
        if "ultimo_token_captura" in st.session_state:
            st.code(st.session_state["ultimo_token_captura"])


def _renderizar_vagas_capturadas(
    repositorio_vaga: VagaRepositoryImpl,
    repositorio_candidatura: CandidaturaRepositoryImpl,
    curriculos_salvos: tuple[CurriculoSalvo, ...],
    perfil_identificador: str,
) -> None:
    st.subheader("Vagas capturadas")

    with st.expander("Colar uma vaga manualmente"):
        texto_manual = st.text_area("Descrição da vaga", key="vaga_manual_texto")
        if st.button("Registrar vaga colada") and texto_manual.strip():
            capturar_use_case = CapturarVaga(repositorio_vaga=repositorio_vaga)
            capturar_use_case.executar(
                CapturarVagaInputDto(
                    perfil_identificador=perfil_identificador, texto_descricao=texto_manual.strip()
                )
            )
            st.success("Vaga registrada.")
            st.rerun()

    listar_vagas_use_case = ListarVagasCapturadas(repositorio_vaga=repositorio_vaga)
    vagas_capturadas = listar_vagas_use_case.executar(perfil_identificador)

    if not vagas_capturadas:
        st.caption("Nenhuma vaga capturada pendente.")
        return

    for vaga in vagas_capturadas:
        with st.container(border=True):
            texto_truncado = len(vaga.texto_descricao) > 300
            resumo = vaga.texto_descricao[:300] + ("..." if texto_truncado else "")
            st.write(resumo)
            if texto_truncado:
                with st.expander("Ver descrição completa"):
                    st.write(vaga.texto_descricao)
            if vaga.url_origem:
                st.caption(vaga.url_origem)

            if not curriculos_salvos:
                st.caption(
                    "Salve um currículo na página 'Adaptar Currículo' para poder criar uma candidatura."
                )
                continue

            col_curriculo, col_empresa, col_cargo, col_botao = st.columns([2, 2, 2, 1])
            with col_curriculo:
                nome_curriculo_escolhido = st.selectbox(
                    "Currículo",
                    [c.nome_referencia for c in curriculos_salvos],
                    key=f"curriculo_{vaga.id}",
                )
            with col_empresa:
                empresa = st.text_input("Empresa", key=f"empresa_{vaga.id}")
            with col_cargo:
                cargo = st.text_input("Cargo", key=f"cargo_{vaga.id}")
            with col_botao:
                st.write("")
                if st.button("Criar candidatura", key=f"criar_candidatura_{vaga.id}"):
                    if empresa.strip() and cargo.strip():
                        curriculo_escolhido = next(
                            c for c in curriculos_salvos if c.nome_referencia == nome_curriculo_escolhido
                        )
                        criar_use_case = CriarCandidatura(
                            repositorio_candidatura=repositorio_candidatura,
                            repositorio_vaga=repositorio_vaga,
                        )
                        criar_use_case.executar(
                            CriarCandidaturaInputDto(
                                perfil_identificador=perfil_identificador,
                                vaga_id=vaga.id,
                                curriculo_salvo_id=curriculo_escolhido.id,
                                empresa=empresa.strip(),
                                cargo=cargo.strip(),
                            )
                        )
                        st.success("Candidatura criada!")
                        st.rerun()
                    else:
                        st.error("Informe empresa e cargo.")


def _renderizar_kanban(repositorio_candidatura: CandidaturaRepositoryImpl, perfil_identificador: str) -> None:
    st.subheader("Kanban de candidaturas")

    listar_use_case = ListarCandidaturasPorStatus(repositorio_candidatura=repositorio_candidatura)
    candidaturas_por_status = listar_use_case.executar(perfil_identificador)

    labels_status = [_LABEL_STATUS[status] for status in _ORDEM_STATUS]
    colunas = st.columns(len(_ORDEM_STATUS))
    for coluna, status in zip(colunas, _ORDEM_STATUS):
        with coluna:
            candidaturas = candidaturas_por_status[status]
            st.markdown(f"**{_LABEL_STATUS[status]}** ({len(candidaturas)})")
            for candidatura in candidaturas:
                with st.container(border=True):
                    st.write(f"**{candidatura.cargo}**")
                    st.caption(candidatura.empresa)
                    novo_status_label = st.selectbox(
                        "Mover para",
                        labels_status,
                        index=_ORDEM_STATUS.index(status),
                        key=f"mover_{candidatura.id}",
                        label_visibility="collapsed",
                    )
                    novo_status = _ORDEM_STATUS[labels_status.index(novo_status_label)]
                    if novo_status != status:
                        mover_use_case = MoverCandidatura(repositorio_candidatura=repositorio_candidatura)
                        mover_use_case.executar(candidatura.id, novo_status)
                        st.rerun()


def _pagina_vagas_e_candidaturas(
    repositorio_curriculo_salvo: CurriculoSalvoRepositoryImpl,
    repositorio_token: TokenCapturaRepositoryImpl,
    repositorio_vaga: VagaRepositoryImpl,
    repositorio_candidatura: CandidaturaRepositoryImpl,
    perfil_identificador: str,
) -> None:
    st.title("Vagas & Candidaturas")

    _renderizar_token_captura(repositorio_token, perfil_identificador)

    listar_curriculos_use_case = ListarCurriculosSalvos(repositorio_curriculo_salvo=repositorio_curriculo_salvo)
    curriculos_salvos = listar_curriculos_use_case.executar(perfil_identificador)

    _renderizar_vagas_capturadas(
        repositorio_vaga, repositorio_candidatura, curriculos_salvos, perfil_identificador
    )
    _renderizar_kanban(repositorio_candidatura, perfil_identificador)


# --- Entry point --------------------------------------------------------------

def main() -> None:
    st.set_page_config(page_title="job-sync", page_icon="📄", layout="wide")
    _carregar_secrets_para_env()
    _injetar_estilo_shadcn()

    repositorio_perfil = _montar_repositorio_perfil()

    if "perfil_identificador" not in st.session_state:
        _renderizar_tela_de_entrada(repositorio_perfil)
        return

    perfil_identificador = st.session_state["perfil_identificador"]
    repositorio_curriculo_salvo = _montar_repositorio_curriculo_salvo()

    with st.sidebar:
        st.caption(f"Perfil: **{perfil_identificador}**")
        pagina = st.radio(
            "Navegação",
            [
                _PAGINA_MEU_PERFIL,
                _PAGINA_ADAPTAR_CURRICULO,
                _PAGINA_ANALISAR_ATS,
                _PAGINA_VAGAS,
                _PAGINA_VAGAS_E_CANDIDATURAS,
            ],
            label_visibility="collapsed",
        )
        if st.button("Sair"):
            for chave in [k for k in st.session_state if k.startswith("perfil_")]:
                del st.session_state[chave]
            st.rerun()

    repositorio_perfil_estruturado = _montar_repositorio_perfil_estruturado()

    if pagina == _PAGINA_MEU_PERFIL:
        _pagina_meu_perfil(repositorio_perfil_estruturado, repositorio_curriculo_salvo, perfil_identificador)
    elif pagina == _PAGINA_ADAPTAR_CURRICULO:
        _pagina_adaptar_curriculo(repositorio_curriculo_salvo, repositorio_perfil_estruturado, perfil_identificador)
    elif pagina == _PAGINA_ANALISAR_ATS:
        repositorio_vaga = _montar_repositorio_vaga()
        _pagina_analisar_ats(
            repositorio_curriculo_salvo, repositorio_perfil_estruturado, repositorio_vaga, perfil_identificador
        )
    elif pagina == _PAGINA_VAGAS:
        _pagina_vagas(repositorio_curriculo_salvo, repositorio_perfil_estruturado, perfil_identificador)
    else:
        repositorio_token = _montar_repositorio_token_captura()
        repositorio_vaga = _montar_repositorio_vaga()
        repositorio_candidatura = _montar_repositorio_candidatura()
        _pagina_vagas_e_candidaturas(
            repositorio_curriculo_salvo,
            repositorio_token,
            repositorio_vaga,
            repositorio_candidatura,
            perfil_identificador,
        )


if __name__ == "__main__":
    main()
