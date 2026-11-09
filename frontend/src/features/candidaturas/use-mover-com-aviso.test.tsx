import { QueryClient } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import type { ApiClient } from "../../api/api-client";
import { AppProviders } from "../../app/AppProviders";
import { CHAVE_SESSAO } from "../../shared/sessao/sessao-context";
import { useMoverComAviso } from "./use-mover-com-aviso";

const notificar = vi.fn();
vi.mock("../../shared/ui/use-toast", () => ({ useToast: () => ({ notificar }) }));

function montar(moverCandidatura: ApiClient["moverCandidatura"]) {
  localStorage.setItem(CHAVE_SESSAO, "adriano");
  const api = { moverCandidatura } as unknown as ApiClient;
  const wrapper = ({ children }: { children: ReactNode }) => (
    <AppProviders apiClient={api} queryClient={new QueryClient()}>
      {children}
    </AppProviders>
  );
  return renderHook(() => useMoverComAviso(), { wrapper });
}

describe("useMoverComAviso", () => {
  beforeEach(() => notificar.mockClear());

  it("avisa o sucesso com o rótulo da coluna de destino", async () => {
    const mover = vi.fn().mockResolvedValue({});
    const { result } = montar(mover);

    act(() => result.current("cand-1", "ENTREVISTA", 0));

    await waitFor(() =>
      expect(notificar).toHaveBeenCalledWith("Candidatura movida para Entrevista.", "sucesso"),
    );
    expect(mover).toHaveBeenCalledWith("cand-1", "ENTREVISTA", 0);
  });

  it("avisa o erro com a mensagem da API", async () => {
    const mover = vi.fn().mockRejectedValue(new Error("Candidatura não encontrada."));
    const { result } = montar(mover);

    act(() => result.current("cand-1", "OFERTA"));

    await waitFor(() =>
      expect(notificar).toHaveBeenCalledWith("Candidatura não encontrada.", "erro"),
    );
  });
});
