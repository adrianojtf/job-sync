import { QueryClient } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import type { ReactNode } from "react";
import { HttpApiClient } from "../../api/http-api-client";
import { AppProviders } from "../../app/AppProviders";
import { CHAVE_QUERY_SESSAO } from "../../shared/sessao/sessao-context";
import { PERFIL_ESTRUTURADO } from "../../test/fixtures";
import { API_TESTE } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";
import { usuarioDeTeste } from "../../test/usuario-de-teste";
import { FONTE_PERFIL, useFontesCurriculo } from "./fonte-curriculo";

const CURRICULO = {
  id: "c1",
  perfil_identificador: "adriano",
  nome_referencia: "CV LinkedIn",
  data_upload: "2026-11-01T10:00:00",
};

function montar() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  queryClient.setQueryData(CHAVE_QUERY_SESSAO, usuarioDeTeste("adriano"));
  const wrapper = ({ children }: { children: ReactNode }) => (
    <AppProviders apiClient={new HttpApiClient({ baseUrl: API_TESTE })} queryClient={queryClient}>
      {children}
    </AppProviders>
  );
  return renderHook(() => useFontesCurriculo(), { wrapper });
}

const atrasar = (ms: number) => new Promise((resolver) => setTimeout(resolver, ms));

describe("useFontesCurriculo", () => {
  it("prefere o perfil mestre mesmo quando a lista de PDFs chega primeiro", async () => {
    servidorApi.use(
      http.get(`${API_TESTE}/v1/curriculos`, () =>
        HttpResponse.json({ items: [CURRICULO], total: 1 }),
      ),
      http.get(`${API_TESTE}/v1/perfil-estruturado/:perfil`, async () => {
        await atrasar(80);
        return HttpResponse.json(PERFIL_ESTRUTURADO);
      }),
    );

    const { result } = montar();

    await waitFor(() => expect(result.current.carregando).toBe(false));
    expect(result.current.padrao).toBe(FONTE_PERFIL);
  });

  it("não define um padrão enquanto alguma das consultas está pendente", async () => {
    servidorApi.use(
      http.get(`${API_TESTE}/v1/curriculos`, () =>
        HttpResponse.json({ items: [CURRICULO], total: 1 }),
      ),
      http.get(`${API_TESTE}/v1/perfil-estruturado/:perfil`, async () => {
        await atrasar(80);
        return HttpResponse.json(PERFIL_ESTRUTURADO);
      }),
    );

    const { result } = montar();
    await waitFor(() => expect(result.current.opcoes.length).toBeGreaterThan(0));

    expect(result.current.carregando).toBe(true);
    expect(result.current.padrao).toBe("");
  });

  it("sem perfil mestre, usa o primeiro PDF da biblioteca", async () => {
    servidorApi.use(
      http.get(`${API_TESTE}/v1/curriculos`, () =>
        HttpResponse.json({ items: [CURRICULO], total: 1 }),
      ),
    );

    const { result } = montar();

    await waitFor(() => expect(result.current.carregando).toBe(false));
    expect(result.current.padrao).toBe("c1");
  });

  it("sem nenhuma fonte, o padrão fica vazio", async () => {
    const { result } = montar();

    await waitFor(() => expect(result.current.carregando).toBe(false));
    expect(result.current.padrao).toBe("");
    expect(result.current.opcoes).toEqual([]);
  });
});
