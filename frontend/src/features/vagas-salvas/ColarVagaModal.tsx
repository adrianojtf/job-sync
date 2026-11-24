import { useForm, useWatch } from "react-hook-form";
import type { DadosVaga } from "../../api/tipos";
import { CampoLinkVaga } from "../../shared/leitura-de-vaga/CampoLinkVaga";
import { PreencherPeloTexto } from "../../shared/leitura-de-vaga/PreencherPeloTexto";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Modal } from "../../shared/ui/Modal";
import { useToast } from "../../shared/ui/use-toast";
import estilos from "./ColarVagaModal.module.css";
import { useColarVaga } from "./use-vagas-salvas";

interface Props {
  aberto: boolean;
  aoFechar: () => void;
}

interface Dados {
  texto: string;
  url: string;
  cargo: string;
  empresa: string;
  local: string;
}

const VAZIO: Dados = { texto: "", url: "", cargo: "", empresa: "", local: "" };
const ID_FORMULARIO = "form-colar-vaga";

/** Campos opcionais vazios não são enviados, como antes da leitura por link. */
const opcional = (valor: string) => valor.trim() || undefined;

/**
 * RF8.2 — registra uma vaga colada (alternativa à extensão de navegador) ou lida de um link.
 * O que a leitura encontra é um rascunho: a pessoa confere e corrige antes de salvar.
 */
export function ColarVagaModal({ aberto, aoFechar }: Props) {
  const form = useForm<Dados>({ defaultValues: VAZIO });
  const colar = useColarVaga();
  const { notificar } = useToast();
  const { errors } = form.formState;
  const link = useWatch({ control: form.control, name: "url" });
  const texto = useWatch({ control: form.control, name: "texto" });

  const fechar = () => {
    form.reset(VAZIO);
    colar.reset();
    aoFechar();
  };

  const preencherComDadosLidos = (dados: DadosVaga) => {
    const opcoes = { shouldDirty: true };
    form.setValue("texto", dados.descricao, { ...opcoes, shouldValidate: true });
    if (dados.cargo) form.setValue("cargo", dados.cargo, opcoes);
    if (dados.empresa) form.setValue("empresa", dados.empresa, opcoes);
    if (dados.local) form.setValue("local", dados.local, opcoes);
    if (dados.url) form.setValue("url", dados.url, opcoes);
  };

  const salvar = (dados: Dados) =>
    colar.mutate(
      {
        texto_descricao: dados.texto.trim(),
        url_origem: dados.url.trim() || null,
        cargo: opcional(dados.cargo),
        empresa: opcional(dados.empresa),
        local: opcional(dados.local),
      },
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
      descricao="Cole o link da vaga e leia os dados, ou cole a descrição completa. A primeira linha vira o título na lista."
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
        <CampoLinkVaga
          rotulo="Link da vaga (opcional)"
          valor={link}
          aoAlterar={(valor) => form.setValue("url", valor, { shouldDirty: true })}
          aoLer={preencherComDadosLidos}
        />
        <div className={estilos.identificacao}>
          <Field rotulo="Título (opcional)" {...form.register("cargo")} />
          <Field rotulo="Empresa (opcional)" {...form.register("empresa")} />
          <Field rotulo="Local (opcional)" {...form.register("local")} />
        </div>
        <Field
          tipoCampo="textarea"
          rotulo="Descrição da vaga"
          rows={8}
          erro={errors.texto?.message}
          {...form.register("texto", {
            validate: (v) => v.trim() !== "" || "Cole a descrição da vaga.",
          })}
        />
        <PreencherPeloTexto texto={texto} aoLer={preencherComDadosLidos} />
        {colar.isError && (
          <p role="alert" style={{ color: "var(--red)", margin: 0 }}>
            {colar.error.message}
          </p>
        )}
      </form>
    </Modal>
  );
}
