import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { Modal } from "./Modal";

function ModalDeTeste({ aoFechar = () => {} }: { aoFechar?: () => void }) {
  const [aberto, setAberto] = useState(false);
  return (
    <>
      <button onClick={() => setAberto(true)}>Abrir</button>
      <Modal
        aberto={aberto}
        titulo="Ajustar currículo para uma vaga"
        descricao="Adicione os dados da oportunidade."
        aoFechar={() => {
          aoFechar();
          setAberto(false);
        }}
      >
        <input aria-label="Título da vaga" />
      </Modal>
    </>
  );
}

describe("Modal", () => {
  it("não renderiza quando fechado", () => {
    render(<ModalDeTeste />);

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("abre como diálogo modal rotulado pelo título e leva o foco para dentro", async () => {
    render(<ModalDeTeste />);

    await userEvent.click(screen.getByRole("button", { name: "Abrir" }));

    const dialogo = screen.getByRole("dialog", { name: "Ajustar currículo para uma vaga" });
    expect(dialogo).toHaveAttribute("aria-modal", "true");
    expect(dialogo).toHaveAccessibleDescription("Adicione os dados da oportunidade.");
    expect(screen.getByLabelText("Título da vaga")).toHaveFocus();
  });

  it("fecha com Esc e devolve o foco ao botão que abriu", async () => {
    const aoFechar = vi.fn();
    render(<ModalDeTeste aoFechar={aoFechar} />);
    await userEvent.click(screen.getByRole("button", { name: "Abrir" }));

    await userEvent.keyboard("{Escape}");

    expect(aoFechar).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Abrir" })).toHaveFocus();
  });

  it("fecha ao clicar fora do conteúdo", async () => {
    const aoFechar = vi.fn();
    render(<ModalDeTeste aoFechar={aoFechar} />);
    await userEvent.click(screen.getByRole("button", { name: "Abrir" }));

    await userEvent.click(screen.getByTestId("modal-fundo"));

    expect(aoFechar).toHaveBeenCalledTimes(1);
  });

  it("não fecha ao clicar dentro do conteúdo", async () => {
    const aoFechar = vi.fn();
    render(<ModalDeTeste aoFechar={aoFechar} />);
    await userEvent.click(screen.getByRole("button", { name: "Abrir" }));

    await userEvent.click(screen.getByLabelText("Título da vaga"));

    expect(aoFechar).not.toHaveBeenCalled();
  });

  it("fecha pelo botão de fechar", async () => {
    const aoFechar = vi.fn();
    render(<ModalDeTeste aoFechar={aoFechar} />);
    await userEvent.click(screen.getByRole("button", { name: "Abrir" }));

    await userEvent.click(screen.getByRole("button", { name: "Fechar" }));

    expect(aoFechar).toHaveBeenCalledTimes(1);
  });
});

describe("Modal com foco fora do diálogo", () => {
  it("fecha com Esc mesmo quando o foco foi para o body", async () => {
    const aoFechar = vi.fn();
    render(
      <Modal aberto titulo="Diálogo" aoFechar={aoFechar}>
        <input aria-label="Campo" />
      </Modal>,
    );
    (document.activeElement as HTMLElement).blur();

    await userEvent.keyboard("{Escape}");

    expect(aoFechar).toHaveBeenCalledTimes(1);
  });
});
