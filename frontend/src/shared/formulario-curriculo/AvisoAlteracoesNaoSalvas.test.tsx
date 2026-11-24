import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createRef, useState } from "react";
import { createMemoryRouter, Link, RouterProvider } from "react-router-dom";
import { AvisoAlteracoesNaoSalvas } from "./AvisoAlteracoesNaoSalvas";

function Tela({ inicial = false, saida }: { inicial?: boolean; saida?: React.RefObject<boolean> }) {
  const [alterado, setAlterado] = useState(inicial);
  return (
    <>
      <button onClick={() => setAlterado((atual) => !atual)}>Alternar alteração</button>
      <Link to="/outra">Ir para outra</Link>
      <Link to="/?busca=1">Mesma tela</Link>
      <AvisoAlteracoesNaoSalvas alterado={alterado} saidaConfirmada={saida} />
    </>
  );
}

function renderizar(props: Parameters<typeof Tela>[0] = {}) {
  const router = createMemoryRouter(
    [
      { path: "/", element: <Tela {...props} /> },
      { path: "/outra", element: <p>Outra tela</p> },
    ],
    { initialEntries: ["/"] },
  );
  render(<RouterProvider router={router} />);
  return router;
}

describe("AvisoAlteracoesNaoSalvas", () => {
  it("sem alterações navega direto, sem perguntar", async () => {
    renderizar();

    await userEvent.click(screen.getByRole("link", { name: "Ir para outra" }));

    expect(screen.getByText("Outra tela")).toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("com alterações pergunta antes de sair e fica na tela até o usuário decidir", async () => {
    renderizar({ inicial: true });

    await userEvent.click(screen.getByRole("link", { name: "Ir para outra" }));

    expect(screen.getByRole("dialog", { name: "Sair sem salvar?" })).toBeInTheDocument();
    expect(screen.queryByText("Outra tela")).not.toBeInTheDocument();
  });

  it("Cancelar mantém o usuário na tela", async () => {
    renderizar({ inicial: true });
    await userEvent.click(screen.getByRole("link", { name: "Ir para outra" }));

    await userEvent.click(screen.getByRole("button", { name: "Cancelar" }));

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Ir para outra" })).toBeInTheDocument();
  });

  it("Sair sem salvar leva para a outra tela", async () => {
    renderizar({ inicial: true });
    await userEvent.click(screen.getByRole("link", { name: "Ir para outra" }));

    await userEvent.click(screen.getByRole("button", { name: "Sair sem salvar" }));

    expect(await screen.findByText("Outra tela")).toBeInTheDocument();
  });

  it("depois que as alterações acabam (salvou), navega direto", async () => {
    renderizar({ inicial: true });
    await userEvent.click(screen.getByRole("button", { name: "Alternar alteração" }));

    await userEvent.click(screen.getByRole("link", { name: "Ir para outra" }));

    expect(screen.getByText("Outra tela")).toBeInTheDocument();
  });

  it("mudar só a busca da mesma tela não pergunta", async () => {
    renderizar({ inicial: true });

    await userEvent.click(screen.getByRole("link", { name: "Mesma tela" }));

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("saída já confirmada em outro diálogo não pergunta de novo", async () => {
    const saida = createRef<boolean>() as { current: boolean };
    saida.current = true;
    renderizar({ inicial: true, saida });

    await userEvent.click(screen.getByRole("link", { name: "Ir para outra" }));

    expect(screen.getByText("Outra tela")).toBeInTheDocument();
  });

  it("ao fechar ou recarregar a aba com alterações, aciona o aviso do navegador", () => {
    renderizar({ inicial: true });
    const evento = new Event("beforeunload", { cancelable: true });

    act(() => {
      window.dispatchEvent(evento);
    });

    expect(evento.defaultPrevented).toBe(true);
  });

  it("sem alterações o navegador não é avisado", () => {
    renderizar();
    const evento = new Event("beforeunload", { cancelable: true });

    act(() => {
      window.dispatchEvent(evento);
    });

    expect(evento.defaultPrevented).toBe(false);
  });

  it("fora de um roteador de dados não quebra e não bloqueia nada", () => {
    render(<AvisoAlteracoesNaoSalvas alterado />);

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
