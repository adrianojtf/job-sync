import { MutationCache, QueryCache, QueryClient } from "@tanstack/react-query";
import { ApiError } from "../api/api-error";
import { CHAVE_QUERY_SESSAO } from "../shared/sessao/sessao-context";

export function criarQueryClient(): QueryClient {
  // Qualquer 401 significa sessão expirada ou encerrada: as guardas levam a /entrar.
  const aoFalhar = (erro: unknown) => {
    if (erro instanceof ApiError && erro.status === 401) {
      queryClient.setQueryData(CHAVE_QUERY_SESSAO, null);
    }
  };
  const queryClient: QueryClient = new QueryClient({
    queryCache: new QueryCache({ onError: aoFalhar }),
    mutationCache: new MutationCache({ onError: aoFalhar }),
    defaultOptions: {
      queries: { retry: 1, refetchOnWindowFocus: false },
      mutations: { retry: false },
    },
  });
  return queryClient;
}
