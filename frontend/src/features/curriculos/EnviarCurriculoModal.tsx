import { useState, type FormEvent } from "react";
import { arquivoParaBase64, validarArquivoPdf } from "../../shared/arquivos/arquivos";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Modal } from "../../shared/ui/Modal";
import { useToast } from "../../shared/ui/use-toast";
import { useEnviarCurriculo } from "./use-curriculos";

interface Props {
  aberto: boolean;
  aoFechar: () => void;
}

interface Erros {
  nome?: string;
  arquivo?: string;
}

const ID_FORMULARIO = "form-enviar-curriculo";

export function EnviarCurriculoModal({ aberto, aoFechar }: Props) {
  const [nome, setNome] = useState("");
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [erros, setErros] = useState<Erros>({});
  const envio = useEnviarCurriculo();
  const { notificar } = useToast();

  const fechar = () => {
    setNome("");
    setArquivo(null);
    setErros({});
    envio.reset();
    aoFechar();
  };

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault();
    const novosErros: Erros = {
      nome: nome.trim() ? undefined : "Informe um nome de referência.",
      arquivo: validarArquivoPdf(arquivo),
    };
    setErros(novosErros);
    if (novosErros.nome || novosErros.arquivo || !arquivo) return;
    envio.mutate(
      { nome_referencia: nome.trim(), pdf_base64: await arquivoParaBase64(arquivo) },
      {
        onSuccess: () => {
          notificar("Currículo enviado.", "sucesso");
          fechar();
        },
      },
    );
  };

  return (
    <Modal
      aberto={aberto}
      titulo="Enviar currículo"
      descricao="Salve um PDF na sua biblioteca para reutilizá-lo depois."
      aoFechar={fechar}
      rodape={
        <>
          <Button onClick={fechar}>Cancelar</Button>
          <Button
            type="submit"
            form={ID_FORMULARIO}
            variante="primary"
            carregando={envio.isPending}
          >
            Enviar
          </Button>
        </>
      }
    >
      <form id={ID_FORMULARIO} onSubmit={enviar} noValidate>
        <Field
          rotulo="Nome de referência"
          placeholder="Ex.: Backend Java 2026"
          value={nome}
          onChange={(evento) => setNome(evento.target.value)}
          erro={erros.nome}
        />
        <Field
          rotulo="Arquivo PDF"
          type="file"
          accept="application/pdf,.pdf"
          ajuda="Somente PDF, até 5 MB."
          onChange={(evento) => setArquivo(evento.target.files?.[0] ?? null)}
          erro={erros.arquivo}
        />
        {envio.isError && (
          <p role="alert" style={{ color: "var(--red)", margin: 0 }}>
            {envio.error.message}
          </p>
        )}
      </form>
    </Modal>
  );
}
