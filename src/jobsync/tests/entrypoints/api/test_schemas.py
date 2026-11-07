"""Testes dos schemas Pydantic da API."""

from __future__ import annotations

import base64
import uuid
from datetime import date, datetime

from jobsync.ats_score import ResultadoAtsScore
from jobsync.candidatura import Candidatura, MudancaStatus, StatusCandidatura
from jobsync.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from jobsync.curriculo import RascunhoCurriculoAdaptado
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.dtos import (
    AdaptarCurriculoParaVagaOutputDto,
)
from jobsync.curriculo.service_layer.gerar_pdf_curriculo_revisado import (
    GerarPdfCurriculoRevisadoOutputDto,
)
from jobsync.curriculo.service_layer.analisar_ats_vaga.dtos import (
    AnalisarAtsVagaOutputDto,
)
from jobsync.curriculo_salvo import CurriculoSalvo
from jobsync.entrypoints.api.schemas.candidatura import (
    CandidaturaCriarRequest,
    CandidaturaResponse,
    CandidaturasListagemResponse,
    CandidaturaSubmeterRequest,
)
from jobsync.entrypoints.api.schemas.curriculo import (
    AdaptarCurriculoRequest,
    AdaptarCurriculoResponse,
    AnalisarAtsRequest,
    AnalisarAtsResponse,
    CurriculoSalvarRequest,
    CurriculoSalvoResponse,
)
from jobsync.entrypoints.api.schemas.perfil import (
    PerfilResponse,
    PerfisListagemResponse,
)
from jobsync.entrypoints.api.schemas.vaga import (
    VagaCapturarRequest,
    VagaResponse,
    VagasListagemResponse,
)
from jobsync.entrypoints.api.schemas.vaga_externa import (
    DescobrirVagasRequest,
    DescobrirVagasResponse,
    VagaDescobertaResponse,
)
from jobsync.perfil import Perfil
from jobsync.shared_kernel.domain import NomeArquivo
from jobsync.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
    Vaga,
)
from jobsync.vaga_externa import FonteVagaExterna, VagaComScore, VagaExterna


class TestCurriculoSchemas:
    def test_curriculo_salvar_request_to_dto(self):
        pdf_bytes = b"%PDF-1.4 test"
        pdf_base64 = base64.b64encode(pdf_bytes).decode()

        request = CurriculoSalvarRequest(
            perfil_identificador="matheus",
            nome_referencia="Curriculo.pdf",
            pdf_base64=pdf_base64,
        )

        dto = request.to_dto()

        assert dto.perfil_identificador == "matheus"
        assert dto.nome_referencia == "Curriculo.pdf"
        assert dto.pdf_bytes == pdf_bytes

    def test_curriculo_salvo_response_from_dto(self):
        curriculo = CurriculoSalvo(
            id=str(uuid.uuid4()),
            perfil_identificador="matheus",
            nome_referencia="Curriculo.pdf",
            pdf_bytes=b"%PDF-1.4 test",
            data_upload=datetime(2025, 1, 1, 12, 0),
        )

        response = CurriculoSalvoResponse.from_dto(curriculo)

        assert response.id == curriculo.id
        assert response.perfil_identificador == "matheus"
        assert response.nome_referencia == "Curriculo.pdf"
        assert response.data_upload == curriculo.data_upload

    def test_adaptar_curriculo_request_to_dto(self):
        pdf_bytes = b"%PDF-1.4 test"
        pdf_base64 = base64.b64encode(pdf_bytes).decode()

        request = AdaptarCurriculoRequest(
            descricao_vaga="Desenvolvedor Python",
            idioma_alvo="pt",
            cargo_alvo="Engenheiro",
            empresa_alvo="TechCorp",
            pdf_base64=pdf_base64,
        )

        dto = request.to_dto()

        assert dto.descricao_vaga == "Desenvolvedor Python"
        assert dto.pdf_curriculo == pdf_bytes

    def test_adaptar_curriculo_response_from_dto(self):
        curriculo = Curriculo(
            nome_completo="Matheus Silva",
            email="matheus@email.com",
            linkedin="https://linkedin.com/in/matheus",
            secoes=(
                SecaoCurriculo(
                    tipo=TipoSecao.TECNOLOGIAS,
                    titulo="Tecnologias",
                    conteudo="Python",
                ),
            ),
        )
        analise = AnaliseVaga(
            requisitos=(),
            ambiguidade=(),
            texto_original="Desenvolvedor Python",
        )
        nome_arquivo = NomeArquivo.criar(
            nome_completo="Matheus Silva",
            cargo="Engenheiro",
            empresa="TechCorp",
        )
        dto = AdaptarCurriculoParaVagaOutputDto(
            rascunho=RascunhoCurriculoAdaptado(
                nome_completo=curriculo.nome_completo,
                email=curriculo.email,
                linkedin=curriculo.linkedin,
                secoes=curriculo.secoes,
            ),
            curriculo_adaptado=curriculo,
            analise_vaga=analise,
        )
        pdf = GerarPdfCurriculoRevisadoOutputDto(
            pdf_bytes=b"%PDF-1.4 adapted", nome_arquivo=nome_arquivo
        )

        response = AdaptarCurriculoResponse.from_dto(dto, pdf)

        assert response.nome_arquivo == nome_arquivo.valor
        assert response.pdf_base64 == base64.b64encode(b"%PDF-1.4 adapted").decode()
        assert response.nome_completo == "Matheus Silva"

    def test_analisar_ats_request_to_dto(self):
        pdf_bytes = b"%PDF-1.4 test"
        pdf_base64 = base64.b64encode(pdf_bytes).decode()

        request = AnalisarAtsRequest(
            descricao_vaga="Desenvolvedor Python",
            pdf_base64=pdf_base64,
        )

        dto = request.to_dto()

        assert dto.descricao_vaga == "Desenvolvedor Python"
        assert dto.pdf_curriculo == pdf_bytes

    def test_analisar_ats_response_from_dto(self):
        curriculo = Curriculo(
            nome_completo="Matheus Silva",
            email="matheus@email.com",
            linkedin="https://linkedin.com/in/matheus",
            secoes=(
                SecaoCurriculo(
                    tipo=TipoSecao.TECNOLOGIAS,
                    titulo="Tecnologias",
                    conteudo="Python",
                ),
            ),
        )
        analise = AnaliseVaga(
            requisitos=(),
            ambiguidade=(),
            texto_original="Desenvolvedor Python",
        )
        requisito_faltante = RequisitoTecnico(
            nome="Docker",
            categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
            tipo=TipoRequisitoTecnico.EXPLICITO,
            origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
        )
        resultado = ResultadoAtsScore(
            nota=85,
            requisitos_faltantes=(requisito_faltante,),
        )
        dto = AnalisarAtsVagaOutputDto(
            curriculo=curriculo,
            analise_vaga=analise,
            resultado_ats=resultado,
            sugestoes=("Incluir Docker",),
        )

        response = AnalisarAtsResponse.from_dto(dto)

        assert response.nome_completo == "Matheus Silva"
        assert response.nota == 85
        assert response.requisitos_faltantes[0].nome == "Docker"
        assert response.sugestoes == ["Incluir Docker"]


class TestVagaSchemas:
    def test_vaga_capturar_request_to_dto(self):
        request = VagaCapturarRequest(
            perfil_identificador="matheus",
            texto_descricao="Desenvolvedor Python",
            url_origem="https://example.com",
        )

        dto = request.to_dto()

        assert dto.perfil_identificador == "matheus"
        assert dto.texto_descricao == "Desenvolvedor Python"
        assert dto.url_origem == "https://example.com"

    def test_vaga_response_from_dto(self):
        vaga = Vaga(
            id=str(uuid.uuid4()),
            perfil_identificador="matheus",
            texto_descricao="Desenvolvedor Python",
            data_captura=datetime(2025, 1, 1, 12, 0),
            url_origem="https://example.com",
        )

        response = VagaResponse.from_dto(vaga)

        assert response.id == vaga.id
        assert response.perfil_identificador == "matheus"
        assert response.texto_descricao == "Desenvolvedor Python"

    def test_vagas_listagem_response_from_dto(self):
        vaga = Vaga(
            id=str(uuid.uuid4()),
            perfil_identificador="matheus",
            texto_descricao="Desenvolvedor Python",
            data_captura=datetime(2025, 1, 1, 12, 0),
            url_origem=None,
        )

        response = VagasListagemResponse.from_dto((vaga,))

        assert response.total == 1
        assert len(response.items) == 1
        assert response.items[0].id == vaga.id


class TestVagaExternaSchemas:
    def test_descobrir_vagas_request_to_dto(self):
        pdf_bytes = b"%PDF-1.4 test"
        pdf_base64 = base64.b64encode(pdf_bytes).decode()

        request = DescobrirVagasRequest(
            termo="Python",
            pdf_base64=pdf_base64,
            dias_maximo=7,
        )

        dto = request.to_dto()

        assert dto["termo"] == "Python"
        assert dto["dias_maximo"] == 7
        assert dto["pdf_curriculo"] == pdf_bytes

    def test_vaga_descoberta_response_from_dto(self):
        vaga_externa = VagaExterna(
            titulo="Desenvolvedor Python",
            empresa="TechCorp",
            descricao="Vaga para desenvolvedor Python",
            url="https://example.com/job",
            fonte=FonteVagaExterna.REMOTEOK,
            data_publicacao=date(2025, 1, 1),
        )
        requisito = RequisitoTecnico(
            nome="Docker",
            categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
            tipo=TipoRequisitoTecnico.EXPLICITO,
            origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
        )
        vaga_com_score = VagaComScore(
            vaga=vaga_externa,
            resultado_score=ResultadoAtsScore(
                nota=90,
                requisitos_faltantes=(requisito,),
            ),
        )

        response = VagaDescobertaResponse.from_dto(vaga_com_score)

        assert response.titulo == "Desenvolvedor Python"
        assert response.nota == 90
        assert response.requisitos_faltantes[0].nome == "Docker"

    def test_descobrir_vagas_response_from_dto(self):
        vaga_externa = VagaExterna(
            titulo="Desenvolvedor Python",
            empresa="TechCorp",
            descricao="Vaga",
            url="https://example.com/job",
            fonte=FonteVagaExterna.REMOTEOK,
        )
        vaga_com_score = VagaComScore(
            vaga=vaga_externa,
            resultado_score=ResultadoAtsScore(nota=80, requisitos_faltantes=()),
        )

        response = DescobrirVagasResponse.from_dto((vaga_com_score,))

        assert response.total == 1
        assert response.items[0].nota == 80


class TestCandidaturaSchemas:
    def test_candidatura_criar_request_to_dto(self):
        request = CandidaturaCriarRequest(
            perfil_identificador="matheus",
            vaga_id="vaga-1",
            curriculo_salvo_id="curriculo-1",
            empresa="TechCorp",
            cargo="Engenheiro",
        )

        dto = request.to_dto()

        assert dto.vaga_id == "vaga-1"
        assert dto.curriculo_salvo_id == "curriculo-1"

    def test_candidatura_submeter_request_to_dto(self):
        request = CandidaturaSubmeterRequest(novo_status="entrevista")

        dto = request.to_dto()

        assert dto["novo_status"] == StatusCandidatura.ENTREVISTA

    def test_candidatura_response_from_dto(self):
        agora = datetime(2025, 1, 1, 12, 0)
        candidatura = Candidatura(
            id="candidatura-1",
            perfil_identificador="matheus",
            vaga_id="vaga-1",
            curriculo_salvo_id="curriculo-1",
            empresa="TechCorp",
            cargo="Engenheiro",
            status=StatusCandidatura.APLICADO,
            data_aplicacao=agora,
            historico_status=(MudancaStatus(status=StatusCandidatura.APLICADO, data=agora),),
        )

        response = CandidaturaResponse.from_dto(candidatura)

        assert response.id == "candidatura-1"
        assert response.status == "APLICADO"
        assert response.historico_status[0].status == "APLICADO"

    def test_candidaturas_listagem_response_from_dto(self):
        agora = datetime(2025, 1, 1, 12, 0)
        candidatura = Candidatura(
            id="candidatura-1",
            perfil_identificador="matheus",
            vaga_id="vaga-1",
            curriculo_salvo_id="curriculo-1",
            empresa="TechCorp",
            cargo="Engenheiro",
            status=StatusCandidatura.APLICADO,
            data_aplicacao=agora,
            historico_status=(MudancaStatus(status=StatusCandidatura.APLICADO, data=agora),),
        )
        agrupadas = {StatusCandidatura.APLICADO: (candidatura,)}

        response = CandidaturasListagemResponse.from_dto(agrupadas)

        assert response.total == 1
        assert len(response.por_status["APLICADO"]) == 1
        assert len(response.por_status["ENTREVISTA"]) == 0


class TestPerfilSchemas:
    def test_perfil_response_from_dto(self):
        perfil = Perfil(identificador="matheus")

        response = PerfilResponse.from_dto(perfil)

        assert response.identificador == "matheus"

    def test_perfis_listagem_response_from_dto(self):
        perfil = Perfil(identificador="matheus")

        response = PerfisListagemResponse.from_dto((perfil,))

        assert response.total == 1
        assert response.items[0].identificador == "matheus"
