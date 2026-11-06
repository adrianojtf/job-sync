import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import type { CurriculoSalvo, Vaga } from "../../api/tipos";
import { primeiraLinha } from "../../shared/formatacao";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Modal } from "../../shared/ui/Modal";
import { useToast } from "../../shared/ui/use-toast";
import { useCurriculos } from "../curriculos/use-curriculos";
import { useCriarCandidatura } from "./use-vagas-salvas";

interface Props {
  vaga: Vaga | null;
  aoFechar: () => void;
}

interface Dados {
  empresa: string;
  cargo: string;
  curriculoId: string;
}

const ID_FORMULARIO = "form-criar-candidatura";

/** RF8.4 — transforma a vaga em candidatura (Aplicado), registrando o PDF usado. */
export function CriarCandidaturaModal({ vaga, aoFechar }: Props) {
  const curriculos = useCurriculos();
  if (!vaga) return null;
  if (!curriculos.isSuccess) {
    return (
      <Modal aberto titulo="Criar candidatura" aoFechar={aoFechar}>
        {curriculos.isError ? (
          <Aviso tom="erro">
            Não foi possível carregar os currículos: {curriculos.error.message}
          </Aviso>
        ) : (
          <p>Carregando currículos…</p>
        )}
      </Modal>
    );
  }
  return (
    <FormularioCandidatura
      key={vaga.id}
      vaga={vaga}
      biblioteca={curriculos.data}
      aoFechar={aoFechar}
    />
  );
}

interface PropsFormulario {
  vaga: Vaga;
  biblioteca: CurriculoSalvo[];
  aoFechar: () => void;
}

function FormularioCandidatura({ vaga, biblioteca, aoFechar }: PropsFormulario) {
  const criar = useCriarCandidatura();
  const { notificar } = useToast();
  const form = useForm<Dados>({
    defaultValues: {
      empresa: "",
      cargo: primeiraLinha(vaga.texto_descricao, 120),
      curriculoId: biblioteca[0]?.id ?? "",
    },
  });
  const { errors } = form.formState;
  const semCurriculo = biblioteca.length === 0;
  const obrigatorio = (mensagem: string) => ({
    validate: (v: string) => v.trim() !== "" || mensagem,
  });

  const salvar = (dados: Dados) =>
    criar.mutate(
      {
        vaga_id: vaga.id,
        curriculo_salvo_id: dados.curriculoId,
        empresa: dados.empresa.trim(),
        cargo: dados.cargo.trim(),
      },
      {
        onSuccess: () => {
          notificar("Candidatura criada em Aplicado.", "sucesso");
          aoFechar();
        },
      },
    );

  return (
    <Modal
      aberto
      titulo="Criar candidatura"
      descricao="A candidatura entra na coluna Aplicado e a vaga sai desta lista."
      aoFechar={aoFechar}
      rodape={
        <>
          <Button onClick={aoFechar}>Cancelar</Button>
          <Button
            type="submit"
            form={ID_FORMULARIO}
            variante="primary"
            disabled={semCurriculo}
            carregando={criar.isPending}
          >
            Criar candidatura
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
          rotulo="Empresa"
          erro={errors.empresa?.message}
          {...form.register("empresa", obrigatorio("Informe a empresa."))}
        />
        <Field
          rotulo="Cargo"
          erro={errors.cargo?.message}
          {...form.register("cargo", obrigatorio("Informe o cargo."))}
        />
        {semCurriculo ? (
          <Aviso tom="alerta">
            A candidatura registra qual PDF você enviou. Salve um em{" "}
            <Link to="/curriculos">Meus currículos</Link> primeiro.
          </Aviso>
        ) : (
          <Field
            tipoCampo="select"
            rotulo="Currículo usado"
            opcoes={biblioteca.map((curriculo) => ({
              valor: curriculo.id,
              rotulo: curriculo.nome_referencia,
            }))}
            {...form.register("curriculoId")}
          />
        )}
        {criar.isError && (
          <p role="alert" style={{ color: "var(--red)", margin: 0 }}>
            {criar.error.message}
          </p>
        )}
      </form>
    </Modal>
  );
}
