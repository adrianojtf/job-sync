import { render } from "@testing-library/react";
import { StrictMode } from "react";
import { createMemoryRouter, parsePath, RouterProvider } from "react-router-dom";
import type { ApiClient } from "../api/api-client";
import { HttpApiClient } from "../api/http-api-client";
import { AppProviders } from "../app/AppProviders";
import { criarQueryClient } from "../app/query-client";
import { OPCOES_ROUTER, rotas } from "../app/rotas";
import { CHAVE_QUERY_SESSAO } from "../shared/sessao/sessao-context";

import { API_TESTE } from "./servidor-api";
import { usuarioDeTeste } from "./usuario-de-teste";

export { API_TESTE };

interface Opcoes {
  caminho?: string;
  /** Estado do histórico da entrada inicial (ex.: para simular um recarregamento da página). */
  estado?: unknown;
  /** Perfil da sessão já aberta. Sem ele, a aplicação começa sem sessão. */
  perfil?: string;
  apiClient?: ApiClient;
  /** Deixa a aplicação perguntar ao servidor se há sessão, em vez de começar com ela definida. */
  consultarSessao?: boolean;
}

/** Renderiza a aplicação completa (providers + rotas) em memória, como o usuário a vê. */
export function renderizarApp({
  caminho = "/",
  estado,
  perfil,
  apiClient,
  consultarSessao = false,
}: Opcoes = {}) {
  const router = createMemoryRouter(rotas, {
    initialEntries: [{ ...parsePath(caminho), state: estado }],
    ...OPCOES_ROUTER,
  });
  const queryClient = criarQueryClient();
  queryClient.setDefaultOptions({ queries: { retry: false } });
  if (!consultarSessao) {
    queryClient.setQueryData(CHAVE_QUERY_SESSAO, perfil ? usuarioDeTeste(perfil) : null);
  }
  // StrictMode como em main.tsx: revela efeitos que quebram com a montagem dupla do React.
  render(
    <StrictMode>
      <AppProviders
        apiClient={apiClient ?? new HttpApiClient({ baseUrl: API_TESTE })}
        queryClient={queryClient}
      >
        <RouterProvider router={router} future={{ v7_startTransition: true }} />
      </AppProviders>
    </StrictMode>,
  );
  return { router, queryClient };
}
