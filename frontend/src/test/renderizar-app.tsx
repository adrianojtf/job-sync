import { render } from "@testing-library/react";
import { StrictMode } from "react";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import type { ApiClient } from "../api/api-client";
import { HttpApiClient } from "../api/http-api-client";
import { AppProviders } from "../app/AppProviders";
import { criarQueryClient } from "../app/query-client";
import { OPCOES_ROUTER, rotas } from "../app/rotas";
import { CHAVE_SESSAO } from "../shared/sessao/sessao-context";

import { API_TESTE } from "./servidor-api";

export { API_TESTE };

interface Opcoes {
  caminho?: string;
  /** Estado do histórico da entrada inicial (ex.: para simular um recarregamento da página). */
  estado?: unknown;
  perfil?: string;
  apiClient?: ApiClient;
}

/** Renderiza a aplicação completa (providers + rotas) em memória, como o usuário a vê. */
export function renderizarApp({ caminho = "/", estado, perfil, apiClient }: Opcoes = {}) {
  if (perfil) localStorage.setItem(CHAVE_SESSAO, perfil);
  const router = createMemoryRouter(rotas, {
    initialEntries: [{ pathname: caminho, state: estado }],
    ...OPCOES_ROUTER,
  });
  const queryClient = criarQueryClient();
  queryClient.setDefaultOptions({ queries: { retry: false } });
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
