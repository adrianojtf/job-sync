import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import type { CategoriaFormulario } from "./campos-curriculo";
import { EditorCompetencias } from "./EditorCompetencias";

const INICIAL: CategoriaFormulario[] = [
  { nome: "Linguagens", tags: ["Java", "Python"] },
  { nome: "Bancos de Dados", tags: ["SQL"] },
];

function Hospedeiro({
  inicial = INICIAL,
  aoMudar,
}: {
  inicial?: CategoriaFormulario[];
  aoMudar?: (valor: CategoriaFormulario[]) => void;
}) {
  const [valor, setValor] = useState(inicial);
  return (
    <EditorCompetencias
      valor={valor}
      aoMudar={(novo) => {
        setValor(novo);
        aoMudar?.(novo);
      }}
    />
  );
}

const grupo = (nome: string) => screen.getByRole("group", { name: nome });

describe("EditorCompetencias", () => {
  it("mostra cada categoria com as suas tags", () => {
    render(<Hospedeiro />);

    const linguagens = within(grupo("Linguagens"));
    expect(linguagens.getByText("Java")).toBeInTheDocument();
    expect(linguagens.getByText("Python")).toBeInTheDocument();
    expect(within(grupo("Bancos de Dados")).getByText("SQL")).toBeInTheDocument();
  });

  it("remove uma tag pelo botão com o nome da tag", async () => {
    const aoMudar = vi.fn();
    render(<Hospedeiro aoMudar={aoMudar} />);

    await userEvent.click(
      within(grupo("Linguagens")).getByRole("button", { name: "Remover Java" }),
    );

    expect(within(grupo("Linguagens")).queryByText("Java")).not.toBeInTheDocument();
    expect(aoMudar).toHaveBeenLastCalledWith([
      { nome: "Linguagens", tags: ["Python"] },
      { nome: "Bancos de Dados", tags: ["SQL"] },
    ]);
  });

  it("cria uma tag com Enter", async () => {
    render(<Hospedeiro />);

    await userEvent.type(
      within(grupo("Linguagens")).getByRole("textbox", { name: "Nova tag" }),
      "Go{Enter}",
    );

    expect(within(grupo("Linguagens")).getByText("Go")).toBeInTheDocument();
    expect(within(grupo("Linguagens")).getByRole("textbox", { name: "Nova tag" })).toHaveValue("");
  });

  it("cria uma tag com vírgula", async () => {
    render(<Hospedeiro />);

    await userEvent.type(
      within(grupo("Linguagens")).getByRole("textbox", { name: "Nova tag" }),
      "Kotlin,",
    );

    expect(within(grupo("Linguagens")).getByText("Kotlin")).toBeInTheDocument();
  });

  it("cria a tag ao sair do campo", async () => {
    render(<Hospedeiro />);

    await userEvent.type(
      within(grupo("Linguagens")).getByRole("textbox", { name: "Nova tag" }),
      "Rust",
    );
    await userEvent.tab();

    expect(within(grupo("Linguagens")).getByText("Rust")).toBeInTheDocument();
  });

  it("separa vários itens colados com vírgula em várias tags", async () => {
    const aoMudar = vi.fn();
    render(<Hospedeiro aoMudar={aoMudar} />);

    await userEvent.click(within(grupo("Linguagens")).getByRole("textbox", { name: "Nova tag" }));
    await userEvent.paste("Go, Rust ,  Kotlin");
    await userEvent.keyboard("{Enter}");

    expect(aoMudar).toHaveBeenLastCalledWith([
      { nome: "Linguagens", tags: ["Java", "Python", "Go", "Rust", "Kotlin"] },
      { nome: "Bancos de Dados", tags: ["SQL"] },
    ]);
  });

  it("ignora tag repetida sem diferenciar maiúsculas e minúsculas", async () => {
    const aoMudar = vi.fn();
    render(<Hospedeiro aoMudar={aoMudar} />);

    await userEvent.type(
      within(grupo("Linguagens")).getByRole("textbox", { name: "Nova tag" }),
      "java{Enter}",
    );

    expect(within(grupo("Linguagens")).getAllByText(/^java$/i)).toHaveLength(1);
  });

  it("ignora tag vazia", async () => {
    const aoMudar = vi.fn();
    render(<Hospedeiro aoMudar={aoMudar} />);

    await userEvent.type(
      within(grupo("Linguagens")).getByRole("textbox", { name: "Nova tag" }),
      "   {Enter}",
    );

    expect(aoMudar).not.toHaveBeenCalled();
  });

  it("renomeia uma categoria", async () => {
    const aoMudar = vi.fn();
    render(<Hospedeiro aoMudar={aoMudar} />);

    const nome = within(grupo("Bancos de Dados")).getByRole("textbox", {
      name: "Nome da categoria",
    });
    await userEvent.clear(nome);
    await userEvent.type(nome, "Dados");

    expect(aoMudar).toHaveBeenLastCalledWith([
      { nome: "Linguagens", tags: ["Java", "Python"] },
      { nome: "Dados", tags: ["SQL"] },
    ]);
  });

  it("adiciona uma categoria vazia e leva o foco ao nome dela", async () => {
    render(<Hospedeiro />);

    await userEvent.click(screen.getByRole("button", { name: "Adicionar categoria" }));

    const nomes = screen.getAllByRole("textbox", { name: "Nome da categoria" });
    expect(nomes).toHaveLength(3);
    expect(nomes[2]).toHaveFocus();
  });

  it("exclui uma categoria", async () => {
    const aoMudar = vi.fn();
    render(<Hospedeiro aoMudar={aoMudar} />);

    await userEvent.click(screen.getByRole("button", { name: "Excluir categoria Linguagens" }));

    expect(screen.queryByRole("group", { name: "Linguagens" })).not.toBeInTheDocument();
    expect(aoMudar).toHaveBeenLastCalledWith([{ nome: "Bancos de Dados", tags: ["SQL"] }]);
  });

  it("sem categorias mostra a orientação para adicionar", () => {
    render(<Hospedeiro inicial={[]} />);

    expect(screen.getByText("Nenhuma categoria adicionada.")).toBeInTheDocument();
  });

  it("anuncia a criação e a remoção de tags para leitores de tela", async () => {
    render(<Hospedeiro />);

    await userEvent.type(
      within(grupo("Linguagens")).getByRole("textbox", { name: "Nova tag" }),
      "Go{Enter}",
    );
    expect(screen.getByRole("status")).toHaveTextContent("Tag Go adicionada em Linguagens.");

    await userEvent.click(within(grupo("Linguagens")).getByRole("button", { name: "Remover Go" }));
    expect(screen.getByRole("status")).toHaveTextContent("Tag Go removida de Linguagens.");
  });

  it("não envia o formulário ao teclar Enter no campo de tag", async () => {
    const aoEnviar = vi.fn((evento: React.FormEvent) => evento.preventDefault());
    render(
      <form onSubmit={aoEnviar}>
        <Hospedeiro />
      </form>,
    );

    await userEvent.type(
      within(grupo("Linguagens")).getByRole("textbox", { name: "Nova tag" }),
      "Go{Enter}",
    );

    expect(aoEnviar).not.toHaveBeenCalled();
  });
});
