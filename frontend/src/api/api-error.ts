import type { Problema } from "./tipos";

/** Erro de chamada à API, normalizado a partir do ProblemaResponse (RFC 7807). */
export class ApiError extends Error {
  readonly status: number;
  readonly title: string;
  readonly detail: string;
  readonly instance: string | null;

  constructor(status: number, title: string, detail = "", instance: string | null = null) {
    super(detail || title);
    this.name = "ApiError";
    this.status = status;
    this.title = title;
    this.detail = detail;
    this.instance = instance;
  }

  static deProblema(problema: Problema): ApiError {
    return new ApiError(problema.status, problema.title, problema.detail, problema.instance);
  }

  static tempoEsgotado(): ApiError {
    return new ApiError(0, "Tempo esgotado", "A API demorou mais que o esperado para responder.");
  }

  static semConexao(): ApiError {
    return new ApiError(0, "Falha de conexão", "Não foi possível falar com a API.");
  }
}
