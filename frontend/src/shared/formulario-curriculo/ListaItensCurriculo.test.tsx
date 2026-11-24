import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useForm } from "react-hook-form";
import {
  CAMPO_PERIODO_VALIDADO,
  CAMPOS_EXPERIENCIA_ADAPTADA,
  EXPERIENCIA_ADAPTADA_VAZIA,
  type ExperienciaAdaptadaFormulario,
} from "./campos-curriculo";
import { ListaItensCurriculo } from "./ListaItensCurriculo";
import { validarPeriodo } from "./periodo";

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

describe("ListaItensCurriculo com validação de formato", () => {
  function FormularioComPeriodo({ periodo }: { periodo: string }) {
    const form = useForm<{ itens: { empresa: string; periodo: string }[] }>({
      defaultValues: { itens: [{ empresa: "TechCorp", periodo }] },
    });
    return (
      <form onSubmit={form.handleSubmit(() => undefined)} noValidate>
        <ListaItensCurriculo
          form={form}
          nome="itens"
          titulo="Itens"
          rotuloItem="Item"
          itemVazio={{ empresa: "", periodo: "" }}
          campos={[
            { chave: "empresa", rotulo: "Empresa", obrigatorio: "Informe a empresa." },
            { chave: "periodo", rotulo: "Período", validar: validarPeriodo },
          ]}
        />
        <button type="submit">Enviar</button>
      </form>
    );
  }

  it("mostra a mensagem do formato quando o campo preenchido é inválido", async () => {
    render(<FormularioComPeriodo periodo="ontem" />);

    await userEvent.click(screen.getByRole("button", { name: "Enviar" }));

    expect(
      await screen.findByText("Use o formato Mar 2024 - Atual ou 2020 - 2022."),
    ).toBeInTheDocument();
  });

  it("aceita o campo vazio e o formato correto", async () => {
    render(<FormularioComPeriodo periodo="2020 - 2022" />);

    await userEvent.click(screen.getByRole("button", { name: "Enviar" }));

    expect(screen.queryByText(/Use o formato/)).not.toBeInTheDocument();
  });

  it("a validação do formato não substitui a obrigatoriedade", async () => {
    render(<FormularioComPeriodo periodo="2020" />);
    await userEvent.clear(screen.getByLabelText("Empresa"));

    await userEvent.click(screen.getByRole("button", { name: "Enviar" }));

    expect(await screen.findByText("Informe a empresa.")).toBeInTheDocument();
  });
});

describe("campo de período do perfil", () => {
  it("o período da revisão do adaptado segue sem validação de formato", () => {
    expect(
      CAMPOS_EXPERIENCIA_ADAPTADA.find((campo) => campo.chave === "periodo")?.validar,
    ).toBeUndefined();
  });

  it("o período do perfil valida o formato e orienta com um exemplo", () => {
    expect(CAMPO_PERIODO_VALIDADO.validar?.("ontem")).toContain("Mar 2024 - Atual");
    expect(CAMPO_PERIODO_VALIDADO.ajuda).toContain("2020 - 2022");
  });
});
