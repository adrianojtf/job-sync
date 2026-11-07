import type { ApiClient } from "./api-client";
import { ApiError } from "./api-error";
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
  Problema,
  SalvarCurriculoEntrada,
  StatusCandidatura,
  SugerirAjusteExperienciaAdaptadaEntrada,
  SugerirAjusteExperienciaEntrada,
  SugerirAjusteSecaoEntrada,
  SugestaoExperiencia,
  SugestaoExperienciaAdaptada,
  SugestaoSecao,
  TokenCaptura,
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

  obterOuCriarPerfil(identificador: string): Promise<Perfil> {
    return this.requisitar("GET", caminho`/v1/perfis/${identificador}`);
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

  moverCandidatura(id: string, novoStatus: StatusCandidatura): Promise<Candidatura> {
    return this.requisitar("POST", caminho`/v1/candidaturas/${id}/submissao`, {
      corpo: { novo_status: novoStatus.toLowerCase() },
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
