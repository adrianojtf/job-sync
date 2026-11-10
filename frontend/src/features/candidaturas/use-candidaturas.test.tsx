import { QueryClient } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import type { ApiClient } from "../../api/api-client";
import type { Candidatura, CandidaturasPorStatus } from "../../api/tipos";
import { AppProviders } from "../../app/AppProviders";
import { CHAVE_SESSAO } from "../../shared/sessao/sessao-context";
import { chaveCandidaturas, useMoverCandidatura } from "./use-candidaturas";

const notificar = vi.fn();
vi.mock("../../shared/ui/use-toast", () => ({ useToast: () => ({ notificar }) }));

const cartao = (id: string, status: string, posicao: number): Candidatura => ({
  id,
  perfil_identificador: "adriano",
  vaga_id: "v",
  curriculo_salvo_id: "c",
  empresa: "Empresa",
  cargo: `Cargo ${id}`,
  status,
  data_aplicacao: "2026-11-02T09:00:00",
  historico_status: [],
  posicao,
});

const inicial = (): CandidaturasPorStatus => ({
  por_status: {
    APLICADO: [cartao("a", "APLICADO", 0), cartao("b", "APLICADO", 1)],
    ENTREVISTA: [],
    OFERTA: [],
    REJEITADO: [],
  },
  total: 2,
});

interface Adiado {
  resolver: () => void;
  rejeitar: (erro: Error) => void;
}

function prepararApi() {
  const pendentes: Adiado[] = [];
  const moverCandidatura = vi.fn<ApiClient["moverCandidatura"]>(
    () =>
      new Promise<Candidatura>((resolver, rejeitar) => {
        pendentes.push({ resolver: () => resolver(cartao("a", "ENTREVISTA", 0)), rejeitar });
      }),
  );
  const api = { moverCandidatura, listarCandidaturas: vi.fn() } as unknown as ApiClient;
  return { api, moverCandidatura, pendentes };
}

function montar(api: ApiClient) {
  localStorage.setItem(CHAVE_SESSAO, "adriano");
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  queryClient.setQueryData(chaveCandidaturas("adriano"), inicial());
  const wrapper = ({ children }: { children: ReactNode }) => (
    <AppProviders apiClient={api} queryClient={queryClient}>
      {children}
    </AppProviders>
  );
  const hook = renderHook(() => useMoverCandidatura(), { wrapper });
  const ler = () => queryClient.getQueryData<CandidaturasPorStatus>(chaveCandidaturas("adriano"))!;
  return { ...hook, ler, queryClient };
}

const ids = (q: CandidaturasPorStatus, status: string) =>
  (q.por_status?.[status] ?? []).map((c) => c.id);

describe("useMoverCandidatura", () => {
  beforeEach(() => notificar.mockClear());

  it("atualiza o quadro no cache antes de a API responder", async () => {
    const { api } = prepararApi();
    const { result, ler } = montar(api);

    act(() => result.current.mutate({ id: "a", novoStatus: "ENTREVISTA", posicao: 0 }));

    await waitFor(() => expect(ids(ler(), "ENTREVISTA")).toEqual(["a"]));
    expect(ids(ler(), "APLICADO")).toEqual(["b"]);
  });

  it("sem posição, coloca o cartão no topo da coluna de destino", async () => {
    const { api } = prepararApi();
    const { result, ler } = montar(api);
    act(() => result.current.mutate({ id: "b", novoStatus: "APLICADO" }));
    await waitFor(() => expect(ids(ler(), "APLICADO")).toEqual(["b", "a"]));
  });

  it("envia id, status e posição à API", async () => {
    const { api, moverCandidatura } = prepararApi();
    const { result } = montar(api);

    act(() => result.current.mutate({ id: "a", novoStatus: "OFERTA", posicao: 1 }));

    await waitFor(() => expect(moverCandidatura).toHaveBeenCalledWith("a", "OFERTA", 1));
  });

  it("restaura o quadro anterior quando a API falha", async () => {
    const { api, pendentes } = prepararApi();
    const { result, ler } = montar(api);
    act(() => result.current.mutate({ id: "a", novoStatus: "ENTREVISTA", posicao: 0 }));
    await waitFor(() => expect(ids(ler(), "ENTREVISTA")).toEqual(["a"]));

    await act(async () => pendentes[0]!.rejeitar(new Error("falhou")));

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(ids(ler(), "APLICADO")).toEqual(["a", "b"]);
    expect(ids(ler(), "ENTREVISTA")).toEqual([]);
  });

  it("executa dois movimentos em sequência, um de cada vez", async () => {
    const { api, moverCandidatura, pendentes } = prepararApi();
    const { result, ler } = montar(api);

    act(() => {
      result.current.mutate({ id: "a", novoStatus: "ENTREVISTA", posicao: 0 });
      result.current.mutate({ id: "b", novoStatus: "ENTREVISTA", posicao: 0 });
    });

    await waitFor(() => expect(moverCandidatura).toHaveBeenCalledTimes(1));
    await act(async () => pendentes[0]!.resolver());
    await waitFor(() => expect(moverCandidatura).toHaveBeenCalledTimes(2));
    expect(moverCandidatura.mock.calls.map((chamada) => chamada[0])).toEqual(["a", "b"]);
    await act(async () => pendentes[1]!.resolver());
    await waitFor(() => expect(ids(ler(), "ENTREVISTA")).toEqual(["b", "a"]));
  });

  it("invalida o quadro ao terminar", async () => {
    const { api, pendentes } = prepararApi();
    const { result, queryClient } = montar(api);
    act(() => result.current.mutate({ id: "a", novoStatus: "OFERTA", posicao: 0 }));
    await waitFor(() => expect(pendentes).toHaveLength(1));

    await act(async () => pendentes[0]!.resolver());

    await waitFor(() =>
      expect(queryClient.getQueryState(chaveCandidaturas("adriano"))?.isInvalidated).toBe(true),
    );
  });
});
