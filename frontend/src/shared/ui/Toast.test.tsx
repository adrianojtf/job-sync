import { act, render, screen } from "@testing-library/react";
import { ToastProvider } from "./ToastProvider";
import { useToast } from "./use-toast";

function Disparador({ mensagem, tom }: { mensagem: string; tom?: "sucesso" | "erro" }) {
  const { notificar } = useToast();
  return <button onClick={() => notificar(mensagem, tom)}>Notificar</button>;
}

describe("Toast", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it("anuncia a mensagem em região viva e some depois do tempo", () => {
    render(
      <ToastProvider duracaoMs={2600}>
        <Disparador mensagem="Perfil salvo." />
      </ToastProvider>,
    );

    act(() => screen.getByRole("button", { name: "Notificar" }).click());

    expect(screen.getByRole("status")).toHaveTextContent("Perfil salvo.");

    act(() => vi.advanceTimersByTime(2600));

    expect(screen.getByRole("status")).toBeEmptyDOMElement();
  });

  it("usa role alert para mensagens de erro", () => {
    render(
      <ToastProvider>
        <Disparador mensagem="Falha ao salvar." tom="erro" />
      </ToastProvider>,
    );

    act(() => screen.getByRole("button", { name: "Notificar" }).click());

    expect(screen.getByRole("alert")).toHaveTextContent("Falha ao salvar.");
  });

  it("falha com mensagem clara fora do provider", () => {
    vi.spyOn(console, "error").mockImplementation(() => {});

    expect(() => render(<Disparador mensagem="x" />)).toThrow(/ToastProvider/);
  });
});
