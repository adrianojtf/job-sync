import type { DndContextProps, DragEndEvent } from "@dnd-kit/core";
import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useForm, useWatch } from "react-hook-form";
import { ToastProvider } from "../ui/ToastProvider";
import { idDaCategoria, idDaTag } from "./competencias";
import { ListaDeTecnologias } from "./ListaDeTecnologias";
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

function Hospedeiro({ inicial = ["Java", "SQL", "AWS"] }: { inicial?: string[] }) {
  const form = useForm<{ tecnologias: string[] }>({ defaultValues: { tecnologias: inicial } });
  const historico = useHistoricoDoFormulario(form);
  const tecnologias = useWatch({ control: form.control, name: "tecnologias" });
  return (
    <>
      <ListaDeTecnologias
        valor={tecnologias}
        aoMudar={(tags) => form.setValue("tecnologias", tags, { shouldDirty: true })}
        historico={historico}
      />
      <output aria-label="valor">{tecnologias.join(",")}</output>
    </>
  );
}

const renderizar = (inicial?: string[]) =>
  render(
    <ToastProvider>
      <Hospedeiro inicial={inicial} />
    </ToastProvider>,
  );
const valor = () => screen.getByLabelText("valor").textContent;

async function soltar(ativo: string, sobre: string | null) {
  await act(async () => {
    dnd.props!.onDragStart!({ active: { id: ativo } } as never);
    dnd.props!.onDragEnd!({
      active: { id: ativo },
      over: sobre ? { id: sobre } : null,
    } as DragEndEvent);
  });
}

describe("ListaDeTecnologias", () => {
  it("mostra as tecnologias como tags, na ordem recebida", () => {
    renderizar();

    const lista = screen.getByRole("list", { name: "Tags de tecnologias" });
    expect(lista.textContent).toMatch(/Java.*SQL.*AWS/);
  });

  it("cria tecnologias com Enter e vírgula e ignora repetidas sem diferenciar a caixa", async () => {
    renderizar();

    await userEvent.type(screen.getByLabelText("Nova tecnologia"), "Kafka, java, Docker{Enter}");

    expect(valor()).toBe("Java,SQL,AWS,Kafka,Docker");
  });

  it("remove pelo botão da tag, avisa e permite desfazer", async () => {
    renderizar();

    await userEvent.click(screen.getByRole("button", { name: "Remover SQL" }));

    expect(valor()).toBe("Java,AWS");
    expect(screen.getByText("Tecnologia removida.")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Desfazer" }));
    expect(valor()).toBe("Java,SQL,AWS");
  });

  it("soltar uma tag sobre outra a reordena, avisa e permite desfazer", async () => {
    renderizar();

    await soltar(idDaTag(0, "AWS"), idDaTag(0, "Java"));

    expect(valor()).toBe("AWS,Java,SQL");
    expect(screen.getByText("Ordem alterada.")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Desfazer" }));
    expect(valor()).toBe("Java,SQL,AWS");
  });

  it("soltar no fim da lista leva a tag para o fim", async () => {
    renderizar();

    await soltar(idDaTag(0, "Java"), idDaCategoria(0));

    expect(valor()).toBe("SQL,AWS,Java");
  });

  it("soltar fora ou na mesma posição não altera nada", async () => {
    renderizar();

    await soltar(idDaTag(0, "Java"), null);
    await soltar(idDaTag(0, "SQL"), idDaTag(0, "SQL"));

    expect(valor()).toBe("Java,SQL,AWS");
    expect(screen.queryByText("Ordem alterada.")).not.toBeInTheDocument();
  });

  it("cada tag tem uma alça com nome acessível e as instruções explicam o teclado", () => {
    renderizar();

    expect(screen.getByRole("button", { name: "Mover Java" })).toBeInTheDocument();
    expect(dnd.props?.accessibility?.screenReaderInstructions?.draggable).toMatch(/Espaço.*setas/);
  });

  it("sem tecnologias mostra só o campo para criar a primeira", () => {
    renderizar([]);

    expect(screen.getByLabelText("Nova tecnologia")).toBeInTheDocument();
    expect(valor()).toBe("");
  });

  it("não há limite de tecnologias", async () => {
    renderizar(Array.from({ length: 30 }, (_, n) => `Tec ${n}`));

    await userEvent.type(screen.getByLabelText("Nova tecnologia"), "Mais uma{Enter}");

    expect(valor()?.split(",")).toHaveLength(31);
  });
});
