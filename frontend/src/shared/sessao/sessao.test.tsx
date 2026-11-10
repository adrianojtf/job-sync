import { QueryClient } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import type { ReactNode } from "react";
import { HttpApiClient } from "../../api/http-api-client";
import { AppProviders } from "../../app/AppProviders";
import { criarQueryClient } from "../../app/query-client";
import { API_TESTE } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";
import { usuarioDeTeste } from "../../test/usuario-de-teste";
import { CHAVE_QUERY_SESSAO } from "./sessao-context";
import { useSessao } from "./use-sessao";

function montar(queryClient: QueryClient = criarQueryClient()) {
  queryClient.setDefaultOptions({ queries: { retry: false } });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <AppProviders apiClient={new HttpApiClient({ baseUrl: API_TESTE })} queryClient={queryClient}>
      {children}
    </AppProviders>
  );
  return { queryClient, ...renderHook(() => useSessao(), { wrapper }) };
}

const usuarioDoServidor = {
  id: "1",
  email: "ana@exemplo.com",
  nome: "Ana",
  perfil_identificador: "u-ana",
};

describe("SessaoProvider", () => {
  it("fica carregando até o servidor responder e depois expõe que não há sessão", async () => {
    const { result } = montar();

    expect(result.current.carregando).toBe(true);
    await waitFor(() => expect(result.current.carregando).toBe(false));
    expect(result.current.perfil).toBeNull();
    expect(result.current.usuario).toBeNull();
  });

  it("expõe o usuário e o perfil devolvidos pelo servidor", async () => {
    servidorApi.use(
      http.get(`${API_TESTE}/v1/usuarios/me`, () => HttpResponse.json(usuarioDoServidor)),
    );

    const { result } = montar();

    await waitFor(() => expect(result.current.perfil).toBe("u-ana"));
    expect(result.current.usuario?.email).toBe("ana@exemplo.com");
    expect(result.current.carregando).toBe(false);
  });

  it("não guarda nada em localStorage", async () => {
    servidorApi.use(
      http.get(`${API_TESTE}/v1/usuarios/me`, () => HttpResponse.json(usuarioDoServidor)),
    );

    const { result } = montar();
    await waitFor(() => expect(result.current.perfil).toBe("u-ana"));

    expect(localStorage.length).toBe(0);
  });

  it("entrar registra o usuário sem nova consulta ao servidor", async () => {
    const { result } = montar();
    await waitFor(() => expect(result.current.carregando).toBe(false));

    act(() => result.current.entrar(usuarioDeTeste("adriano")));

    await waitFor(() => expect(result.current.perfil).toBe("adriano"));
  });

  it("sair encerra a sessão no servidor e descarta os dados em memória", async () => {
    let chamadas = 0;
    servidorApi.use(
      http.delete(`${API_TESTE}/v1/sessoes/atual`, () => {
        chamadas += 1;
        return new HttpResponse(null, { status: 204 });
      }),
    );
    const { result, queryClient } = montar();
    await waitFor(() => expect(result.current.carregando).toBe(false));
    act(() => result.current.entrar(usuarioDeTeste("adriano")));
    await waitFor(() => expect(result.current.perfil).toBe("adriano"));
    queryClient.setQueryData(["candidaturas", "adriano"], { total: 1 });

    await act(() => result.current.sair());

    expect(chamadas).toBe(1);
    await waitFor(() => expect(result.current.perfil).toBeNull());
    expect(queryClient.getQueryData(["candidaturas", "adriano"])).toBeUndefined();
  });

  it("sair limpa a sessão local mesmo se o servidor falhar", async () => {
    servidorApi.use(http.delete(`${API_TESTE}/v1/sessoes/atual`, () => HttpResponse.error()));
    const { result } = montar();
    await waitFor(() => expect(result.current.carregando).toBe(false));
    act(() => result.current.entrar(usuarioDeTeste("adriano")));
    await waitFor(() => expect(result.current.perfil).toBe("adriano"));

    await act(async () => {
      await result.current.sair().catch(() => undefined);
    });

    await waitFor(() => expect(result.current.perfil).toBeNull());
  });

  it("uma consulta que recebe 401 derruba a sessão", async () => {
    const { result, queryClient } = montar();
    await waitFor(() => expect(result.current.carregando).toBe(false));
    act(() => result.current.entrar(usuarioDeTeste("adriano")));
    await waitFor(() => expect(result.current.perfil).toBe("adriano"));
    servidorApi.use(
      http.get(`${API_TESTE}/v1/candidaturas`, () =>
        HttpResponse.json(
          { type: "t", title: "Não autenticado", status: 401, detail: "x", instance: "i" },
          { status: 401 },
        ),
      ),
    );

    await act(async () => {
      await queryClient
        .fetchQuery({
          queryKey: ["candidaturas", "adriano"],
          queryFn: () => new HttpApiClient({ baseUrl: API_TESTE }).listarCandidaturas("adriano"),
        })
        .catch(() => undefined);
    });

    await waitFor(() => expect(result.current.perfil).toBeNull());
    expect(queryClient.getQueryData(CHAVE_QUERY_SESSAO)).toBeNull();
  });
});
