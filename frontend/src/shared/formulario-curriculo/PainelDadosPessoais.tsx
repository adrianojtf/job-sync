import { useEffect } from "react";
import { useWatch, type FieldValues, type Path, type UseFormReturn } from "react-hook-form";
import { Button } from "../ui/Button";
import { Field } from "../ui/Field";
import { Panel } from "../ui/Panel";
import type { DadosPessoaisFormulario } from "./campos-curriculo";
import estilos from "./FormularioCurriculo.module.css";
import { SugestaoCampo } from "./SugestaoCampo";
import type { SugerirComRefino } from "./SugestaoIA";
import { useCartoesAbertos } from "./use-cartoes-abertos";

interface Props<T extends FieldValues & DadosPessoaisFormulario> {
  form: UseFormReturn<T>;
  /** O cadastro exige e-mail; um currículo vindo de PDF pode não ter. */
  emailObrigatorio?: boolean;
  /** Quando informada, mostra "Sugestões de IA" no resumo profissional (JOB-0034). */
  sugerirResumo?: SugerirComRefino<string>;
  /**
   * Mostra os dados como um cartão recolhível, com nome e e-mail no resumo (JOB-0046). O estado
   * aberto é lembrado na chave informada; abre sozinho se o envio acusar erro nos campos.
   */
  recolhivel?: { chaveDeArmazenamento?: string; abertoPorPadrao?: boolean };
}

const ID_DO_CARTAO = "dados";

const campo = <T extends FieldValues>(nome: keyof DadosPessoaisFormulario) => nome as Path<T>;

/** Bloco "Dados pessoais" (nome, e-mail, LinkedIn e resumo) do cadastro e da revisão. */
export function PainelDadosPessoais<T extends FieldValues & DadosPessoaisFormulario>({
  form,
  emailObrigatorio = true,
  sugerirResumo,
  recolhivel,
}: Props<T>) {
  const { errors } = form.formState;
  const { abertos, alternar, abrirVarios } = useCartoesAbertos({
    chaveDeArmazenamento: recolhivel?.chaveDeArmazenamento,
    ids: [ID_DO_CARTAO],
    chavesDosItens: [ID_DO_CARTAO],
    abertosPorPadrao: recolhivel?.abertoPorPadrao,
  });
  const nome = useWatch({
    control: form.control,
    name: campo<T>("nome_completo"),
    disabled: !recolhivel,
  });
  const email = useWatch({ control: form.control, name: campo<T>("email"), disabled: !recolhivel });
  const aberto = !recolhivel || abertos.has(ID_DO_CARTAO);

  useEffect(() => {
    if (!recolhivel) return;
    return form.subscribe({
      formState: { errors: true },
      callback: ({ errors: erros }) => {
        if (erros?.nome_completo || erros?.email) abrirVarios([ID_DO_CARTAO]);
      },
    });
  }, [form, recolhivel, abrirVarios]);

  const resumo = [String(nome ?? "").trim(), String(email ?? "").trim()]
    .filter(Boolean)
    .join(" · ");

  return (
    <Panel
      titulo={recolhivel ? "Dados pessoais e resumo" : "Dados pessoais"}
      subtitulo={recolhivel ? resumo || "Preencha seu nome e e-mail." : undefined}
      acoes={
        recolhivel ? (
          <Button aria-expanded={aberto} onClick={() => alternar(ID_DO_CARTAO)}>
            {aberto ? "Concluir" : "Editar"}
          </Button>
        ) : undefined
      }
    >
      <div className={estilos.grade} hidden={!aberto}>
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
          {sugerirResumo && (
            <SugestaoCampo
              form={form}
              campo={campo<T>("resumo_profissional")}
              rotuloBloco="resumo"
              sugerir={sugerirResumo}
            />
          )}
        </div>
      </div>
    </Panel>
  );
}
