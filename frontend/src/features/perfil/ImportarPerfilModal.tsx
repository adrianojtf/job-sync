import { useState, type FormEvent } from "react";
import type { PerfilEstruturado } from "../../api/tipos";
import { validarArquivoPdf } from "../../shared/arquivos/arquivos";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Modal } from "../../shared/ui/Modal";
import { useCurriculos } from "../curriculos/use-curriculos";
import { useImportarPerfil } from "./use-perfil-estruturado";

interface Props {
  aberto: boolean;
  aoFechar: () => void;
  aoImportar: (rascunho: PerfilEstruturado) => void;
}

const ID_FORMULARIO = "form-importar-perfil";

/** RF4.2 — importa um PDF (novo ou da biblioteca) para pré-preencher o formulário, sem salvar. */
export function ImportarPerfilModal({ aberto, aoFechar, aoImportar }: Props) {
  const [origem, setOrigem] = useState<"arquivo" | "biblioteca">("arquivo");
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [curriculoId, setCurriculoId] = useState("");
  const [erro, setErro] = useState<string>();
  const curriculos = useCurriculos();
  const importacao = useImportarPerfil();
  const biblioteca = curriculos.data ?? [];

  const fechar = () => {
    setArquivo(null);
    setCurriculoId("");
    setErro(undefined);
    importacao.reset();
    aoFechar();
  };

  const importar = (evento: FormEvent) => {
    evento.preventDefault();
    const problema =
      origem === "arquivo"
        ? validarArquivoPdf(arquivo)
        : curriculoId
          ? undefined
          : "Escolha um currículo.";
    setErro(problema);
    if (problema) return;
    importacao.mutate(
      origem === "arquivo"
        ? { tipo: "arquivo", arquivo: arquivo! }
        : { tipo: "biblioteca", curriculoId },
      {
        onSuccess: (rascunho) => {
          aoImportar(rascunho);
          fechar();
        },
      },
    );
  };

  return (
    <Modal
      aberto={aberto}
      titulo="Importar currículo de um PDF"
      descricao="Os campos serão pré-preenchidos para você revisar. Nada é salvo até clicar em Salvar perfil."
      aoFechar={fechar}
      rodape={
        <>
          <Button onClick={fechar}>Cancelar</Button>
          <Button
            type="submit"
            form={ID_FORMULARIO}
            variante="primary"
            carregando={importacao.isPending}
          >
            {importacao.isPending
              ? "Importando… pode levar até 1 minuto"
              : "Importar e pré-preencher"}
          </Button>
        </>
      }
    >
      <form id={ID_FORMULARIO} onSubmit={importar} noValidate>
        <fieldset
          style={{
            border: 0,
            padding: 0,
            margin: "0 0 4px",
            display: "flex",
            gap: 18,
            flexWrap: "wrap",
          }}
        >
          <legend className="sr-only">Origem do PDF</legend>
          <label>
            <input
              type="radio"
              name="origem"
              checked={origem === "arquivo"}
              onChange={() => {
                setOrigem("arquivo");
                setErro(undefined);
              }}
            />{" "}
            Novo arquivo PDF
          </label>
          <label>
            <input
              type="radio"
              name="origem"
              checked={origem === "biblioteca"}
              disabled={biblioteca.length === 0}
              onChange={() => {
                setOrigem("biblioteca");
                setErro(undefined);
              }}
            />{" "}
            Currículo da biblioteca
          </label>
        </fieldset>

        {origem === "arquivo" ? (
          <Field
            rotulo="Arquivo PDF"
            type="file"
            accept="application/pdf,.pdf"
            ajuda="Dica: no LinkedIn, use “Salvar como PDF” no seu perfil. Até 5 MB."
            onChange={(evento) => setArquivo(evento.target.files?.[0] ?? null)}
            erro={erro}
          />
        ) : (
          <Field
            tipoCampo="select"
            rotulo="Currículo"
            opcoes={[
              { valor: "", rotulo: "Selecione…" },
              ...biblioteca.map((item) => ({ valor: item.id, rotulo: item.nome_referencia })),
            ]}
            value={curriculoId}
            onChange={(evento) => setCurriculoId(evento.target.value)}
            erro={erro}
          />
        )}
        {importacao.isError && (
          <p role="alert" style={{ color: "var(--red)", margin: 0 }}>
            {importacao.error.message}
          </p>
        )}
      </form>
    </Modal>
  );
}
