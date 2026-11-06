import { render, screen } from "@testing-library/react";
import { ErrorBoundary } from "./ErrorBoundary";

function Quebrado(): never {
  throw new Error("falha de renderização");
}

describe("ErrorBoundary", () => {
  it("mostra a tela de falha com a ação de recarregar", () => {
    vi.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <Quebrado />
      </ErrorBoundary>,
    );

    expect(screen.getByRole("heading", { name: "Algo deu errado" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Recarregar" })).toBeInTheDocument();
    vi.restoreAllMocks();
  });

  it("renderiza os filhos quando não há erro", () => {
    render(
      <ErrorBoundary>
        <p>conteúdo</p>
      </ErrorBoundary>,
    );

    expect(screen.getByText("conteúdo")).toBeInTheDocument();
  });
});
