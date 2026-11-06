import { render, screen } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { HttpApiClient } from "../api/http-api-client";
import { servidorApi } from "../test/servidor-api";
import { App } from "./App";
import { AppProviders } from "./AppProviders";
import { criarQueryClient } from "./query-client";

const BASE = "http://api.test";

function renderizarApp() {
  const queryClient = criarQueryClient();
  queryClient.setDefaultOptions({ queries: { retry: false } });
  render(
    <AppProviders apiClient={new HttpApiClient({ baseUrl: BASE })} queryClient={queryClient}>
      <App />
    </AppProviders>,
  );
}

describe("App", () => {
  it("mostra que a API está disponível", async () => {
    servidorApi.use(http.get(`${BASE}/v1/health`, () => HttpResponse.json({ status: "ok" })));

    renderizarApp();

    expect(await screen.findByText("API disponível")).toBeInTheDocument();
  });

  it("mostra a mensagem do erro quando a API falha", async () => {
    servidorApi.use(http.get(`${BASE}/v1/health`, () => HttpResponse.error()));

    renderizarApp();

    expect(
      await screen.findByText(/API indisponível: Não foi possível falar com a API/),
    ).toBeInTheDocument();
  });
});
