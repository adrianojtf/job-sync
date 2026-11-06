import type { ReactNode } from "react";
import {
  get,
  useFieldArray,
  type ArrayPath,
  type FieldArray,
  type FieldValues,
  type Path,
  type UseFormReturn,
} from "react-hook-form";
import { Button } from "../ui/Button";
import { Field } from "../ui/Field";
import { Panel } from "../ui/Panel";
import type { CampoItem } from "./campos-curriculo";
import estilos from "./FormularioCurriculo.module.css";

interface Props<T extends FieldValues, N extends ArrayPath<T>> {
  form: UseFormReturn<T>;
  nome: N;
  titulo: string;
  subtitulo?: string;
  rotuloItem: string;
  itemVazio: FieldArray<T, N>;
  campos: CampoItem[];
  acoesItem?: (indice: number) => ReactNode;
}

/**
 * Lista editável de itens de um formulário de currículo (experiências, formações, certificações,
 * idiomas) — RF4.1. Usada no cadastro (Meu perfil) e na revisão do currículo adaptado.
 */
export function ListaItensCurriculo<T extends FieldValues, N extends ArrayPath<T>>({
  form,
  nome,
  titulo,
  subtitulo,
  rotuloItem,
  itemVazio,
  campos,
  acoesItem,
}: Props<T, N>) {
  const { fields, append, remove } = useFieldArray({ control: form.control, name: nome });
  const rotuloMinusculo = rotuloItem.toLowerCase();

  return (
    <Panel
      titulo={titulo}
      subtitulo={subtitulo}
      acoes={
        <Button variante="text" onClick={() => append(itemVazio)}>
          Adicionar {rotuloMinusculo}
        </Button>
      }
    >
      {fields.length === 0 && <p className={estilos.vazio}>Nenhum item adicionado.</p>}
      {fields.map((campoLista, indice) => (
        <fieldset key={campoLista.id} className={estilos.item}>
          <legend className={estilos.legenda}>
            {rotuloItem} {indice + 1}
          </legend>
          <div className={estilos.grade}>
            {campos.map((campo) => {
              const caminho = `${nome}.${indice}.${campo.chave}` as Path<T>;
              const erro = get(form.formState.errors, caminho)?.message as string | undefined;
              const registro = form.register(caminho, {
                validate: campo.obrigatorio
                  ? (valor) => String(valor ?? "").trim() !== "" || campo.obrigatorio
                  : undefined,
              });
              return (
                <div
                  key={campo.chave}
                  className={campo.larguraTotal ? estilos.larguraTotal : undefined}
                >
                  {campo.tipoCampo === "select" ? (
                    <Field
                      tipoCampo="select"
                      rotulo={campo.rotulo}
                      opcoes={campo.opcoes ?? []}
                      erro={erro}
                      {...registro}
                    />
                  ) : campo.tipoCampo === "textarea" ? (
                    <Field tipoCampo="textarea" rotulo={campo.rotulo} erro={erro} {...registro} />
                  ) : (
                    <Field rotulo={campo.rotulo} erro={erro} {...registro} />
                  )}
                </div>
              );
            })}
          </div>
          <div className={estilos.acoesItem}>
            {acoesItem?.(indice)}
            <Button
              aria-label={`Remover ${rotuloMinusculo} ${indice + 1}`}
              onClick={() => remove(indice)}
            >
              Remover
            </Button>
          </div>
        </fieldset>
      ))}
    </Panel>
  );
}
