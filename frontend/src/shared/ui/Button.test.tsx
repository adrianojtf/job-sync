import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "./Button";

describe("Button", () => {
  it("em carregamento mantém o foco, anuncia ocupado e ignora cliques", async () => {
    const aoClicar = vi.fn();
    render(
      <Button carregando onClick={aoClicar}>
        Salvar
      </Button>,
    );
    const botao = screen.getByRole("button", { name: "Salvar" });
    botao.focus();

    await userEvent.click(botao);

    expect(botao).not.toBeDisabled();
    expect(botao).toHaveAttribute("aria-disabled", "true");
    expect(botao).toHaveAttribute("aria-busy", "true");
    expect(botao).toHaveFocus();
    expect(aoClicar).not.toHaveBeenCalled();
  });

  it("em carregamento não envia o formulário", async () => {
    const aoEnviar = vi.fn((evento: Event) => evento.preventDefault());
    render(
      <form onSubmit={(evento) => aoEnviar(evento.nativeEvent)}>
        <Button type="submit" carregando>
          Enviar
        </Button>
      </form>,
    );

    await userEvent.click(screen.getByRole("button", { name: "Enviar" }));

    expect(aoEnviar).not.toHaveBeenCalled();
  });

  it("desabilitado de verdade quando disabled", () => {
    render(<Button disabled>Enviar</Button>);

    expect(screen.getByRole("button", { name: "Enviar" })).toBeDisabled();
  });
});
