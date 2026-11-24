import type { DndContextProps, DragEndEvent } from "@dnd-kit/core";
import { act, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useForm } from "react-hook-form";
import { ToastProvider } from "../ui/ToastProvider";
import type { CampoItem } from "./campos-curriculo";
import { ListaItensCurriculo } from "./ListaItensCurriculo";
import { chaveDePeriodo } from "./periodo";
import { useHistoricoDoFormulario } from "./use-historico-do-formulario";

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

interface Item {
  empresa: string;
  periodo: string;
}

const CAMPOS: CampoItem[] = [
  { chave: "empresa", rotulo: "Empresa", obrigatorio: "Informe a empresa." },
  { chave: "periodo", rotulo: "Período" },
];

const ITENS: Item[] = [
  { empresa: "Alfa", periodo: "2018 - 2020" },
  { empresa: "Beta", periodo: "2020 - 2022" },
  { empresa: "Gama", periodo: "2022 - Atual" },
];

function Lista({
  itens = ITENS,
  limite,
  ordenar = false,
  reordenavel = true,
}: {
  itens?: Item[];
  limite?: number;
  ordenar?: boolean;
  reordenavel?: boolean;
}) {
  const form = useForm<{ itens: Item[] }>({ defaultValues: { itens } });
  const historico = useHistoricoDoFormulario(form);
  return (
    <ListaItensCurriculo
      form={form}
      nome="itens"
      titulo="Experiências"
      rotuloItem="Experiência"
      itemVazio={{ empresa: "", periodo: "" }}
      campos={CAMPOS}
      modo="cartao"
      resumoDoItem={(valores) => ({
        titulo: valores.empresa,
        subtitulo: "Resumo",
        meta: valores.periodo,
      })}
      reordenavel={reordenavel}
      limite={limite}
      ordenarPor={
        ordenar
          ? { rotulo: "período", chave: (valores) => chaveDePeriodo(valores.periodo) }
          : undefined
      }
      historico={historico}
    />
  );
}

function renderizar(props: Parameters<typeof Lista>[0] = {}) {
  return render(
    <ToastProvider>
      <Lista {...props} />
    </ToastProvider>,
  );
}

const cartoes = () =>
  screen.getAllByRole("group").filter((grupo) => grupo.hasAttribute("data-item-id"));
const empresas = () =>
  cartoes()
    .map((cartao) => within(cartao).getByLabelText("Empresa"))
    .map((c) => (c as HTMLInputElement).value);

async function soltar(ativo: string, sobre: string | null) {
  await act(async () => {
    dnd.props!.onDragStart!({ active: { id: ativo } } as never);
    dnd.props!.onDragEnd!({
      active: { id: ativo },
      over: sobre ? { id: sobre } : null,
    } as DragEndEvent);
  });
}
const idDe = (indice: number) => cartoes()[indice]!.getAttribute("data-item-id")!;

describe("ListaItensCurriculo em modo cartão", () => {
  it("mostra cada item recolhido, com o resumo, e os campos escondidos", () => {
    renderizar();

    expect(cartoes()).toHaveLength(3);
    expect(screen.getByText("Alfa")).toBeInTheDocument();
    expect(screen.getAllByText("Resumo")).toHaveLength(3);
    expect(screen.getByText("2018 - 2020")).toBeInTheDocument();
    expect(within(cartoes()[0]!).getByLabelText("Empresa")).not.toBeVisible();
  });

  it("abre e recolhe o cartão pelo título e pelo botão de abrir", async () => {
    renderizar();
    const primeiro = within(cartoes()[0]!);

    await userEvent.click(primeiro.getByRole("button", { name: "Editar Alfa" }));
    expect(primeiro.getByLabelText("Empresa")).toBeVisible();
    expect(primeiro.getByRole("button", { name: "Recolher Alfa" })).toHaveAttribute(
      "aria-expanded",
      "true",
    );

    await userEvent.click(primeiro.getByRole("button", { name: "Concluir" }));
    expect(primeiro.getByLabelText("Empresa")).not.toBeVisible();
  });

  it("vários cartões podem ficar abertos e Expandir/Recolher todas alterna todos", async () => {
    renderizar();

    await userEvent.click(screen.getByRole("button", { name: "Expandir todas" }));
    cartoes().forEach((cartao) => expect(within(cartao).getByLabelText("Empresa")).toBeVisible());

    await userEvent.click(screen.getByRole("button", { name: "Recolher todas" }));
    cartoes().forEach((cartao) =>
      expect(within(cartao).getByLabelText("Empresa")).not.toBeVisible(),
    );
  });

  it("o resumo acompanha o que o usuário digita", async () => {
    renderizar();
    const primeiro = within(cartoes()[0]!);
    await userEvent.click(primeiro.getByRole("button", { name: "Editar Alfa" }));

    await userEvent.clear(primeiro.getByLabelText("Empresa"));
    await userEvent.type(primeiro.getByLabelText("Empresa"), "Nova Alfa");

    expect(primeiro.getByRole("button", { name: "Recolher Nova Alfa" })).toBeInTheDocument();
  });

  it("move um item para baixo pelo botão, avisa e permite desfazer", async () => {
    renderizar();

    await userEvent.click(screen.getByRole("button", { name: "Mover Alfa para baixo" }));

    expect(empresas()).toEqual(["Beta", "Alfa", "Gama"]);
    expect(screen.getByText("Ordem alterada.")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Desfazer" }));

    expect(empresas()).toEqual(["Alfa", "Beta", "Gama"]);
  });

  it("os botões de mover ficam desabilitados nas pontas da lista", () => {
    renderizar();

    expect(screen.getByRole("button", { name: "Mover Alfa para cima" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Mover Gama para baixo" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Mover Beta para cima" })).toBeEnabled();
  });

  it("o foco acompanha o item movido pelo botão", async () => {
    renderizar();

    await userEvent.click(screen.getByRole("button", { name: "Mover Alfa para baixo" }));

    expect(screen.getByRole("button", { name: "Mover Alfa para baixo" })).toHaveFocus();
  });

  it("soltar um item em outra posição reordena e permite desfazer", async () => {
    renderizar();

    await soltar(idDe(0), idDe(2));

    expect(empresas()).toEqual(["Beta", "Gama", "Alfa"]);
    await userEvent.click(screen.getByRole("button", { name: "Desfazer" }));
    expect(empresas()).toEqual(["Alfa", "Beta", "Gama"]);
  });

  it("soltar fora da lista ou sobre si mesmo não altera nada", async () => {
    renderizar();

    await soltar(idDe(0), null);
    await soltar(idDe(1), idDe(1));

    expect(empresas()).toEqual(["Alfa", "Beta", "Gama"]);
    expect(screen.queryByText("Ordem alterada.")).not.toBeInTheDocument();
  });

  it("devolve o foco à alça do item solto", async () => {
    renderizar();

    await soltar(idDe(0), idDe(1));

    expect(screen.getByRole("button", { name: /^Mover Alfa\. Posição 2 de 3$/ })).toHaveFocus();
  });

  it("durante o arrasto marca a lista para recolher os cartões", async () => {
    renderizar();

    await act(async () => dnd.props!.onDragStart!({ active: { id: idDe(0) } } as never));

    expect(document.querySelector("[data-arrastando]")).not.toBeNull();

    await soltar(idDe(0), null);
    expect(document.querySelector("[data-arrastando]")).toBeNull();
  });

  it("a alça tem nome com o título e a posição", () => {
    renderizar();

    expect(screen.getByRole("button", { name: "Mover Beta. Posição 2 de 3" })).toHaveAttribute(
      "aria-roledescription",
      "item arrastável",
    );
  });

  it("sem reordenavel não há alça nem botões de mover", () => {
    renderizar({ reordenavel: false });

    expect(screen.queryByRole("button", { name: /^Mover/ })).not.toBeInTheDocument();
  });

  it("os anúncios em português usam o título do item e a posição", () => {
    renderizar();
    const anuncios = dnd.props!.accessibility!.announcements!;

    expect(anuncios.onDragStart!({ active: { id: idDe(0) } } as never)).toBe(
      "Alfa pego. Posição 1 de 3.",
    );
    expect(anuncios.onDragEnd!({ active: { id: idDe(0) }, over: { id: idDe(2) } } as never)).toBe(
      "Alfa solto na posição 3 de 3.",
    );
    expect(anuncios.onDragEnd!({ active: { id: idDe(0) }, over: null } as never)).toContain(
      "Nada foi alterado",
    );
    expect(dnd.props!.accessibility!.screenReaderInstructions!.draggable).toMatch(/Espaço.*setas/);
  });

  it("remove um item, avisa e permite desfazer", async () => {
    renderizar();
    await userEvent.click(within(cartoes()[1]!).getByRole("button", { name: "Editar Beta" }));

    await userEvent.click(screen.getByRole("button", { name: "Remover experiência 2" }));

    expect(empresas()).toEqual(["Alfa", "Gama"]);
    await userEvent.click(screen.getByRole("button", { name: "Desfazer" }));
    expect(empresas()).toEqual(["Alfa", "Beta", "Gama"]);
  });
});

describe("ListaItensCurriculo em modo cartão: adicionar e limite", () => {
  it("adiciona no topo, abre o cartão novo e foca o primeiro campo", async () => {
    renderizar();

    await userEvent.click(screen.getByRole("button", { name: "Adicionar experiência" }));

    expect(cartoes()).toHaveLength(4);
    expect(empresas()).toEqual(["", "Alfa", "Beta", "Gama"]);
    expect(within(cartoes()[0]!).getByLabelText("Empresa")).toBeVisible();
    expect(within(cartoes()[1]!).getByLabelText("Empresa")).not.toBeVisible();
  });

  it("no limite o botão de adicionar fica desabilitado e a lista explica", () => {
    renderizar({ limite: 3 });

    expect(screen.getByRole("button", { name: "Adicionar experiência" })).toBeDisabled();
    expect(screen.getByRole("note")).toHaveTextContent(
      "Você chegou ao limite de 3 itens nesta lista.",
    );
  });

  it("abaixo do limite não mostra o aviso e permite adicionar", async () => {
    renderizar({ limite: 4 });

    expect(screen.queryByRole("note")).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Adicionar experiência" }));

    expect(cartoes()).toHaveLength(4);
    expect(screen.getByRole("button", { name: "Adicionar experiência" })).toBeDisabled();
  });

  it("remover um item libera o botão de adicionar", async () => {
    renderizar({ limite: 3 });
    await userEvent.click(within(cartoes()[0]!).getByRole("button", { name: "Editar Alfa" }));

    await userEvent.click(screen.getByRole("button", { name: "Remover experiência 1" }));

    expect(screen.getByRole("button", { name: "Adicionar experiência" })).toBeEnabled();
  });
});

describe("ListaItensCurriculo em modo cartão: ordenar por período", () => {
  it("ordena do mais recente para o mais antigo, avisa e permite desfazer", async () => {
    renderizar({ ordenar: true });

    await userEvent.click(screen.getByRole("button", { name: "Ordenar por período" }));

    expect(empresas()).toEqual(["Gama", "Beta", "Alfa"]);
    expect(screen.getByText("Ordenado do mais recente para o mais antigo.")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Desfazer" }));
    expect(empresas()).toEqual(["Alfa", "Beta", "Gama"]);
  });

  it("avisa quando já estava ordenado e não registra nada para desfazer", async () => {
    renderizar({
      ordenar: true,
      itens: [
        { empresa: "Gama", periodo: "2022 - Atual" },
        { empresa: "Alfa", periodo: "2018 - 2020" },
      ],
    });

    await userEvent.click(screen.getByRole("button", { name: "Ordenar por período" }));

    expect(screen.getByText("Já estava ordenado.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Desfazer" })).not.toBeInTheDocument();
  });

  it("período vazio fica no fim, mantendo a ordem relativa", async () => {
    renderizar({
      ordenar: true,
      itens: [
        { empresa: "Sem período A", periodo: "" },
        { empresa: "Alfa", periodo: "2018 - 2020" },
        { empresa: "Sem período B", periodo: "" },
        { empresa: "Gama", periodo: "2022 - Atual" },
      ],
    });

    await userEvent.click(screen.getByRole("button", { name: "Ordenar por período" }));

    expect(empresas()).toEqual(["Gama", "Alfa", "Sem período A", "Sem período B"]);
  });

  it("o botão de ordenar só existe quando a lista pede", () => {
    renderizar();

    expect(screen.queryByRole("button", { name: /^Ordenar por/ })).not.toBeInTheDocument();
  });
});
