import { QueryClientProvider, type QueryClient } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";
import type { ApiClient } from "../api/api-client";
import { ApiClientProvider } from "../api/ApiClientProvider";
import { HttpApiClient } from "../api/http-api-client";
import { SessaoProvider } from "../shared/sessao/SessaoProvider";
import { ToastProvider } from "../shared/ui/ToastProvider";
import { criarQueryClient } from "./query-client";

interface Props {
  children: ReactNode;
  /** Permite injetar outro adapter (ex.: fake em testes). Padrão: HttpApiClient. */
  apiClient?: ApiClient;
  queryClient?: QueryClient;
}

export function AppProviders({ children, apiClient, queryClient }: Props) {
  const [cliente] = useState<ApiClient>(
    () => apiClient ?? new HttpApiClient({ baseUrl: import.meta.env.VITE_API_BASE_URL }),
  );
  const [consultas] = useState(() => queryClient ?? criarQueryClient());
  return (
    <QueryClientProvider client={consultas}>
      <ApiClientProvider cliente={cliente}>
        <SessaoProvider>
          <ToastProvider>{children}</ToastProvider>
        </SessaoProvider>
      </ApiClientProvider>
    </QueryClientProvider>
  );
}
