"""API real para os testes E2E da UI, com dublês apenas nas portas de IA e de busca externa.

Repositórios (PostgreSQL), casos de uso, gerador de PDF e cálculo de ATS são os de produção.
Os dublês devolvem respostas determinísticas, sem rede e sem chaves de API.

Uso: PYTHONPATH=src DATABASE_URL=<url do postgres> uvicorn jobsync.tests.e2e.app_e2e:app --port 8010
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from fastapi import Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from jobsync.ats_score import CalcularAtsScore, ResultadoAtsScore
from jobsync.curriculo import AvaliacaoExperiencia, ContextoVaga, Curriculo, DiretrizesExperiencia, EquivalenciaTecnologia, PedidoRefino, ExperienciaAdaptada, ExperienciaParaAvaliacao, SecaoCurriculo, TipoSecao
from jobsync.curriculo.adapters.gerador_pdf_client import GeradorPdfClient
from jobsync.curriculo.domain.ajustador_experiencia_port import AjustadorExperienciaPort
from jobsync.curriculo.domain.ajustador_texto_port import AjustadorTextoPort
from jobsync.curriculo.domain.avaliador_experiencia_port import AvaliadorExperienciaPort
from jobsync.curriculo.domain.extrator_curriculo_port import ExtratorCurriculoPort
from jobsync.curriculo.domain.identificador_equivalencias_port import IdentificadorEquivalenciasPort
from jobsync.curriculo.domain.gerar_carta_apresentacao_port import GerarCartaApresentacaoPort
from jobsync.curriculo.domain.gerar_sugestoes_ats_port import GerarSugestoesAtsPort
from jobsync.curriculo.domain.melhorador_texto_curriculo_port import MelhoradorTextoCurriculoPort
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga import AdaptarCurriculoParaVaga
from jobsync.curriculo.service_layer.analisar_ats_vaga import AnalisarAtsVaga
from jobsync.curriculo.service_layer.avaliar_experiencia import AvaliarExperiencia
from jobsync.curriculo.service_layer.gerar_carta_apresentacao.service import GerarCartaApresentacao
from jobsync.curriculo.service_layer.sugerir_ajuste_experiencia import SugerirAjusteExperiencia
from jobsync.curriculo.service_layer.sugerir_ajuste_experiencia_adaptada import SugerirAjusteExperienciaAdaptada
from jobsync.curriculo.service_layer.sugerir_ajuste_secao_curriculo import SugerirAjusteSecaoCurriculo
from jobsync.autenticacao.adapters import (
    EstadoOAuthRepositoryImpl,
    HasherSenhaArgon2,
    LimiteTentativasRepositoryImpl,
    SessaoRepositoryImpl,
    TokenUsoUnicoRepositoryImpl,
    UsuarioRepositoryImpl,
)
from jobsync.autenticacao.domain.provedor_identidade import IdentidadeAutenticada
from jobsync.autenticacao.service_layer.associar_email_a_perfil import AssociarEmailAPerfil
from jobsync.entrypoints.api import dependencies
from jobsync.entrypoints.api.main import app
from jobsync.entrypoints.autenticacao_config import (
    configuracao_autenticacao_do_ambiente,
    configuracao_http_do_ambiente,
)
from jobsync.entrypoints.autenticacao_servicos import montar_servicos_autenticacao
from jobsync.entrypoints.dependencies import obter_pool_conexoes, obter_servicos_autenticacao
from jobsync.perfil.adapters import PerfilRepositoryImpl
from jobsync.perfil_estruturado.adapters import PerfilEstruturadoRepositoryImpl
from jobsync.shared_kernel.domain.score_avaliacao import ResultadoDimensaoAvaliacao
from jobsync.vaga import (
    AnaliseVaga,
    AvaliacaoDescricaoVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from jobsync.vaga.domain.avaliador_descricao_vaga_port import AvaliadorDescricaoVagaPort
from jobsync.vaga.domain.job_description_analyzer_port import JobDescriptionAnalyzerPort
from jobsync.vaga.service_layer.avaliar_descricao_vaga import AvaliarDescricaoVaga
from jobsync.vaga_externa import FonteVagaExterna, VagaExterna
from jobsync.vaga_externa.domain.buscador_vagas_externo_port import BuscadorVagasExternoPort
from jobsync.vaga_externa.service_layer.candidatar_na_vaga_externa import CandidatarNaVagaExterna
from jobsync.vaga_externa.service_layer.descobrir_vagas_com_match import DescobrirVagasComMatch

TECNOLOGIAS_CONHECIDAS = ("Python", "FastAPI", "Java", "Kafka", "AWS", "Docker")


def _dimensao(score: int, nivel: str) -> ResultadoDimensaoAvaliacao:
    return ResultadoDimensaoAvaliacao(score, nivel, 0.9)


class AnalisadorVagaE2E(JobDescriptionAnalyzerPort):
    """Considera requisito explícito cada tecnologia conhecida citada na descrição."""

    def analisar(self, descricao_vaga: str) -> AnaliseVaga:
        requisitos = tuple(
            RequisitoTecnico(
                nome=nome,
                categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
                tipo=TipoRequisitoTecnico.EXPLICITO,
                origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
            )
            for nome in TECNOLOGIAS_CONHECIDAS
            if nome.lower() in descricao_vaga.lower()
        )
        return AnaliseVaga(requisitos=requisitos, ambiguidade=(), texto_original=descricao_vaga)


class AjustadorTextoE2E(AjustadorTextoPort):
    def ajustar_secao(self, secao: SecaoCurriculo, contexto: ContextoVaga, ajustes=()) -> SecaoCurriculo:
        return secao

    def refinar_secao(self, secao: SecaoCurriculo, contexto: ContextoVaga, refino: PedidoRefino) -> SecaoCurriculo:
        return secao


class IdentificadorEquivalenciasE2E(IdentificadorEquivalenciasPort):
    """Aponta React → Angular quando a vaga cita Angular; nada nos demais casos."""

    def identificar(self, experiencias, contexto: ContextoVaga) -> tuple[EquivalenciaTecnologia, ...]:
        if "angular" in contexto.descricao_vaga.lower():
            return (EquivalenciaTecnologia(original="React", alvo="Angular"),)
        return ()


class AjustadorExperienciaE2E(AjustadorExperienciaPort):
    def ajustar(
        self, experiencia: ExperienciaParaAvaliacao, contexto: ContextoVaga, diretrizes: DiretrizesExperiencia
    ) -> ExperienciaAdaptada:
        trocas = "".join(f" Com {troca.alvo}." for troca in diretrizes.trocar)
        return ExperienciaAdaptada(
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
            conquistas=(experiencia.descricao,) if experiencia.descricao.strip() else (),
            contexto=f"Contexto de {experiencia.empresa}.{trocas}",
        )

    def refinar(
        self, experiencia: ExperienciaAdaptada, contexto: ContextoVaga, refino: PedidoRefino
    ) -> ExperienciaAdaptada:
        return experiencia


class AjustadorTextoSugestaoE2E(AjustadorTextoPort):
    """Sugestão com vaga: marca o texto recebido, para o E2E provar de onde veio."""

    def ajustar_secao(self, secao: SecaoCurriculo, contexto: ContextoVaga, ajustes=()) -> SecaoCurriculo:
        raise NotImplementedError("As sugestões com vaga usam refinar_secao.")

    def refinar_secao(self, secao: SecaoCurriculo, contexto: ContextoVaga, refino: PedidoRefino) -> SecaoCurriculo:
        return secao.com_novo_conteudo(f"Sugestão com vaga: {secao.conteudo}")


class AjustadorExperienciaSugestaoE2E(AjustadorExperienciaPort):
    def ajustar(
        self, experiencia: ExperienciaParaAvaliacao, contexto: ContextoVaga, diretrizes: DiretrizesExperiencia
    ) -> ExperienciaAdaptada:
        raise NotImplementedError("As sugestões com vaga usam refinar.")

    def refinar(
        self, experiencia: ExperienciaAdaptada, contexto: ContextoVaga, refino: PedidoRefino
    ) -> ExperienciaAdaptada:
        return ExperienciaAdaptada(
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
            conquistas=tuple(f"Sugestão com vaga: {conquista}" for conquista in experiencia.conquistas),
            contexto=f"Sugestão com vaga: {experiencia.contexto}",
        )


class MelhoradorTextoE2E(MelhoradorTextoCurriculoPort):
    """Sugestão sem vaga: marca o texto recebido."""

    def melhorar_secao(self, secao: SecaoCurriculo, refino: PedidoRefino) -> SecaoCurriculo:
        return secao.com_novo_conteudo(f"Sugestão de escrita: {secao.conteudo}")

    def melhorar_experiencia(
        self, experiencia: ExperienciaParaAvaliacao, refino: PedidoRefino
    ) -> ExperienciaParaAvaliacao:
        return ExperienciaParaAvaliacao(
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
            descricao=f"Sugestão de escrita: {experiencia.descricao}",
        )


class AvaliadorDescricaoVagaE2E(AvaliadorDescricaoVagaPort):
    def avaliar(self, descricao_vaga: str) -> AvaliacaoDescricaoVaga:
        return AvaliacaoDescricaoVaga(
            completude=_dimensao(75, "adequada"),
            clareza=_dimensao(80, "clara"),
            relevancia=_dimensao(85, "relevante"),
            inclusao=_dimensao(70, "inclusiva"),
        )


class AvaliadorExperienciaE2E(AvaliadorExperienciaPort):
    def avaliar(self, experiencia: ExperienciaParaAvaliacao, descricao_vaga: str) -> AvaliacaoExperiencia:
        return AvaliacaoExperiencia(
            clareza_escrita=_dimensao(80, "clara"),
            qualidade_detalhe=_dimensao(65, "parcial"),
            aderencia_vaga=_dimensao(88, "alta"),
            consistencia_textual=_dimensao(77, "consistente"),
        )


class ExtratorCurriculoE2E(ExtratorCurriculoPort):
    """Devolve um currículo fixo para fluxos que partem de um PDF da biblioteca."""

    def extrair(self, conteudo_pdf: bytes) -> Curriculo:
        return Curriculo(
            nome_completo="Pessoa E2E",
            email="e2e@jobsync.test",
            linkedin="",
            secoes=(SecaoCurriculo(tipo=TipoSecao.TECNOLOGIAS, titulo="Tecnologias", conteudo="Python, FastAPI"),),
        )


class GeradorSugestoesE2E(GerarSugestoesAtsPort):
    def gerar(self, curriculo: Curriculo, analise_vaga: AnaliseVaga, resultado_ats: ResultadoAtsScore) -> tuple[str, ...]:
        return tuple(f"Cite {requisito.nome} nas experiências em que foi usado." for requisito in resultado_ats.requisitos_faltantes)


class GeradorCartaE2E(GerarCartaApresentacaoPort):
    def gerar(self, curriculo: Curriculo, analise_vaga: AnaliseVaga, idioma_alvo: str) -> str:
        return f"Prezados recrutadores,\n\nSou {curriculo.nome_completo} e tenho interesse na vaga."


class BuscadorVagasE2E(BuscadorVagasExternoPort):
    def buscar(self, termo: str, dias_maximo: int | None = None) -> tuple[VagaExterna, ...]:
        return (
            VagaExterna(
                titulo=f"Backend Engineer ({termo})",
                empresa="Globex",
                descricao="Python, FastAPI e Kafka. Remoto.",
                url="https://example.com/vagas/globex",
                fonte=FonteVagaExterna.REMOTEOK,
            ),
        )


def _adaptar() -> AdaptarCurriculoParaVaga:
    return AdaptarCurriculoParaVaga(
        extrator=ExtratorCurriculoE2E(),
        analisador_vaga=AnalisadorVagaE2E(),
        ajustador_texto=AjustadorTextoE2E(),
        avaliador_descricao_vaga=AvaliadorDescricaoVagaE2E(),
        ajustador_experiencia=AjustadorExperienciaE2E(),
        avaliador_experiencia=AvaliadorExperienciaE2E(),
        identificador_equivalencias=IdentificadorEquivalenciasE2E(),
    )


app.dependency_overrides.update(
    {
        dependencies.obter_service_avaliar_descricao_vaga: lambda: AvaliarDescricaoVaga(avaliador=AvaliadorDescricaoVagaE2E()),
        dependencies.obter_service_avaliar_experiencia: lambda: AvaliarExperiencia(avaliador=AvaliadorExperienciaE2E()),
        dependencies.obter_service_adaptar_curriculo: _adaptar,
        dependencies.obter_service_sugerir_ajuste_secao_curriculo: lambda: SugerirAjusteSecaoCurriculo(
            ajustador_texto=AjustadorTextoSugestaoE2E(), melhorador=MelhoradorTextoE2E()
        ),
        dependencies.obter_service_sugerir_ajuste_experiencia: lambda: SugerirAjusteExperiencia(
            melhorador=MelhoradorTextoE2E()
        ),
        dependencies.obter_service_sugerir_ajuste_experiencia_adaptada: lambda: SugerirAjusteExperienciaAdaptada(
            ajustador_experiencia=AjustadorExperienciaSugestaoE2E()
        ),
        dependencies.obter_service_analisar_ats_vaga: lambda: AnalisarAtsVaga(
            extrator=ExtratorCurriculoE2E(),
            analisador_vaga=AnalisadorVagaE2E(),
            calcular_ats_score=CalcularAtsScore(),
            gerador_sugestoes=GeradorSugestoesE2E(),
        ),
        dependencies.obter_service_gerar_carta_apresentacao: lambda: GerarCartaApresentacao(gerador_carta=GeradorCartaE2E()),
        dependencies.obter_service_descobrir_vagas_com_match: lambda: DescobrirVagasComMatch(
            buscadores=(BuscadorVagasE2E(),),
            analisador_vaga=AnalisadorVagaE2E(),
            extrator_curriculo=ExtratorCurriculoE2E(),
            calcular_score=CalcularAtsScore(),
        ),
        dependencies.obter_service_candidatar_na_vaga_externa: lambda: CandidatarNaVagaExterna(
            extrator=ExtratorCurriculoE2E(),
            analisador_vaga=AnalisadorVagaE2E(),
            ajustador_texto=AjustadorTextoE2E(),
            gerador_pdf=GeradorPdfClient(),
            calcular_ats_score=CalcularAtsScore(),
            gerador_carta=GeradorCartaE2E(),
        ),
    }
)


# --- Autenticação: Google e e-mail simulados, só para o navegador percorrer o fluxo real ---


class CaixaDeEmailE2E:
    """Guarda os e-mails enviados para o teste ler o link de confirmação ou de redefinição."""

    def __init__(self) -> None:
        self.enviados: list[dict[str, str]] = []

    def enviar(self, para, assunto: str, corpo: str) -> None:
        self.enviados.append({"para": para.valor, "assunto": assunto, "corpo": corpo})


@dataclass
class IdentidadeGoogleE2E:
    subject: str = "sub-e2e"
    email: str = "google@jobsync.test"
    email_verificado: bool = True
    nome: Optional[str] = "Pessoa Google"


class ProvedorGoogleE2E:
    """Faz o papel do Google: a "tela do Google" é /e2e/idp, que volta direto com um código."""

    nome = "google"

    def __init__(self) -> None:
        self.identidade = IdentidadeGoogleE2E()

    def url_autorizacao(self, estado: str, nonce: str, code_challenge: str) -> str:
        # URL absoluta, como a do Google: a "tela do Google" fica na porta da API, fora do proxy /v1.
        return f"{URL_API_E2E}/e2e/idp?state={estado}"

    def trocar_codigo(self, codigo: str, code_verifier: str, nonce: str) -> IdentidadeAutenticada:
        atual = self.identidade
        return IdentidadeAutenticada("google", atual.subject, atual.email, atual.email_verificado, atual.nome)


URL_API_E2E = os.environ.get("E2E_URL_API", "http://localhost:8010")
CAIXA_DE_EMAIL = CaixaDeEmailE2E()
GOOGLE_E2E = ProvedorGoogleE2E()
_servicos_e2e = None


def _servicos_autenticacao_e2e():
    global _servicos_e2e
    if _servicos_e2e is None:
        pool = obter_pool_conexoes()
        _servicos_e2e = montar_servicos_autenticacao(
            usuarios=UsuarioRepositoryImpl(pool),
            sessoes=SessaoRepositoryImpl(pool),
            tokens=TokenUsoUnicoRepositoryImpl(pool),
            estados=EstadoOAuthRepositoryImpl(pool),
            limites=LimiteTentativasRepositoryImpl(pool),
            hasher=HasherSenhaArgon2(),
            enviador=CAIXA_DE_EMAIL,
            provedores={"google": GOOGLE_E2E},
            config=configuracao_autenticacao_do_ambiente(os.environ),
            http=configuracao_http_do_ambiente(os.environ),
        )
    return _servicos_e2e


app.dependency_overrides[obter_servicos_autenticacao] = _servicos_autenticacao_e2e


class IdentidadeGoogleRequest(BaseModel):
    subject: str
    email: str
    email_verificado: bool = True
    nome: Optional[str] = None


class PerfilLegadoRequest(BaseModel):
    perfil: str
    email: str
    nome_completo: str


@app.get("/e2e/idp", include_in_schema=False)
def tela_do_google_falsa(state: str = Query(...)) -> RedirectResponse:
    return RedirectResponse(f"/v1/provedores/google/retorno?code=codigo-e2e&state={state}", status_code=302)


@app.put("/e2e/idp/identidade", include_in_schema=False)
def definir_identidade_do_google(corpo: IdentidadeGoogleRequest) -> dict:
    GOOGLE_E2E.identidade = IdentidadeGoogleE2E(
        corpo.subject, corpo.email, corpo.email_verificado, corpo.nome
    )
    return {"ok": True}


@app.get("/e2e/emails", include_in_schema=False)
def listar_emails(para: str) -> list[dict[str, str]]:
    return [email for email in CAIXA_DE_EMAIL.enviados if email["para"] == para.lower()]


@app.post("/e2e/perfis-legados", include_in_schema=False)
def criar_perfil_legado(corpo: PerfilLegadoRequest) -> dict:
    """Cria um perfil anterior à autenticação, com dados, e associa o e-mail do dono (como a CLI)."""
    from jobsync.perfil_estruturado.service_layer.salvar_perfil_estruturado import (
        SalvarPerfilEstruturado,
        SalvarPerfilEstruturadoInputDto,
    )

    pool = obter_pool_conexoes()
    perfis = PerfilRepositoryImpl(pool)
    perfis.criar(corpo.perfil)
    SalvarPerfilEstruturado(repositorio=PerfilEstruturadoRepositoryImpl(pool)).executar(
        SalvarPerfilEstruturadoInputDto(
            perfil_identificador=corpo.perfil,
            nome_completo=corpo.nome_completo,
            email=corpo.email,
            linkedin="",
            resumo_profissional="Dados anteriores à autenticação.",
            experiencias=(),
            formacoes=(),
            certificacoes=(),
            idiomas=(),
            tecnologias=("Python",),
        )
    )
    AssociarEmailAPerfil(UsuarioRepositoryImpl(pool), perfis).executar(corpo.perfil, corpo.email)
    return {"ok": True}


@app.delete("/e2e/limites", include_in_schema=False)
def zerar_limites_de_tentativas() -> dict:
    """O banco de E2E é reaproveitado entre rodadas: zera o contador de falhas de login."""
    with obter_pool_conexoes().connection() as conexao:
        conexao.execute("DELETE FROM limite_tentativa")
    return {"ok": True}
