import type { ApiClient } from "./api-client";
import { ApiError } from "./api-error";
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
  CriarCandidaturaEntrada,
  CurriculoAdaptado,
  CurriculoAdaptadoPdf,
  CurriculoAdaptadoResumo,
  CurriculoConteudo,
  CurriculoRevisado,
  CurriculoSalvo,
  DadosVaga,
  DescobrirVagasEntrada,
  ExtracaoVagaEntrada,
  GerarCartaEntrada,
  GerarPdfCurriculoRevisadoEntrada,
  ConquistaRascunho,
  ConquistaRascunhoEntrada,
  ConquistasParecidas,
  Lacunas,
  LacunasEntrada,
  PerfilEstruturado,
  PerfilEstruturadoEntrada,
  RascunhoAdaptado,
  Problema,
  SalvarCurriculoAdaptadoEntrada,
  SalvarCurriculoEntrada,
  StatusCandidatura,
  SugerirAjusteExperienciaAdaptadaEntrada,
  SugerirAjusteExperienciaEntrada,
  SugerirAjusteSecaoEntrada,
  SugestaoExperiencia,
  SugestaoExperienciaAdaptada,
  SugestaoSecao,
  Provedores,
  TokenCaptura,
  Usuario,
  Vaga,
  VagaDescoberta,
} from "./tipos";

export const TIMEOUT_PADRAO_MS = 15_000;
export const TIMEOUT_IA_MS = 180_000;

export interface HttpApiClientOpcoes {
  /** Origem da API. Vazio usa a mesma origem da página (proxy do Vite ou Nginx). */
  baseUrl?: string;
  timeoutPadraoMs?: number;
  timeoutIaMs?: number;
}

type Metodo = "GET" | "POST" | "PUT" | "DELETE";

interface Requisicao {
  corpo?: unknown;
  query?: Record<string, string>;
  /** Operações que chamam modelos de IA e podem levar dezenas de segundos. */
  ia?: boolean;
}

interface Listagem<T> {
  items: T[];
}

const caminho = (strings: TemplateStringsArray, ...partes: string[]): string =>
  strings.reduce(
    (acc, trecho, i) => acc + trecho + (i < partes.length ? encodeURIComponent(partes[i]!) : ""),
    "",
  );

function ehProblema(valor: unknown): valor is Problema {
  return typeof valor === "object" && valor !== null && "status" in valor && "title" in valor;
}

/** Adapter HTTP (fetch) do port ApiClient. */
export class HttpApiClient implements ApiClient {
  private readonly baseUrl: string;
  private readonly timeoutPadraoMs: number;
  private readonly timeoutIaMs: number;

  constructor(opcoes: HttpApiClientOpcoes = {}) {
    this.baseUrl = (opcoes.baseUrl ?? "").replace(/\/$/, "");
    this.timeoutPadraoMs = opcoes.timeoutPadraoMs ?? TIMEOUT_PADRAO_MS;
    this.timeoutIaMs = opcoes.timeoutIaMs ?? TIMEOUT_IA_MS;
  }

  verificarSaude(): Promise<{ status: string }> {
    return this.requisitar("GET", "/v1/health");
  }

  async obterUsuarioAtual(): Promise<Usuario | null> {
    try {
      return await this.requisitar<Usuario>("GET", "/v1/usuarios/me");
    } catch (erro) {
      if (erro instanceof ApiError && erro.status === 401) return null;
      throw erro;
    }
  }

  listarProvedores(): Promise<Provedores> {
    return this.requisitar("GET", "/v1/provedores");
  }

  entrarComSenha(email: string, senha: string): Promise<Usuario> {
    return this.requisitar("POST", "/v1/sessoes", { corpo: { email, senha } });
  }

  entrarComIdentificador(identificador: string): Promise<Usuario> {
    return this.requisitar("POST", "/v1/sessoes/simples", { corpo: { identificador } });
  }

  async sair(): Promise<void> {
    await this.requisitar("DELETE", "/v1/sessoes/atual");
  }

  async cadastrar(email: string, senha: string): Promise<void> {
    await this.requisitar("POST", "/v1/usuarios", { corpo: { email, senha } });
  }

  async confirmarEmail(token: string): Promise<void> {
    await this.requisitar("PUT", caminho`/v1/confirmacoes-email/${token}`);
  }

  async solicitarRedefinicaoSenha(email: string): Promise<void> {
    await this.requisitar("POST", "/v1/redefinicoes-senha", { corpo: { email } });
  }

  async redefinirSenha(token: string, novaSenha: string): Promise<void> {
    await this.requisitar("PUT", caminho`/v1/redefinicoes-senha/${token}`, {
      corpo: { nova_senha: novaSenha },
    });
  }

  urlAutorizacao(provedor: string, destino: string): string {
    return this.montarUrl(`/v1/provedores/${encodeURIComponent(provedor)}/autorizacao`, {
      destino,
    });
  }

  async buscarPerfilEstruturado(perfil: string): Promise<PerfilEstruturado | null> {
    try {
      return await this.requisitar<PerfilEstruturado>(
        "GET",
        caminho`/v1/perfil-estruturado/${perfil}`,
      );
    } catch (erro) {
      if (erro instanceof ApiError && erro.status === 404) return null;
      throw erro;
    }
  }

  salvarPerfilEstruturado(dados: PerfilEstruturadoEntrada): Promise<PerfilEstruturado> {
    return this.requisitar("POST", "/v1/perfil-estruturado", { corpo: dados });
  }

  atualizarPerfilEstruturado(dados: PerfilEstruturadoEntrada): Promise<PerfilEstruturado> {
    return this.requisitar("PUT", caminho`/v1/perfil-estruturado/${dados.perfil_identificador}`, {
      corpo: dados,
    });
  }

  importarPerfilDePdf(pdfBase64: string): Promise<PerfilEstruturado> {
    return this.requisitar("POST", "/v1/perfil-estruturado/importacoes", {
      corpo: { pdf_base64: pdfBase64 },
      ia: true,
    });
  }

  migrarExperienciasDoPerfil(perfil: string): Promise<PerfilEstruturado> {
    return this.requisitar(
      "POST",
      caminho`/v1/perfil-estruturado/${perfil}/migracoes-de-experiencias`,
      { ia: true },
    );
  }

  async verificarConquistasParecidas(texto: string, conquistas: string[]): Promise<string[]> {
    const resposta = await this.requisitar<ConquistasParecidas>(
      "POST",
      "/v1/perfil-estruturado/conquistas/parecidas",
      { corpo: { texto, conquistas } },
    );
    return resposta.parecidas;
  }

  identificarLacunas(dados: LacunasEntrada): Promise<Lacunas> {
    return this.requisitar("POST", "/v1/curriculos/lacunas", { corpo: dados, ia: true });
  }

  redigirConquistaDeLacuna(dados: ConquistaRascunhoEntrada): Promise<ConquistaRascunho> {
    return this.requisitar("POST", "/v1/curriculos/lacunas/conquista-rascunho", {
      corpo: dados,
      ia: true,
    });
  }

  adicionarConquistaAExperiencia(
    perfil: string,
    experienciaIndice: number,
    texto: string,
  ): Promise<PerfilEstruturado> {
    return this.requisitar(
      "POST",
      caminho`/v1/perfil-estruturado/${perfil}/experiencias/${String(experienciaIndice)}/conquistas`,
      { corpo: { texto } },
    );
  }

  avaliarExperiencia(dados: AvaliarExperienciaEntrada): Promise<AvaliacaoExperiencia> {
    return this.requisitar("POST", "/v1/experiencias-profissionais/avaliacoes", {
      corpo: dados,
      ia: true,
    });
  }

  sugerirAjusteSecao(dados: SugerirAjusteSecaoEntrada): Promise<SugestaoSecao> {
    return this.requisitar("POST", "/v1/secoes-curriculo/sugestoes", { corpo: dados, ia: true });
  }

  sugerirAjusteExperiencia(dados: SugerirAjusteExperienciaEntrada): Promise<SugestaoExperiencia> {
    return this.requisitar("POST", "/v1/experiencias-profissionais/sugestoes", {
      corpo: dados,
      ia: true,
    });
  }

  sugerirAjusteExperienciaAdaptada(
    dados: SugerirAjusteExperienciaAdaptadaEntrada,
  ): Promise<SugestaoExperienciaAdaptada> {
    return this.requisitar("POST", "/v1/experiencias-adaptadas/sugestoes", {
      corpo: dados,
      ia: true,
    });
  }

  async listarCurriculos(perfil: string): Promise<CurriculoSalvo[]> {
    const resposta = await this.requisitar<Listagem<CurriculoSalvo>>("GET", "/v1/curriculos", {
      query: { perfil_identificador: perfil },
    });
    return resposta.items;
  }

  salvarCurriculo(dados: SalvarCurriculoEntrada): Promise<CurriculoSalvo> {
    return this.requisitar("POST", "/v1/curriculos", { corpo: dados });
  }

  baixarCurriculo(id: string, perfil: string): Promise<CurriculoConteudo> {
    return this.requisitar("GET", caminho`/v1/curriculos/${id}/conteudo`, {
      query: { perfil_identificador: perfil },
    });
  }

  removerCurriculo(id: string, perfil: string): Promise<void> {
    return this.requisitar("DELETE", caminho`/v1/curriculos/${id}`, {
      query: { perfil_identificador: perfil },
    });
  }

  avaliarVaga(descricaoVaga: string): Promise<AvaliacaoDescricaoVaga> {
    return this.requisitar("POST", "/v1/vagas/avaliacoes", {
      corpo: { descricao_vaga: descricaoVaga },
      ia: true,
    });
  }

  gerarRascunhoAdaptado(
    curriculoId: string,
    dados: AdaptarCurriculoEntrada,
  ): Promise<RascunhoAdaptado> {
    return this.requisitar("POST", caminho`/v1/curriculos/${curriculoId}/rascunhos-adaptados`, {
      corpo: dados,
      ia: true,
    });
  }

  gerarPdfCurriculoRevisado(dados: GerarPdfCurriculoRevisadoEntrada): Promise<CurriculoRevisado> {
    return this.requisitar("POST", "/v1/curriculos-revisados", { corpo: dados });
  }

  salvarCurriculoAdaptado(dados: SalvarCurriculoAdaptadoEntrada): Promise<CurriculoAdaptadoPdf> {
    return this.requisitar("POST", "/v1/curriculos-adaptados", { corpo: dados });
  }

  atualizarCurriculoAdaptado(
    id: string,
    dados: AtualizarCurriculoAdaptadoEntrada,
  ): Promise<CurriculoAdaptadoPdf> {
    return this.requisitar("PUT", caminho`/v1/curriculos-adaptados/${id}`, { corpo: dados });
  }

  obterCurriculoAdaptado(id: string, perfil: string): Promise<CurriculoAdaptado> {
    return this.requisitar("GET", caminho`/v1/curriculos-adaptados/${id}`, {
      query: { perfil_identificador: perfil },
    });
  }

  async listarCurriculosAdaptados(perfil: string): Promise<CurriculoAdaptadoResumo[]> {
    const resposta = await this.requisitar<Listagem<CurriculoAdaptadoResumo>>(
      "GET",
      "/v1/curriculos-adaptados",
      { query: { perfil_identificador: perfil } },
    );
    return resposta.items;
  }

  analisarAts(curriculoId: string, dados: AnalisarAtsEntrada): Promise<AnaliseAts> {
    return this.requisitar("POST", caminho`/v1/curriculos/${curriculoId}/analises-ats`, {
      corpo: dados,
      ia: true,
    });
  }

  gerarCarta(dados: GerarCartaEntrada): Promise<CartaApresentacao> {
    return this.requisitar("POST", "/v1/cartas-apresentacao", { corpo: dados, ia: true });
  }

  async listarVagas(perfil: string): Promise<Vaga[]> {
    const resposta = await this.requisitar<Listagem<Vaga>>("GET", "/v1/vagas", {
      query: { perfil_identificador: perfil },
    });
    return resposta.items;
  }

  capturarVaga(dados: CapturarVagaEntrada): Promise<Vaga> {
    return this.requisitar("POST", "/v1/vagas", { corpo: dados });
  }

  extrairDadosVaga(dados: ExtracaoVagaEntrada): Promise<DadosVaga> {
    return this.requisitar("POST", "/v1/vagas/extracoes", { corpo: dados, ia: true });
  }

  async descobrirVagas(dados: DescobrirVagasEntrada): Promise<VagaDescoberta[]> {
    const resposta = await this.requisitar<Listagem<VagaDescoberta>>(
      "POST",
      "/v1/vagas/descobrir",
      {
        corpo: dados,
        ia: true,
      },
    );
    return resposta.items;
  }

  candidatarVagaExterna(dados: CandidatarVagaExternaEntrada): Promise<CandidaturaExterna> {
    return this.requisitar("POST", "/v1/vagas/descobertas/candidaturas", {
      corpo: dados,
      ia: true,
    });
  }

  listarCandidaturas(perfil: string): Promise<CandidaturasPorStatus> {
    return this.requisitar("GET", "/v1/candidaturas", { query: { perfil_identificador: perfil } });
  }

  criarCandidatura(dados: CriarCandidaturaEntrada): Promise<Candidatura> {
    return this.requisitar("POST", "/v1/candidaturas", { corpo: dados });
  }

  confirmarCandidaturaAjustada(dados: ConfirmarCandidaturaEntrada): Promise<Candidatura> {
    return this.requisitar("POST", "/v1/candidaturas-ajustadas", { corpo: dados });
  }

  moverCandidatura(
    id: string,
    novoStatus: StatusCandidatura,
    posicao?: number,
  ): Promise<Candidatura> {
    return this.requisitar("POST", caminho`/v1/candidaturas/${id}/submissao`, {
      corpo: {
        novo_status: novoStatus.toLowerCase(),
        ...(posicao === undefined ? {} : { posicao }),
      },
    });
  }

  criarTokenCaptura(perfil: string): Promise<TokenCaptura> {
    return this.requisitar("POST", "/v1/tokens-captura", {
      corpo: { perfil_identificador: perfil },
    });
  }

  private async requisitar<T>(
    metodo: Metodo,
    rota: string,
    requisicao: Requisicao = {},
  ): Promise<T> {
    const controle = new AbortController();
    const timeout = setTimeout(
      () => controle.abort(),
      requisicao.ia ? this.timeoutIaMs : this.timeoutPadraoMs,
    );
    try {
      const resposta = await fetch(this.montarUrl(rota, requisicao.query), {
        method: metodo,
        headers:
          requisicao.corpo === undefined ? undefined : { "Content-Type": "application/json" },
        body: requisicao.corpo === undefined ? undefined : JSON.stringify(requisicao.corpo),
        signal: controle.signal,
        credentials: "include",
      });
      return await this.lerResposta<T>(resposta);
    } catch (erro) {
      if (erro instanceof ApiError) throw erro;
      throw controle.signal.aborted ? ApiError.tempoEsgotado() : ApiError.semConexao();
    } finally {
      clearTimeout(timeout);
    }
  }

  private montarUrl(rota: string, query?: Record<string, string>): string {
    const parametros = query ? `?${new URLSearchParams(query).toString()}` : "";
    return `${this.baseUrl}${rota}${parametros}`;
  }

  private async lerResposta<T>(resposta: Response): Promise<T> {
    if (resposta.ok) {
      return (resposta.status === 204 ? undefined : await resposta.json()) as T;
    }
    const corpo: unknown = await resposta.json().catch(() => null);
    if (ehProblema(corpo)) throw ApiError.deProblema(corpo);
    throw new ApiError(resposta.status, "Erro inesperado da API", resposta.statusText);
  }
}
