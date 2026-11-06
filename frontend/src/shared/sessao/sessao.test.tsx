import { act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { CHAVE_SESSAO } from "./sessao-context";
import { SessaoProvider } from "./SessaoProvider";
import { useSessao } from "./use-sessao";

const wrapper = ({ children }: { children: ReactNode }) => (
  <SessaoProvider>{children}</SessaoProvider>
);

describe("SessaoProvider", () => {
  it("começa sem perfil quando nada foi salvo", () => {
    const { result } = renderHook(() => useSessao(), { wrapper });

    expect(result.current.perfil).toBeNull();
  });

  it("entrar expõe e persiste o perfil", () => {
    const { result } = renderHook(() => useSessao(), { wrapper });

    act(() => result.current.entrar("adriano"));

    expect(result.current.perfil).toBe("adriano");
    expect(localStorage.getItem(CHAVE_SESSAO)).toBe("adriano");
  });

  it("restaura o perfil salvo ao recarregar", () => {
    localStorage.setItem(CHAVE_SESSAO, "adriano");

    const { result } = renderHook(() => useSessao(), { wrapper });

    expect(result.current.perfil).toBe("adriano");
  });

  it("sair limpa o perfil e o armazenamento", () => {
    localStorage.setItem(CHAVE_SESSAO, "adriano");
    const { result } = renderHook(() => useSessao(), { wrapper });

    act(() => result.current.sair());

    expect(result.current.perfil).toBeNull();
    expect(localStorage.getItem(CHAVE_SESSAO)).toBeNull();
  });

  it("continua funcionando em memória quando o armazenamento falha", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("bloqueado");
    });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("bloqueado");
    });
    const { result } = renderHook(() => useSessao(), { wrapper });

    act(() => result.current.entrar("adriano"));

    expect(result.current.perfil).toBe("adriano");
    vi.restoreAllMocks();
  });
});
