import { useForm } from "react-hook-form";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Modal } from "../../shared/ui/Modal";
import { useToast } from "../../shared/ui/use-toast";
import { useColarVaga } from "./use-vagas-salvas";

interface Props {
  aberto: boolean;
  aoFechar: () => void;
}

interface Dados {
  texto: string;
  url: string;
}

const VAZIO: Dados = { texto: "", url: "" };
const ID_FORMULARIO = "form-colar-vaga";

/** RF8.2 — registra uma vaga colada (alternativa à extensão de navegador). */
export function ColarVagaModal({ aberto, aoFechar }: Props) {
  const form = useForm<Dados>({ defaultValues: VAZIO });
  const colar = useColarVaga();
  const { notificar } = useToast();
  const { errors } = form.formState;

  const fechar = () => {
    form.reset(VAZIO);
    colar.reset();
    aoFechar();
  };

  const salvar = (dados: Dados) =>
    colar.mutate(
      { texto_descricao: dados.texto.trim(), url_origem: dados.url.trim() || null },
      {
        onSuccess: () => {
          notificar("Vaga salva.", "sucesso");
          fechar();
        },
      },
    );

  return (
    <Modal
      aberto={aberto}
      titulo="Colar vaga"
      descricao="Cole a descrição completa. A primeira linha vira o título na lista."
      aoFechar={fechar}
      rodape={
        <>
          <Button onClick={fechar}>Cancelar</Button>
          <Button
            type="submit"
            form={ID_FORMULARIO}
            variante="primary"
            carregando={colar.isPending}
          >
            Salvar vaga
          </Button>
        </>
      }
    >
      <form
        id={ID_FORMULARIO}
        onSubmit={(evento) => void form.handleSubmit(salvar)(evento)}
        noValidate
      >
        <Field
          tipoCampo="textarea"
          rotulo="Descrição da vaga"
          rows={8}
          erro={errors.texto?.message}
          {...form.register("texto", {
            validate: (v) => v.trim() !== "" || "Cole a descrição da vaga.",
          })}
        />
        <Field
          rotulo="Link da vaga (opcional)"
          type="url"
          placeholder="https://…"
          {...form.register("url")}
        />
        {colar.isError && (
          <p role="alert" style={{ color: "var(--red)", margin: 0 }}>
            {colar.error.message}
          </p>
        )}
      </form>
    </Modal>
  );
}
