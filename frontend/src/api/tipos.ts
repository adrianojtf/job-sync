// Nomes de domínio para os tipos gerados do contrato OpenAPI (schema.d.ts).
import type { components } from "./schema";

type Esquemas = components["schemas"];

export type Perfil = Esquemas["PerfilResponse"];
export type PerfilEstruturado = Esquemas["PerfilEstruturadoResponse"];
export type PerfilEstruturadoEntrada = Esquemas["PerfilEstruturadoRequest"];
export type AvaliarExperienciaEntrada = Esquemas["AvaliarExperienciaRequest"];
export type AvaliacaoExperiencia = Esquemas["AvaliacaoExperienciaResponse"];
export type CurriculoSalvo = Esquemas["CurriculoSalvoResponse"];
export type SalvarCurriculoEntrada = Esquemas["CurriculoSalvarRequest"];
export type CurriculoConteudo = Esquemas["CurriculoSalvoConteudoResponse"];
export type AvaliacaoDescricaoVaga = Esquemas["AvaliacaoDescricaoVagaResponse"];
export type AdaptarCurriculoEntrada = Esquemas["AdaptarCurriculoRequest"];
export type CurriculoAdaptado = Esquemas["AdaptarCurriculoResponse"];
export type RascunhoAdaptado = Esquemas["RascunhoAdaptadoResponse"];
export type RascunhoCurriculoAdaptado = Esquemas["RascunhoCurriculoAdaptadoSchema"];
export type GerarPdfCurriculoRevisadoEntrada = Esquemas["GerarPdfCurriculoRevisadoRequest"];
export type CurriculoRevisado = Esquemas["CurriculoRevisadoResponse"];
export type AnalisarAtsEntrada = Esquemas["AnalisarAtsRequest"];
export type AnaliseAts = Esquemas["AnalisarAtsResponse"];
export type GerarCartaEntrada = Esquemas["GerarCartaApresentacaoRequest"];
export type CartaApresentacao = Esquemas["CartaApresentacaoResponse"];
export type Vaga = Esquemas["VagaResponse"];
export type CapturarVagaEntrada = Esquemas["VagaCapturarRequest"];
export type DescobrirVagasEntrada = Esquemas["DescobrirVagasRequest"];
export type VagaDescoberta = Esquemas["VagaDescobertaResponse"];
export type CandidatarVagaExternaEntrada = Esquemas["CandidatarVagaExternaRequest"];
export type CandidaturaExterna = Esquemas["CandidatarVagaExternaResponse"];
export type Candidatura = Esquemas["CandidaturaResponse"];
export type CandidaturasPorStatus = Esquemas["CandidaturasListagemResponse"];
export type CriarCandidaturaEntrada = Esquemas["CandidaturaCriarRequest"];
export type TokenCaptura = Esquemas["TokenCapturaResponse"];
export type Problema = Esquemas["ProblemaResponse"];

export type StatusCandidatura = "APLICADO" | "ENTREVISTA" | "OFERTA" | "REJEITADO";
