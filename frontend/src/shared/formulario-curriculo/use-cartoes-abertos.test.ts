import { act, renderHook } from "@testing-library/react";
import { lerChavesAbertas, useCartoesAbertos } from "./use-cartoes-abertos";

const CHAVE = "jobsync:perfil:cartoes:adriano:experiencias";
const itens = (ids: string[], chaves: string[]) => ({
  chaveDeArmazenamento: CHAVE,
  ids,
  chavesDosItens: chaves,
});

describe("useCartoesAbertos", () => {
  beforeEach(() => window.localStorage.clear());
  afterEach(() => vi.restoreAllMocks());

  it("começa com tudo recolhido quando nada foi guardado", () => {
    const { result } = renderHook(() => useCartoesAbertos(itens(["a", "b"], ["A", "B"])));

    expect(result.current.abertos.size).toBe(0);
  });

  it("abre os itens cuja chave foi guardada e ignora chaves que não existem mais", () => {
    window.localStorage.setItem(CHAVE, JSON.stringify(["B", "Removida"]));

    const { result } = renderHook(() => useCartoesAbertos(itens(["a", "b"], ["A", "B"])));

    expect([...result.current.abertos]).toEqual(["b"]);
  });

  it("guarda as chaves por conteúdo ao alternar", () => {
    const { result } = renderHook(() => useCartoesAbertos(itens(["a", "b"], ["A", "B"])));

    act(() => result.current.alternar("b"));

    expect(lerChavesAbertas(CHAVE)).toEqual(["B"]);
    act(() => result.current.alternar("b"));
    expect(lerChavesAbertas(CHAVE)).toEqual([]);
  });

  it("não guarda item sem chave (ainda vazio)", () => {
    const { result } = renderHook(() => useCartoesAbertos(itens(["a", "n"], ["A", ""])));

    act(() => result.current.alternar("a"));
    act(() => result.current.abrir("n"));

    expect(result.current.abertos.has("n")).toBe(true);
    expect(lerChavesAbertas(CHAVE)).toEqual(["A"]);
  });

  it("definir abre ou recolhe vários de uma vez e guarda", () => {
    const { result } = renderHook(() => useCartoesAbertos(itens(["a", "b"], ["A", "B"])));

    act(() => result.current.definir(new Set(["a", "b"])));
    expect(lerChavesAbertas(CHAVE)).toEqual(["A", "B"]);

    act(() => result.current.definir(new Set()));
    expect(lerChavesAbertas(CHAVE)).toEqual([]);
  });

  it("quando os ids mudam (formulário reiniciado), reabre pelo que foi guardado", () => {
    const { result, rerender } = renderHook((entrada) => useCartoesAbertos(entrada), {
      initialProps: itens(["a", "b"], ["A", "B"]),
    });
    act(() => result.current.alternar("a"));

    rerender(itens(["x", "y"], ["A", "B"]));

    expect([...result.current.abertos]).toEqual(["x"]);
  });

  it("remover um item tira do conjunto o que não existe mais", () => {
    const { result, rerender } = renderHook((entrada) => useCartoesAbertos(entrada), {
      initialProps: itens(["a", "b"], ["A", "B"]),
    });
    act(() => result.current.definir(new Set(["a", "b"])));

    rerender(itens(["b"], ["B"]));

    expect([...result.current.abertos]).toEqual(["b"]);
  });

  it("remover outro item não fecha um cartão aberto cujo título foi editado", () => {
    const { result, rerender } = renderHook((entrada) => useCartoesAbertos(entrada), {
      initialProps: itens(["a", "b"], ["A", "B"]),
    });
    act(() => result.current.alternar("a"));

    rerender(itens(["a"], ["A editado"]));

    expect([...result.current.abertos]).toEqual(["a"]);
  });

  it("sem chave de armazenamento não lê nem grava nada", () => {
    const gravar = vi.spyOn(Storage.prototype, "setItem");
    const { result } = renderHook(() => useCartoesAbertos({ ids: ["a"], chavesDosItens: ["A"] }));

    act(() => result.current.alternar("a"));

    expect(result.current.abertos.has("a")).toBe(true);
    expect(gravar).not.toHaveBeenCalled();
  });

  it("funciona quando o storage lança erro ao ler ou gravar", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("bloqueado");
    });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("cheio");
    });

    const { result } = renderHook(() => useCartoesAbertos(itens(["a"], ["A"])));
    act(() => result.current.alternar("a"));

    expect(result.current.abertos.has("a")).toBe(true);
  });

  it("texto inválido no storage vira lista vazia", () => {
    window.localStorage.setItem(CHAVE, "{não é json");

    expect(lerChavesAbertas(CHAVE)).toEqual([]);
  });
});
