import type { DndContextProps, DragEndEvent } from "@dnd-kit/core";
import { act, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import type { CategoriaFormulario } from "./campos-curriculo";
import { idDaCategoria, idDaTag } from "./competencias";
import { EditorCompetencias } from "./EditorCompetencias";

const dnd = vi.hoisted(() => ({ props: null as DndContextProps | null }));
vi.mock("@dnd-kit/core", async (importOriginal) => {
  const real = await importOriginal<typeof import("@dnd-kit/core")>();
  return {
    ...real,
    DndContext: (props: DndContextProps) => {
      dnd.props = props;
      return <real.DndContext {...props} />;
    },
  };
});

async function soltar(ativo: string, sobre: string | null) {
  await act(async () => {
    dnd.props!.onDragEnd!({
      active: { id: ativo },
      over: sobre ? { id: sobre } : null,
    } as DragEndEvent);
  });
}

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
    expect(screen.getByText("Tag Go adicionada em Linguagens.")).toBeInTheDocument();

    await userEvent.click(within(grupo("Linguagens")).getByRole("button", { name: "Remover Go" }));
    expect(screen.getByText("Tag Go removida de Linguagens.")).toBeInTheDocument();
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

describe("EditorCompetencias — arrastar e soltar", () => {
  it("move uma tag para outra categoria e anuncia o movimento", async () => {
    const aoMudar = vi.fn();
    render(<Hospedeiro aoMudar={aoMudar} />);

    await soltar(idDaTag(0, "Python"), idDaTag(1, "SQL"));

    expect(aoMudar).toHaveBeenLastCalledWith([
      { nome: "Linguagens", tags: ["Java"] },
      { nome: "Bancos de Dados", tags: ["Python", "SQL"] },
    ]);
    expect(within(grupo("Bancos de Dados")).getByText("Python")).toBeInTheDocument();
    expect(
      screen.getByText("Tag Python movida de Linguagens para Bancos de Dados."),
    ).toBeInTheDocument();
  });

  it("reordena as tags dentro da categoria e anuncia", async () => {
    const aoMudar = vi.fn();
    render(<Hospedeiro aoMudar={aoMudar} />);

    await soltar(idDaTag(0, "Python"), idDaTag(0, "Java"));

    expect(aoMudar).toHaveBeenLastCalledWith([
      { nome: "Linguagens", tags: ["Python", "Java"] },
      { nome: "Bancos de Dados", tags: ["SQL"] },
    ]);
    expect(screen.getByText("Tag Python reordenada em Linguagens.")).toBeInTheDocument();
  });

  it("solta uma tag numa categoria sem tags", async () => {
    const aoMudar = vi.fn();
    render(
      <Hospedeiro
        inicial={[
          { nome: "Linguagens", tags: ["Java"] },
          { nome: "Novas", tags: [] },
        ]}
        aoMudar={aoMudar}
      />,
    );

    await soltar(idDaTag(0, "Java"), idDaCategoria(1));

    expect(aoMudar).toHaveBeenLastCalledWith([
      { nome: "Linguagens", tags: [] },
      { nome: "Novas", tags: ["Java"] },
    ]);
  });

  it("soltar fora de qualquer categoria não altera nada", async () => {
    const aoMudar = vi.fn();
    render(<Hospedeiro aoMudar={aoMudar} />);

    await soltar(idDaTag(0, "Java"), null);

    expect(aoMudar).not.toHaveBeenCalled();
  });

  it("cada tag tem uma alça com o nome acessível e o botão de remover continua à parte", () => {
    render(<Hospedeiro />);

    const linguagens = within(grupo("Linguagens"));
    expect(linguagens.getByLabelText("Mover Java")).toBeInTheDocument();
    expect(linguagens.getByRole("button", { name: "Remover Java" })).toBeInTheDocument();
  });

  it("as instruções para leitor de tela explicam como mover uma tag pelo teclado", () => {
    render(<Hospedeiro />);

    expect(dnd.props?.accessibility?.screenReaderInstructions?.draggable).toMatch(/Espaço.*setas/);
  });
});
