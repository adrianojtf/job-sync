import { createContext, useContext } from "react";
import type { ApiClient } from "./api-client";

export const ApiClientContext = createContext<ApiClient | null>(null);

/** Devolve o ApiClient injetado pelo ApiClientProvider. */
export function useApiClient(): ApiClient {
  const cliente = useContext(ApiClientContext);
  if (cliente === null) {
    throw new Error("useApiClient precisa estar dentro de <ApiClientProvider>.");
  }
  return cliente;
}
