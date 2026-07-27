"""Interface web do MVP (Streamlit).

Responsabilidade única desta camada: coletar entrada do usuário, montar a
SolicitacaoAdaptacao, executar o caso de uso AdaptarCurriculoParaVaga e
apresentar o resultado. Toda a lógica de negócio vive nas camadas domain/
application; aqui só há orquestração de UI e composição de dependências
(Composition Root), conforme Hexagonal Architecture.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from application.use_cases.adaptar_curriculo_para_vaga import (
    AdaptarCurriculoParaVaga,
    SolicitacaoAdaptacao,
)
from infrastructure.extractors.extrator_curriculo_segmentado_ia import (
    ExtratorCurriculoSegmentadoPorIA,
)
from infrastructure.llm.ajustador_texto_groq import AjustadorTextoGroq
from infrastructure.llm.cliente_groq import ClienteGroq
from infrastructure.llm.job_description_analyzer_groq import JobDescriptionAnalyzerGroq
from infrastructure.pdf.gerador_pdf_reportlab import GeradorPdfReportLab

load_dotenv()

DIRETORIO_ARMAZENAMENTO = Path(__file__).resolve().parent.parent / "storage"
DIRETORIO_ARMAZENAMENTO.mkdir(exist_ok=True)


def _montar_caso_de_uso() -> AdaptarCurriculoParaVaga:
    """Composition Root: monta os adapters concretos e injeta nas portas do caso de uso."""
    cliente_groq = ClienteGroq()
    extrator = ExtratorCurriculoSegmentadoPorIA(cliente_groq=cliente_groq)
    analisador_vaga = JobDescriptionAnalyzerGroq(cliente_groq=cliente_groq)
    ajustador_texto = AjustadorTextoGroq(cliente_groq=cliente_groq)
    gerador_pdf = GeradorPdfReportLab()
    return AdaptarCurriculoParaVaga(extrator, analisador_vaga, ajustador_texto, gerador_pdf)


def _salvar_no_armazenamento(nome_arquivo: str, pdf_bytes: bytes) -> Path:
    caminho = DIRETORIO_ARMAZENAMENTO / nome_arquivo
    caminho.write_bytes(pdf_bytes)
    return caminho


def _renderizar_formulario() -> tuple[bytes | None, str, str, str, str]:
    arquivo_pdf = st.file_uploader("Currículo em PDF", type=["pdf"])
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
    conteudo_pdf = arquivo_pdf.read() if arquivo_pdf is not None else None
    return conteudo_pdf, descricao_vaga, idioma_alvo, cargo_alvo, empresa_alvo


def _validar_formulario(
    conteudo_pdf: bytes | None, descricao_vaga: str, cargo_alvo: str, empresa_alvo: str
) -> str | None:
    if conteudo_pdf is None:
        return "Anexe um arquivo PDF do currículo."
    if not descricao_vaga or not descricao_vaga.strip():
        return "Informe a descrição da vaga."
    if not cargo_alvo or not cargo_alvo.strip():
        return "Informe o cargo da vaga."
    if not empresa_alvo or not empresa_alvo.strip():
        return "Informe o nome da empresa."
    return None


def main() -> None:
    st.set_page_config(page_title="Adaptador de Currículo", page_icon="📄", layout="centered")
    st.title("Adaptador de Currículo para Vagas")
    st.caption(
        "Anexe seu currículo em PDF, cole a descrição da vaga e gere uma versão "
        "adaptada, seção por seção, no idioma desejado."
    )

    conteudo_pdf, descricao_vaga, idioma_alvo, cargo_alvo, empresa_alvo = _renderizar_formulario()

    if st.button("Gerar currículo adaptado", type="primary"):
        erro_validacao = _validar_formulario(conteudo_pdf, descricao_vaga, cargo_alvo, empresa_alvo)
        if erro_validacao:
            st.error(erro_validacao)
            return

        try:
            with st.spinner("Analisando currículo e adaptando cada seção para a vaga..."):
                caso_de_uso = _montar_caso_de_uso()
                solicitacao = SolicitacaoAdaptacao(
                    pdf_curriculo=conteudo_pdf,
                    descricao_vaga=descricao_vaga,
                    idioma_alvo=idioma_alvo,
                    cargo_alvo=cargo_alvo,
                    empresa_alvo=empresa_alvo,
                    data_referencia=date.today(),
                )
                resultado = caso_de_uso.executar(solicitacao)
                caminho_salvo = _salvar_no_armazenamento(resultado.nome_arquivo.valor, resultado.pdf_bytes)

            st.success(f"Currículo gerado e salvo em: {caminho_salvo}")
            st.download_button(
                label="Baixar PDF adaptado",
                data=resultado.pdf_bytes,
                file_name=resultado.nome_arquivo.valor,
                mime="application/pdf",
            )
        except ValueError as erro:
            st.error(str(erro))
        except Exception as erro:  # noqa: BLE001 - fronteira de UI: captura e exibe qualquer falha inesperada
            st.error(f"Ocorreu um erro inesperado ao processar o currículo: {erro}")


if __name__ == "__main__":
    main()
