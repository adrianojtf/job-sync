import { renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import type { ApiClient } from "./api-client";
import { useApiClient } from "./api-client-context";
import { ApiClientProvider } from "./ApiClientProvider";

describe("useApiClient", () => {
  it("devolve o cliente injetado pelo provider", () => {
    const cliente = {} as ApiClient;
    const wrapper = ({ children }: { children: ReactNode }) => (
      <ApiClientProvider cliente={cliente}>{children}</ApiClientProvider>
    );

    const { result } = renderHook(() => useApiClient(), { wrapper });

    expect(result.current).toBe(cliente);
  });

  it("falha com mensagem clara fora do provider", () => {
    vi.spyOn(console, "error").mockImplementation(() => {});

    expect(() => renderHook(() => useApiClient())).toThrow(/ApiClientProvider/);
  });
});
