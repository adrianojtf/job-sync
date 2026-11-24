import { act, renderHook } from "@testing-library/react";
import { useFieldArray, useForm } from "react-hook-form";
import { useHistoricoDoFormulario } from "./use-historico-do-formulario";

interface Valores {
  nome: string;
  itens: { texto: string }[];
}

function useFormularioDeTeste() {
  const form = useForm<Valores>({
    defaultValues: { nome: "Ana", itens: [{ texto: "A" }, { texto: "B" }, { texto: "C" }] },
  });
  const lista = useFieldArray({ control: form.control, name: "itens" });
  const historico = useHistoricoDoFormulario(form);
  return { form, lista, historico };
}

describe("useHistoricoDoFormulario", () => {
  it("desfazer devolve a ordem anterior da lista", () => {
    const { result } = renderHook(useFormularioDeTeste);

    act(() => {
      result.current.historico.registrar();
      result.current.lista.move(0, 2);
    });
    expect(result.current.form.getValues("itens").map((i) => i.texto)).toEqual(["B", "C", "A"]);

    act(() => result.current.historico.desfazer());

    expect(result.current.form.getValues("itens").map((i) => i.texto)).toEqual(["A", "B", "C"]);
  });

  it("desfazer restaura também os outros campos", () => {
    const { result } = renderHook(useFormularioDeTeste);

    act(() => {
      result.current.historico.registrar();
      result.current.form.setValue("nome", "Outra", { shouldDirty: true });
      result.current.lista.remove(1);
    });
    act(() => result.current.historico.desfazer());

    expect(result.current.form.getValues("nome")).toBe("Ana");
    expect(result.current.form.getValues("itens")).toHaveLength(3);
  });

  it("não altera o formulário se nada foi registrado", () => {
    const { result } = renderHook(useFormularioDeTeste);
    act(() => result.current.form.setValue("nome", "Nova", { shouldDirty: true }));

    act(() => result.current.historico.desfazer());

    expect(result.current.form.getValues("nome")).toBe("Nova");
  });

  it("o instantâneo não muda com alterações posteriores", () => {
    const { result } = renderHook(useFormularioDeTeste);
    act(() => result.current.historico.registrar());

    act(() => result.current.form.setValue("itens.0.texto", "Mudou"));
    act(() => result.current.historico.desfazer());

    expect(result.current.form.getValues("itens.0.texto")).toBe("A");
  });

  it("depois de desfazer, um segundo desfazer não faz nada", () => {
    const { result } = renderHook(useFormularioDeTeste);
    act(() => {
      result.current.historico.registrar();
      result.current.form.setValue("nome", "X");
    });
    act(() => result.current.historico.desfazer());
    act(() => result.current.form.setValue("nome", "Y"));

    act(() => result.current.historico.desfazer());

    expect(result.current.form.getValues("nome")).toBe("Y");
  });

  it("devolve as mesmas funções a cada renderização", () => {
    const { result, rerender } = renderHook(useFormularioDeTeste);
    const antes = result.current.historico;

    rerender();

    expect(result.current.historico).toBe(antes);
  });
});
