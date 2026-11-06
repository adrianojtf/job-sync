import { render } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import type { ApiClient } from "../api/api-client";
import { HttpApiClient } from "../api/http-api-client";
import { AppProviders } from "../app/AppProviders";
import { criarQueryClient } from "../app/query-client";
import { OPCOES_ROUTER, rotas } from "../app/rotas";
import { CHAVE_SESSAO } from "../shared/sessao/sessao-context";

export const API_TESTE = "http://api.test";

interface Opcoes {
  caminho?: string;
  perfil?: string;
  apiClient?: ApiClient;
}

/** Renderiza a aplicação completa (providers + rotas) em memória, como o usuário a vê. */
export function renderizarApp({ caminho = "/", perfil, apiClient }: Opcoes = {}) {
  if (perfil) localStorage.setItem(CHAVE_SESSAO, perfil);
  const router = createMemoryRouter(rotas, { initialEntries: [caminho], ...OPCOES_ROUTER });
  const queryClient = criarQueryClient();
  queryClient.setDefaultOptions({ queries: { retry: false } });
  render(
    <AppProviders
      apiClient={apiClient ?? new HttpApiClient({ baseUrl: API_TESTE })}
      queryClient={queryClient}
    >
      <RouterProvider router={router} future={{ v7_startTransition: true }} />
    </AppProviders>,
  );
  return { router };
}
