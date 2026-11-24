import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useForm } from "react-hook-form";
import {
  CAMPOS_EXPERIENCIA_ADAPTADA,
  EXPERIENCIA_ADAPTADA_VAZIA,
  type ExperienciaAdaptadaFormulario,
} from "./campos-curriculo";
import { ListaItensCurriculo } from "./ListaItensCurriculo";

function Formulario({ valores }: { valores: ExperienciaAdaptadaFormulario[] }) {
  const form = useForm<{ experiencias: ExperienciaAdaptadaFormulario[] }>({
    defaultValues: { experiencias: valores },
  });
  return (
    <form onSubmit={form.handleSubmit(() => undefined)} noValidate>
      <ListaItensCurriculo
        form={form}
        nome="experiencias"
        titulo="Experiências profissionais"
        rotuloItem="Experiência"
        itemVazio={EXPERIENCIA_ADAPTADA_VAZIA}
        campos={CAMPOS_EXPERIENCIA_ADAPTADA}
      />
      <button type="submit">Enviar</button>
    </form>
  );
}

const EXPERIENCIA: ExperienciaAdaptadaFormulario = {
  empresa: "TechCorp",
  cargo: "Dev",
  periodo: "2024",
  conquistas: "Criei APIs.\nReduzi custos.",
  contexto: "Empresa de pagamentos.",
  responsabilidades: "",
  skills: [],
};

describe("ListaItensCurriculo com conquistas e contexto", () => {
  it("mostra os campos de identificação, conquistas e contexto com os valores atuais", () => {
    render(<Formulario valores={[EXPERIENCIA]} />);

    expect(screen.getByLabelText("Empresa")).toHaveValue("TechCorp");
    expect(screen.getByLabelText("Cargo")).toHaveValue("Dev");
    expect(screen.getByLabelText("Período")).toHaveValue("2024");
    expect(screen.getByLabelText("Principais realizações")).toHaveValue(
      "Criei APIs.\nReduzi custos.",
    );
    expect(screen.getByLabelText("Contexto")).toHaveValue("Empresa de pagamentos.");
  });

  it("explica que cada realização fica em uma linha", () => {
    render(<Formulario valores={[EXPERIENCIA]} />);

    expect(screen.getByLabelText("Principais realizações")).toHaveAccessibleDescription(
      "Uma realização por linha.",
    );
  });

  it("exige empresa e cargo", async () => {
    render(<Formulario valores={[{ ...EXPERIENCIA_ADAPTADA_VAZIA }]} />);

    await userEvent.click(screen.getByRole("button", { name: "Enviar" }));

    expect(screen.getByText("Informe a empresa.")).toBeInTheDocument();
    expect(screen.getByText("Informe o cargo.")).toBeInTheDocument();
  });

  it("adiciona uma experiência vazia", async () => {
    render(<Formulario valores={[]} />);

    await userEvent.click(screen.getByRole("button", { name: "Adicionar experiência" }));

    expect(screen.getByLabelText("Principais realizações")).toHaveValue("");
  });
});
