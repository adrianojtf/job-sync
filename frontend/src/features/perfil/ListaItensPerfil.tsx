import type { ReactNode } from "react";
import {
  get,
  useFieldArray,
  type FieldArrayPath,
  type Path,
  type UseFormReturn,
} from "react-hook-form";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Panel } from "../../shared/ui/Panel";
import type { FormularioPerfil } from "./formulario-perfil";
import estilos from "./PerfilPage.module.css";

type NomeLista = Extract<
  FieldArrayPath<FormularioPerfil>,
  "experiencias" | "formacoes" | "certificacoes" | "idiomas"
>;

export interface CampoItem {
  chave: string;
  rotulo: string;
  obrigatorio?: string;
  tipoCampo?: "textarea" | "select";
  opcoes?: { valor: string; rotulo: string }[];
  larguraTotal?: boolean;
}

interface Props<N extends NomeLista> {
  form: UseFormReturn<FormularioPerfil>;
  nome: N;
  titulo: string;
  subtitulo?: string;
  rotuloItem: string;
  itemVazio: FormularioPerfil[N][number];
  campos: CampoItem[];
  acoesItem?: (indice: number) => ReactNode;
}

/** Lista editável de itens do perfil (experiências, formações, certificações, idiomas) — RF4.1. */
export function ListaItensPerfil<N extends NomeLista>({
  form,
  nome,
  titulo,
  subtitulo,
  rotuloItem,
  itemVazio,
  campos,
  acoesItem,
}: Props<N>) {
  const { fields, append, remove } = useFieldArray({ control: form.control, name: nome });
  const rotuloMinusculo = rotuloItem.toLowerCase();

  return (
    <Panel
      titulo={titulo}
      subtitulo={subtitulo}
      acoes={
        <Button variante="text" onClick={() => append(itemVazio as never)}>
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
              const caminho = `${nome}.${indice}.${campo.chave}` as Path<FormularioPerfil>;
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
