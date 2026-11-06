import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Modal } from "../../shared/ui/Modal";
import { ROTA_AJUSTAR_VAGA, type EstadoAjustarVaga } from "./navegacao";

interface Props {
  aberto: boolean;
  aoFechar: () => void;
}

interface DadosVaga {
  cargo: string;
  empresa: string;
  descricao: string;
}

const VAZIO: DadosVaga = { cargo: "", empresa: "", descricao: "" };
const ID_FORMULARIO = "form-ajustar-vaga-modal";
const obrigatorio = (mensagem: string) => ({
  validate: (valor: string) => valor.trim() !== "" || mensagem,
});

/** Modal do protótipo: coleta a vaga e abre "Ajustar para uma vaga" já analisando (RF3.7, RF6.1). */
export function AjustarVagaModal({ aberto, aoFechar }: Props) {
  const navegar = useNavigate();
  const form = useForm<DadosVaga>({ defaultValues: VAZIO });
  const { errors } = form.formState;

  const fechar = () => {
    form.reset(VAZIO);
    aoFechar();
  };

  const irParaAjuste = (dados: DadosVaga) => {
    const estado: EstadoAjustarVaga = {
      cargo: dados.cargo.trim(),
      empresa: dados.empresa.trim(),
      descricao: dados.descricao.trim(),
      analisarAoAbrir: true,
      pedido: Date.now(),
    };
    fechar();
    navegar(ROTA_AJUSTAR_VAGA, { state: estado });
  };

  return (
    <Modal
      aberto={aberto}
      titulo="Ajustar currículo para uma vaga"
      descricao="Adicione os dados da oportunidade. Você poderá revisar cada resultado antes de usar."
      aoFechar={fechar}
      rodape={
        <>
          <Button onClick={fechar}>Cancelar</Button>
          <Button type="submit" form={ID_FORMULARIO} variante="primary">
            Analisar vaga <span aria-hidden="true">→</span>
          </Button>
        </>
      }
    >
      <form
        id={ID_FORMULARIO}
        onSubmit={(evento) => void form.handleSubmit(irParaAjuste)(evento)}
        noValidate
      >
        <Field
          rotulo="Título da vaga"
          placeholder="Ex.: Senior Java Backend Developer"
          erro={errors.cargo?.message}
          {...form.register("cargo", obrigatorio("Informe o título da vaga."))}
        />
        <Field
          rotulo="Empresa"
          placeholder="Ex.: Empresa ou organização"
          {...form.register("empresa")}
        />
        <Field
          tipoCampo="textarea"
          rotulo="Descrição da vaga"
          placeholder="Cole aqui a descrição completa da oportunidade…"
          erro={errors.descricao?.message}
          {...form.register("descricao", obrigatorio("Cole a descrição da vaga."))}
        />
      </form>
    </Modal>
  );
}
