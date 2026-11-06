import { ApiError } from "../api/api-error";

/** Registra a falha no console com os dados que ligam o erro aos logs do backend. */
export function registrarErro(erro: unknown): void {
  if (erro instanceof ApiError) {
    console.error("[job-sync] Erro da API", {
      status: erro.status,
      title: erro.title,
      instance: erro.instance,
    });
    return;
  }
  console.error("[job-sync] Erro inesperado", erro);
}
