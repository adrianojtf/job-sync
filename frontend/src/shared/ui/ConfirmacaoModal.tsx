import { Button } from "./Button";
import { Modal } from "./Modal";

interface Props {
  aberto: boolean;
  titulo: string;
  descricao: string;
  rotuloConfirmar: string;
  confirmando?: boolean;
  aoConfirmar: () => void;
  aoCancelar: () => void;
}

/** Confirmação de ações destrutivas (ex.: remover um currículo). */
export function ConfirmacaoModal({
  aberto,
  titulo,
  descricao,
  rotuloConfirmar,
  confirmando = false,
  aoConfirmar,
  aoCancelar,
}: Props) {
  return (
    <Modal
      aberto={aberto}
      titulo={titulo}
      descricao={descricao}
      aoFechar={aoCancelar}
      rodape={
        <>
          <Button onClick={aoCancelar}>Cancelar</Button>
          <Button variante="primary" carregando={confirmando} onClick={aoConfirmar}>
            {rotuloConfirmar}
          </Button>
        </>
      }
    />
  );
}
