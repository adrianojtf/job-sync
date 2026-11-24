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

function DisparadorComAcao({ aoClicar }: { aoClicar: () => void }) {
  const { notificar } = useToast();
  return (
    <button
      onClick={() =>
        notificar("Ordem alterada.", "info", { acao: { rotulo: "Desfazer", aoClicar } })
      }
    >
      Notificar
    </button>
  );
}

describe("Toast com ação", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it("mostra o botão da ação junto da mensagem", () => {
    render(
      <ToastProvider>
        <DisparadorComAcao aoClicar={vi.fn()} />
      </ToastProvider>,
    );

    act(() => screen.getByRole("button", { name: "Notificar" }).click());

    expect(screen.getByRole("status")).toHaveTextContent("Ordem alterada.");
    expect(screen.getByRole("button", { name: "Desfazer" })).toBeInTheDocument();
  });

  it("usar a ação chama o callback e fecha o aviso", () => {
    const aoClicar = vi.fn();
    render(
      <ToastProvider>
        <DisparadorComAcao aoClicar={aoClicar} />
      </ToastProvider>,
    );
    act(() => screen.getByRole("button", { name: "Notificar" }).click());

    act(() => screen.getByRole("button", { name: "Desfazer" }).click());

    expect(aoClicar).toHaveBeenCalledTimes(1);
    expect(screen.getByRole("status")).toBeEmptyDOMElement();
  });

  it("com ação o aviso dura cerca de 6 segundos", () => {
    render(
      <ToastProvider duracaoMs={2600}>
        <DisparadorComAcao aoClicar={vi.fn()} />
      </ToastProvider>,
    );
    act(() => screen.getByRole("button", { name: "Notificar" }).click());

    act(() => vi.advanceTimersByTime(2600));
    expect(screen.getByRole("button", { name: "Desfazer" })).toBeInTheDocument();

    act(() => vi.advanceTimersByTime(3400));
    expect(screen.queryByRole("button", { name: "Desfazer" })).not.toBeInTheDocument();
  });

  it("a duração informada no aviso prevalece", () => {
    function Curto() {
      const { notificar } = useToast();
      return (
        <button onClick={() => notificar("Oi.", "info", { duracaoMs: 1000 })}>Notificar</button>
      );
    }
    render(
      <ToastProvider>
        <Curto />
      </ToastProvider>,
    );
    act(() => screen.getByRole("button", { name: "Notificar" }).click());

    act(() => vi.advanceTimersByTime(1000));

    expect(screen.getByRole("status")).toBeEmptyDOMElement();
  });

  it("sem opções o aviso continua igual ao de antes", () => {
    render(
      <ToastProvider duracaoMs={2600}>
        <Disparador mensagem="Perfil salvo." />
      </ToastProvider>,
    );

    act(() => screen.getByRole("button", { name: "Notificar" }).click());

    expect(screen.queryByRole("button", { name: "Desfazer" })).not.toBeInTheDocument();
  });
});
