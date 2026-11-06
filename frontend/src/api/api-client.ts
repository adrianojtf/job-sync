import type {
  AdaptarCurriculoEntrada,
  AnalisarAtsEntrada,
  AnaliseAts,
  AvaliacaoDescricaoVaga,
  AvaliacaoExperiencia,
  AvaliarExperienciaEntrada,
  CandidatarVagaExternaEntrada,
  Candidatura,
  CandidaturaExterna,
  CandidaturasPorStatus,
  CapturarVagaEntrada,
  CartaApresentacao,
  CriarCandidaturaEntrada,
  CurriculoConteudo,
  CurriculoRevisado,
  CurriculoSalvo,
  DescobrirVagasEntrada,
  GerarCartaEntrada,
  GerarPdfCurriculoRevisadoEntrada,
  Perfil,
  PerfilEstruturado,
  PerfilEstruturadoEntrada,
  RascunhoAdaptado,
  SalvarCurriculoEntrada,
  StatusCandidatura,
  SugerirAjusteExperienciaEntrada,
  SugerirAjusteSecaoEntrada,
  SugestaoExperiencia,
  SugestaoSecao,
  TokenCaptura,
  Vaga,
  VagaDescoberta,
} from "./tipos";

/** Port de saída do frontend: uma operação por caso de uso consumido da API /v1. */
export interface ApiClient {
  verificarSaude(): Promise<{ status: string }>;

  obterOuCriarPerfil(identificador: string): Promise<Perfil>;
  buscarPerfilEstruturado(perfil: string): Promise<PerfilEstruturado | null>;
  salvarPerfilEstruturado(dados: PerfilEstruturadoEntrada): Promise<PerfilEstruturado>;
  atualizarPerfilEstruturado(dados: PerfilEstruturadoEntrada): Promise<PerfilEstruturado>;
  importarPerfilDePdf(pdfBase64: string): Promise<PerfilEstruturado>;
  avaliarExperiencia(dados: AvaliarExperienciaEntrada): Promise<AvaliacaoExperiencia>;
  /** Sugere, via IA, um novo texto para uma seção (JOB-0034). Nada é alterado no servidor. */
  sugerirAjusteSecao(dados: SugerirAjusteSecaoEntrada): Promise<SugestaoSecao>;
  /** Sugere, via IA, uma nova descrição para uma experiência (JOB-0034). */
  sugerirAjusteExperiencia(dados: SugerirAjusteExperienciaEntrada): Promise<SugestaoExperiencia>;

  listarCurriculos(perfil: string): Promise<CurriculoSalvo[]>;
  salvarCurriculo(dados: SalvarCurriculoEntrada): Promise<CurriculoSalvo>;
  baixarCurriculo(id: string, perfil: string): Promise<CurriculoConteudo>;
  removerCurriculo(id: string, perfil: string): Promise<void>;

  avaliarVaga(descricaoVaga: string): Promise<AvaliacaoDescricaoVaga>;
  /** Adapta via IA e devolve o rascunho para revisão, sem gerar PDF (JOB-0033). */
  gerarRascunhoAdaptado(
    curriculoId: string,
    dados: AdaptarCurriculoEntrada,
  ): Promise<RascunhoAdaptado>;
  /** Gera o PDF a partir do rascunho revisado e confirmado pelo usuário. */
  gerarPdfCurriculoRevisado(dados: GerarPdfCurriculoRevisadoEntrada): Promise<CurriculoRevisado>;
  analisarAts(curriculoId: string, dados: AnalisarAtsEntrada): Promise<AnaliseAts>;
  gerarCarta(dados: GerarCartaEntrada): Promise<CartaApresentacao>;

  listarVagas(perfil: string): Promise<Vaga[]>;
  capturarVaga(dados: CapturarVagaEntrada): Promise<Vaga>;
  descobrirVagas(dados: DescobrirVagasEntrada): Promise<VagaDescoberta[]>;
  candidatarVagaExterna(dados: CandidatarVagaExternaEntrada): Promise<CandidaturaExterna>;

  listarCandidaturas(perfil: string): Promise<CandidaturasPorStatus>;
  criarCandidatura(dados: CriarCandidaturaEntrada): Promise<Candidatura>;
  moverCandidatura(id: string, novoStatus: StatusCandidatura): Promise<Candidatura>;

  criarTokenCaptura(perfil: string): Promise<TokenCaptura>;
}
