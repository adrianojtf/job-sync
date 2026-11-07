import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SugestaoIA } from "./SugestaoIA";

function renderizar(props: Partial<Parameters<typeof SugestaoIA<string>>[0]> = {}) {
  const sugerir = vi.fn().mockResolvedValue("Texto sugerido pela IA.");
  const aplicar = vi.fn();
  const focarCampo = vi.fn();
  render(
    <QueryClientProvider client={new QueryClient()}>
      <SugestaoIA
        rotuloBloco="resumo"
        textoAtual="Texto atual editado."
        sugerir={sugerir}
        aplicar={aplicar}
        focarCampo={focarCampo}
        {...props}
      />
    </QueryClientProvider>,
  );
  return { sugerir, aplicar, focarCampo };
}

const pedir = () =>
  userEvent.click(screen.getByRole("button", { name: "Sugestões de IA para resumo" }));

describe("SugestaoIA", () => {
  it("envia o texto atual do campo e mostra a sugestão sem aplicá-la", async () => {
    const { sugerir, aplicar } = renderizar();

    await pedir();

    expect(await screen.findByText("Texto sugerido pela IA.")).toBeInTheDocument();
    expect(sugerir).toHaveBeenCalledWith("Texto atual editado.");
    expect(aplicar).not.toHaveBeenCalled();
    expect(screen.getByRole("region", { name: "Sugestão da IA para resumo" })).toBeInTheDocument();
  });

  it("aplica a sugestão, fecha o painel e devolve o foco ao campo", async () => {
    const { aplicar, focarCampo } = renderizar();
    await pedir();
    await screen.findByText("Texto sugerido pela IA.");

    await userEvent.click(screen.getByRole("button", { name: "Aplicar sugestão em resumo" }));

    expect(aplicar).toHaveBeenCalledWith("Texto sugerido pela IA.");
    expect(focarCampo).toHaveBeenCalledTimes(1);
    expect(screen.queryByText("Texto sugerido pela IA.")).not.toBeInTheDocument();
  });

  it("descarta a sugestão sem alterar o campo", async () => {
    const { aplicar, focarCampo } = renderizar();
    await pedir();
    await screen.findByText("Texto sugerido pela IA.");

    await userEvent.click(screen.getByRole("button", { name: "Descartar sugestão de resumo" }));

    expect(aplicar).not.toHaveBeenCalled();
    expect(focarCampo).toHaveBeenCalledTimes(1);
    expect(screen.queryByText("Texto sugerido pela IA.")).not.toBeInTheDocument();
  });

  it("mostra o erro no bloco e mantém o texto atual", async () => {
    const { aplicar } = renderizar({
      sugerir: vi.fn().mockRejectedValue(new Error("IA fora do ar.")),
    });

    await pedir();

    expect(await screen.findByText(/IA fora do ar\./)).toBeInTheDocument();
    expect(aplicar).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "Sugestões de IA para resumo" })).toBeEnabled();
  });

  it("fica desabilitado quando o campo está vazio", async () => {
    const { sugerir } = renderizar({ textoAtual: "   " });

    const botao = screen.getByRole("button", { name: "Sugestões de IA para resumo" });

    expect(botao).toBeDisabled();
    expect(botao).toHaveAccessibleDescription("Preencha o texto para pedir sugestões.");
    await userEvent.click(botao);
    expect(sugerir).not.toHaveBeenCalled();
  });

  it("indica o carregamento só no botão do bloco", async () => {
    let concluir: (texto: string) => void = () => undefined;
    renderizar({ sugerir: vi.fn(() => new Promise<string>((resolve) => (concluir = resolve))) });

    await pedir();

    const botao = screen.getByRole("button", { name: "Sugestões de IA para resumo" });
    expect(botao).toHaveAttribute("aria-busy", "true");
    expect(botao).toHaveTextContent("Gerando sugestão…");
    concluir("Pronto.");
    expect(await screen.findByText("Pronto.")).toBeInTheDocument();
  });

  it("uma nova sugestão substitui a anterior", async () => {
    const sugerir = vi
      .fn()
      .mockResolvedValueOnce("Primeira sugestão.")
      .mockResolvedValueOnce("Segunda sugestão.");
    renderizar({ sugerir });

    await pedir();
    await screen.findByText("Primeira sugestão.");
    await pedir();

    expect(await screen.findByText("Segunda sugestão.")).toBeInTheDocument();
    expect(screen.queryByText("Primeira sugestão.")).not.toBeInTheDocument();
  });

  it("anuncia a chegada da sugestão em uma região educada", async () => {
    renderizar();
    await pedir();

    const sugestao = await screen.findByText("Texto sugerido pela IA.");

    expect(sugestao.closest("[aria-live]")).toHaveAttribute("aria-live", "polite");
  });
});

describe("SugestaoIA com sugestão estruturada", () => {
  interface SugestaoExperiencia {
    conquistas: string[];
    contexto: string;
  }
  const sugestao: SugestaoExperiencia = {
    conquistas: ["Criei APIs.", "Reduzi custos."],
    contexto: "Pagamentos.",
  };
  const descrever = (s: SugestaoExperiencia) =>
    `${s.conquistas.map((c) => `- ${c}`).join("\n")}\n${s.contexto}`;

  function renderizarEstruturado() {
    const sugerir = vi.fn().mockResolvedValue(sugestao);
    const aplicar = vi.fn();
    const focarCampo = vi.fn();
    render(
      <QueryClientProvider client={new QueryClient()}>
        <SugestaoIA
          rotuloBloco="experiência 1"
          textoAtual="Criei APIs."
          sugerir={sugerir}
          descrever={descrever}
          aplicar={aplicar}
          focarCampo={focarCampo}
        />
      </QueryClientProvider>,
    );
    return { sugerir, aplicar, focarCampo };
  }

  it("mostra o texto descrito da sugestão e aplica o objeto inteiro", async () => {
    const { sugerir, aplicar, focarCampo } = renderizarEstruturado();

    await userEvent.click(
      screen.getByRole("button", { name: "Sugestões de IA para experiência 1" }),
    );
    const painel = await screen.findByRole("region", { name: "Sugestão da IA para experiência 1" });

    expect(sugerir).toHaveBeenCalledWith("Criei APIs.");
    expect(painel.querySelector("p")?.textContent).toBe(
      "- Criei APIs.\n- Reduzi custos.\nPagamentos.",
    );

    await userEvent.click(
      screen.getByRole("button", { name: "Aplicar sugestão em experiência 1" }),
    );

    expect(aplicar).toHaveBeenCalledWith(sugestao);
    expect(focarCampo).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole("region")).not.toBeInTheDocument();
  });

  it("exige descrever quando a sugestão não é texto", () => {
    const semDescrever = () => (
      // @ts-expect-error sugestão estruturada exige `descrever`
      <SugestaoIA
        rotuloBloco="experiência 1"
        textoAtual="Criei APIs."
        sugerir={async () => sugestao}
        aplicar={() => undefined}
      />
    );

    expect(semDescrever).toBeTypeOf("function");
  });

  it("descartar não aplica nada", async () => {
    const { aplicar } = renderizarEstruturado();
    await userEvent.click(
      screen.getByRole("button", { name: "Sugestões de IA para experiência 1" }),
    );
    await screen.findByRole("region", { name: "Sugestão da IA para experiência 1" });

    await userEvent.click(
      screen.getByRole("button", { name: "Descartar sugestão de experiência 1" }),
    );

    expect(aplicar).not.toHaveBeenCalled();
  });
});
