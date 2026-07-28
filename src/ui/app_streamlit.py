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
from application.use_cases.capturar_vaga import CapturarVaga, CapturarVagaInputDto
from application.use_cases.criar_candidatura import CriarCandidatura, CriarCandidaturaInputDto
from application.use_cases.entrar_ou_criar_perfil import EntrarOuCriarPerfil
from application.use_cases.gerar_carta_apresentacao import GerarCartaApresentacao
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
from domain.ats_score.calcular_ats_score_service import CalcularAtsScore
from domain.candidatura import StatusCandidatura
from domain.curriculo_salvo import CurriculoSalvo
from infrastructure.extractors.extrator_curriculo_segmentado_ia import (
    ExtratorCurriculoSegmentadoPorIA,
)
from infrastructure.llm.ajustador_texto_groq import AjustadorTextoGroq
from infrastructure.llm.cliente_groq import ClienteGroq
from infrastructure.llm.gerador_carta_apresentacao_groq import GeradorCartaApresentacaoGroq
from infrastructure.llm.gerador_sugestoes_ats_groq import GeradorSugestoesAtsGroq
from infrastructure.llm.job_description_analyzer_groq import JobDescriptionAnalyzerGroq
from infrastructure.pdf.gerador_pdf_reportlab import GeradorPdfReportLab
from infrastructure.persistence.candidatura_repository_impl import CandidaturaRepositoryImpl
from infrastructure.persistence.curriculo_salvo_repository_impl import CurriculoSalvoRepositoryImpl
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

_PAGINA_ADAPTAR_CURRICULO = "Adaptar Currículo"
_PAGINA_ANALISAR_ATS = "Analisar ATS"
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


def _renderizar_formulario(pdf_pre_selecionado: bytes | None) -> tuple[bytes | None, str, str, str, str]:
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
    conteudo_pdf: bytes | None, descricao_vaga: str, cargo_alvo: str, empresa_alvo: str
) -> str | None:
    if conteudo_pdf is None:
        return "Anexe um arquivo PDF do currículo ou selecione um da biblioteca."
    if not descricao_vaga or not descricao_vaga.strip():
        return "Informe a descrição da vaga."
    if not cargo_alvo or not cargo_alvo.strip():
        return "Informe o cargo da vaga."
    if not empresa_alvo or not empresa_alvo.strip():
        return "Informe o nome da empresa."
    return None


def _pagina_adaptar_curriculo(
    repositorio_curriculo_salvo: CurriculoSalvoRepositoryImpl, perfil_identificador: str
) -> None:
    st.title("Adaptador de Currículo para Vagas")
    st.caption(
        "Anexe seu currículo em PDF, cole a descrição da vaga e gere uma versão "
        "adaptada, seção por seção, no idioma desejado."
    )

    pdf_biblioteca, _ = _renderizar_biblioteca_curriculos(repositorio_curriculo_salvo, perfil_identificador)

    conteudo_pdf, descricao_vaga, idioma_alvo, cargo_alvo, empresa_alvo = _renderizar_formulario(
        pdf_biblioteca
    )

    if st.button("Gerar currículo adaptado", type="primary"):
        erro_validacao = _validar_formulario(conteudo_pdf, descricao_vaga, cargo_alvo, empresa_alvo)
        if erro_validacao:
            st.error(erro_validacao)
            return

        try:
            with st.spinner("Analisando currículo e adaptando cada seção para a vaga..."):
                caso_de_uso = _montar_caso_de_uso()
                input_dto = AdaptarCurriculoParaVagaInputDto(
                    pdf_curriculo=conteudo_pdf,
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
    repositorio_vaga: VagaRepositoryImpl,
    perfil_identificador: str,
) -> None:
    st.title("Analisar ATS")
    st.caption(
        "Veja a aderência do seu currículo à vaga e o que mudar para aumentar a pontuação — "
        "sem gerar um currículo adaptado (mais rápido e barato que 'Adaptar Currículo')."
    )

    pdf_biblioteca, _ = _renderizar_biblioteca_curriculos(repositorio_curriculo_salvo, perfil_identificador)

    if pdf_biblioteca is not None:
        st.caption("Usando currículo selecionado da biblioteca acima.")
        conteudo_pdf = pdf_biblioteca
    else:
        arquivo_pdf = st.file_uploader("Currículo em PDF", type=["pdf"], key="upload_ats")
        conteudo_pdf = arquivo_pdf.read() if arquivo_pdf is not None else None

    descricao_vaga = _selecionar_descricao_vaga(repositorio_vaga, perfil_identificador)

    if st.button("Analisar ATS", type="primary"):
        if conteudo_pdf is None:
            st.error("Anexe um currículo em PDF ou selecione um da biblioteca.")
            return
        if not descricao_vaga or not descricao_vaga.strip():
            st.error("Informe a descrição da vaga ou selecione uma vaga capturada.")
            return

        try:
            with st.spinner("Analisando aderência do currículo à vaga..."):
                use_case = _montar_analisar_ats_vaga()
                resultado = use_case.executar(
                    AnalisarAtsVagaInputDto(pdf_curriculo=conteudo_pdf, descricao_vaga=descricao_vaga)
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
            [_PAGINA_ADAPTAR_CURRICULO, _PAGINA_ANALISAR_ATS, _PAGINA_VAGAS_E_CANDIDATURAS],
            label_visibility="collapsed",
        )
        if st.button("Sair"):
            del st.session_state["perfil_identificador"]
            st.rerun()

    if pagina == _PAGINA_ADAPTAR_CURRICULO:
        _pagina_adaptar_curriculo(repositorio_curriculo_salvo, perfil_identificador)
    elif pagina == _PAGINA_ANALISAR_ATS:
        repositorio_vaga = _montar_repositorio_vaga()
        _pagina_analisar_ats(repositorio_curriculo_salvo, repositorio_vaga, perfil_identificador)
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
