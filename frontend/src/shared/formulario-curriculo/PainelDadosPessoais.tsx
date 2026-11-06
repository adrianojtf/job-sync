import type { FieldValues, Path, UseFormReturn } from "react-hook-form";
import { Field } from "../ui/Field";
import { Panel } from "../ui/Panel";
import type { DadosPessoaisFormulario } from "./campos-curriculo";
import estilos from "./FormularioCurriculo.module.css";

interface Props<T extends FieldValues & DadosPessoaisFormulario> {
  form: UseFormReturn<T>;
  /** O cadastro exige e-mail; um currículo vindo de PDF pode não ter. */
  emailObrigatorio?: boolean;
}

const campo = <T extends FieldValues>(nome: keyof DadosPessoaisFormulario) => nome as Path<T>;

/** Bloco "Dados pessoais" (nome, e-mail, LinkedIn e resumo) do cadastro e da revisão. */
export function PainelDadosPessoais<T extends FieldValues & DadosPessoaisFormulario>({
  form,
  emailObrigatorio = true,
}: Props<T>) {
  const { errors } = form.formState;
  return (
    <Panel titulo="Dados pessoais">
      <div className={estilos.grade}>
        <Field
          rotulo="Nome completo"
          autoComplete="name"
          erro={errors.nome_completo?.message as string | undefined}
          {...form.register(campo<T>("nome_completo"), {
            validate: (v) => String(v).trim() !== "" || "Informe o nome completo.",
          })}
        />
        <Field
          rotulo="E-mail"
          type="email"
          autoComplete="email"
          erro={errors.email?.message as string | undefined}
          {...form.register(campo<T>("email"), {
            validate: emailObrigatorio
              ? (v) => String(v).trim() !== "" || "Informe o e-mail."
              : undefined,
          })}
        />
        <div className={estilos.larguraTotal}>
          <Field
            rotulo="LinkedIn"
            type="url"
            placeholder="https://linkedin.com/in/…"
            {...form.register(campo<T>("linkedin"))}
          />
        </div>
        <div className={estilos.larguraTotal}>
          <Field
            tipoCampo="textarea"
            rotulo="Resumo profissional"
            {...form.register(campo<T>("resumo_profissional"))}
          />
        </div>
      </div>
    </Panel>
  );
}
