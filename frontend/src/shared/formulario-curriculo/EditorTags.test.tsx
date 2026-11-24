import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { EditorTags } from "./EditorTags";

function Hospedeiro({
  inicial = ["Java"],
  aoMudar,
  aoAnunciar,
}: {
  inicial?: string[];
  aoMudar?: (tags: string[]) => void;
  aoAnunciar?: (mensagem: string) => void;
}) {
  const [tags, setTags] = useState(inicial);
  return (
    <EditorTags
      tags={tags}
      aoMudar={(novas) => {
        setTags(novas);
        aoMudar?.(novas);
      }}
      nome="skills"
      aoAnunciar={aoAnunciar}
      rotuloNovaTag="Nova skill"
    />
  );
}

describe("EditorTags", () => {
  it("mostra as tags numa lista com o nome do grupo", () => {
    render(<Hospedeiro inicial={["Java", "SQL"]} />);

    const lista = screen.getByRole("list", { name: "Tags de skills" });
    expect(lista).toHaveTextContent("Java");
    expect(lista).toHaveTextContent("SQL");
  });

  it("cria uma tag com Enter e anuncia", async () => {
    const aoMudar = vi.fn();
    const aoAnunciar = vi.fn();
    render(<Hospedeiro aoMudar={aoMudar} aoAnunciar={aoAnunciar} />);

    await userEvent.type(screen.getByLabelText("Nova skill"), "Flyway{Enter}");

    expect(aoMudar).toHaveBeenLastCalledWith(["Java", "Flyway"]);
    expect(aoAnunciar).toHaveBeenCalledWith("Tag Flyway adicionada em skills.");
    expect(screen.getByLabelText("Nova skill")).toHaveValue("");
  });

  it("cria várias tags de uma vez com vírgula e ignora repetidas sem diferenciar a caixa", async () => {
    const aoMudar = vi.fn();
    render(<Hospedeiro aoMudar={aoMudar} />);

    await userEvent.type(screen.getByLabelText("Nova skill"), "java, SQL, sql{Enter}");

    expect(aoMudar).toHaveBeenLastCalledWith(["Java", "SQL"]);
  });

  it("cria a tag ao sair do campo", async () => {
    const aoMudar = vi.fn();
    render(<Hospedeiro aoMudar={aoMudar} />);

    await userEvent.type(screen.getByLabelText("Nova skill"), "React");
    await userEvent.tab();

    expect(aoMudar).toHaveBeenLastCalledWith(["Java", "React"]);
  });

  it("remove uma tag pelo botão com o nome dela e anuncia", async () => {
    const aoMudar = vi.fn();
    const aoAnunciar = vi.fn();
    render(<Hospedeiro inicial={["Java", "SQL"]} aoMudar={aoMudar} aoAnunciar={aoAnunciar} />);

    await userEvent.click(screen.getByRole("button", { name: "Remover Java" }));

    expect(aoMudar).toHaveBeenLastCalledWith(["SQL"]);
    expect(aoAnunciar).toHaveBeenCalledWith("Tag Java removida de skills.");
  });

  it("sem tags não mostra a lista", () => {
    render(<Hospedeiro inicial={[]} />);

    expect(screen.queryByRole("list")).not.toBeInTheDocument();
  });
});
