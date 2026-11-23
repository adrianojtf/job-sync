import type {
  AdaptarCurriculoEntrada,
  AnalisarAtsEntrada,
  AnaliseAts,
  AtualizarCurriculoAdaptadoEntrada,
  AvaliacaoDescricaoVaga,
  AvaliacaoExperiencia,
  AvaliarExperienciaEntrada,
  CandidatarVagaExternaEntrada,
  Candidatura,
  CandidaturaExterna,
  CandidaturasPorStatus,
  CapturarVagaEntrada,
  CartaApresentacao,
  ConfirmarCandidaturaEntrada,
  ConquistaRascunho,
  ConquistaRascunhoEntrada,
  CriarCandidaturaEntrada,
  CurriculoAdaptado,
  CurriculoAdaptadoPdf,
  CurriculoAdaptadoResumo,
  CurriculoConteudo,
  CurriculoRevisado,
  CurriculoSalvo,
  DescobrirVagasEntrada,
  GerarCartaEntrada,
  GerarPdfCurriculoRevisadoEntrada,
  Lacunas,
  LacunasEntrada,
  PerfilEstruturado,
  PerfilEstruturadoEntrada,
  RascunhoAdaptado,
  SalvarCurriculoAdaptadoEntrada,
  SalvarCurriculoEntrada,
  StatusCandidatura,
  SugerirAjusteExperienciaAdaptadaEntrada,
  SugerirAjusteExperienciaEntrada,
  SugerirAjusteSecaoEntrada,
  SugestaoExperiencia,
  SugestaoExperienciaAdaptada,
  SugestaoSecao,
  TokenCaptura,
  Provedores,
  Usuario,
  Vaga,
  VagaDescoberta,
} from "./tipos";

/** Port de saída do frontend: uma operação por caso de uso consumido da API /v1. */
export interface ApiClient {
  verificarSaude(): Promise<{ status: string }>;

  /** Usuário da sessão atual (cookie HttpOnly), ou `null` quando não há sessão válida. */
  obterUsuarioAtual(): Promise<Usuario | null>;
  /** Métodos de entrada que o servidor oferece (Google, e-mail e senha, login legado de dev). */
  listarProvedores(): Promise<Provedores>;
  entrarComSenha(email: string, senha: string): Promise<Usuario>;
  /** Login legado por identificador; só existe em desenvolvimento (404 fora dele). */
  entrarComIdentificador(identificador: string): Promise<Usuario>;
  sair(): Promise<void>;
  /** Envia o link de confirmação; a senha só vale depois de confirmar o e-mail. */
  cadastrar(email: string, senha: string): Promise<void>;
  confirmarEmail(token: string): Promise<void>;
  solicitarRedefinicaoSenha(email: string): Promise<void>;
  redefinirSenha(token: string, novaSenha: string): Promise<void>;
  /** URL para onde o navegador deve ir para entrar com um provedor (fluxo de redirecionamento). */
  urlAutorizacao(provedor: string, destino: string): string;
  buscarPerfilEstruturado(perfil: string): Promise<PerfilEstruturado | null>;
  salvarPerfilEstruturado(dados: PerfilEstruturadoEntrada): Promise<PerfilEstruturado>;
  atualizarPerfilEstruturado(dados: PerfilEstruturadoEntrada): Promise<PerfilEstruturado>;
  importarPerfilDePdf(pdfBase64: string): Promise<PerfilEstruturado>;
  /** Conquistas da experiência que se parecem com o texto novo (JOB-0042); não altera o perfil salvo. */
  verificarConquistasParecidas(texto: string, conquistas: string[]): Promise<string[]>;
  /** Temas da vaga que o perfil não sustenta, com a pergunta de cada um (JOB-0043). */
  identificarLacunas(dados: LacunasEntrada): Promise<Lacunas>;
  /** Conquista redigida pela IA a partir do caso do candidato; não salva nada (JOB-0043). */
  redigirConquistaDeLacuna(dados: ConquistaRascunhoEntrada): Promise<ConquistaRascunho>;
  /** Guarda a conquista aprovada no banco da experiência e devolve o perfil atualizado (JOB-0043). */
  adicionarConquistaAExperiencia(
    perfil: string,
    experienciaIndice: number,
    texto: string,
  ): Promise<PerfilEstruturado>;
  avaliarExperiencia(dados: AvaliarExperienciaEntrada): Promise<AvaliacaoExperiencia>;
  /** Sugere, via IA, um novo texto para uma seção (JOB-0034). Nada é alterado no servidor. */
  sugerirAjusteSecao(dados: SugerirAjusteSecaoEntrada): Promise<SugestaoSecao>;
  /** Sugere, via IA, uma nova descrição para uma experiência (JOB-0034). */
  sugerirAjusteExperiencia(dados: SugerirAjusteExperienciaEntrada): Promise<SugestaoExperiencia>;
  /** Refina conquistas e contexto de uma experiência adaptada, orientado pela vaga (JOB-0035). */
  sugerirAjusteExperienciaAdaptada(
    dados: SugerirAjusteExperienciaAdaptadaEntrada,
  ): Promise<SugestaoExperienciaAdaptada>;

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
  /** Guarda o currículo adaptado confirmado na revisão e devolve o PDF gerado dele (JOB-0041). */
  salvarCurriculoAdaptado(dados: SalvarCurriculoAdaptadoEntrada): Promise<CurriculoAdaptadoPdf>;
  /** Salva a edição de um currículo adaptado e devolve o PDF regenerado. */
  atualizarCurriculoAdaptado(
    id: string,
    dados: AtualizarCurriculoAdaptadoEntrada,
  ): Promise<CurriculoAdaptadoPdf>;
  /** Conteúdo salvo e vaga usada, para reabrir a revisão. */
  obterCurriculoAdaptado(id: string, perfil: string): Promise<CurriculoAdaptado>;
  listarCurriculosAdaptados(perfil: string): Promise<CurriculoAdaptadoResumo[]>;
  analisarAts(curriculoId: string, dados: AnalisarAtsEntrada): Promise<AnaliseAts>;
  gerarCarta(dados: GerarCartaEntrada): Promise<CartaApresentacao>;

  listarVagas(perfil: string): Promise<Vaga[]>;
  capturarVaga(dados: CapturarVagaEntrada): Promise<Vaga>;
  descobrirVagas(dados: DescobrirVagasEntrada): Promise<VagaDescoberta[]>;
  candidatarVagaExterna(dados: CandidatarVagaExternaEntrada): Promise<CandidaturaExterna>;

  listarCandidaturas(perfil: string): Promise<CandidaturasPorStatus>;
  criarCandidatura(dados: CriarCandidaturaEntrada): Promise<Candidatura>;
  /** Cria vaga, currículo salvo com o PDF gerado e candidatura APLICADO em uma operação (JOB-0037). */
  confirmarCandidaturaAjustada(dados: ConfirmarCandidaturaEntrada): Promise<Candidatura>;
  /** Move a candidatura de coluna e/ou posição (índice na coluna de destino; ausente = topo). */
  moverCandidatura(
    id: string,
    novoStatus: StatusCandidatura,
    posicao?: number,
  ): Promise<Candidatura>;

  criarTokenCaptura(perfil: string): Promise<TokenCaptura>;
}
