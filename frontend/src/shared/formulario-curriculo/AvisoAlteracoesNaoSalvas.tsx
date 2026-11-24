import { useContext, useEffect, type RefObject } from "react";
import { UNSAFE_DataRouterContext, useBlocker } from "react-router-dom";
import { ConfirmacaoModal } from "../ui/ConfirmacaoModal";

interface Props {
  /** Há alterações ainda não salvas ou não enviadas. */
  alterado: boolean;
  /** Quando `true`, a saída já foi confirmada pelo usuário em outro diálogo e não pergunta de novo. */
  saidaConfirmada?: RefObject<boolean>;
}

/**
 * Pede confirmação ao sair de um formulário com alterações pendentes (JOB-0046): ao navegar para
 * outra tela do app (diálogo) e ao fechar ou recarregar a aba (aviso do navegador). Só bloqueia
 * quando a rota muda: mudar apenas a busca ou o estado da mesma tela não pergunta.
 */
export function AvisoAlteracoesNaoSalvas({ alterado, saidaConfirmada }: Props) {
  useAvisoAoFecharAba(alterado);
  const roteadorDeDados = useContext(UNSAFE_DataRouterContext);
  return roteadorDeDados ? (
    <BloqueioDeNavegacao alterado={alterado} saidaConfirmada={saidaConfirmada} />
  ) : null;
}

function useAvisoAoFecharAba(alterado: boolean) {
  useEffect(() => {
    if (!alterado) return;
    const avisar = (evento: BeforeUnloadEvent) => {
      evento.preventDefault();
      evento.returnValue = "";
    };
    window.addEventListener("beforeunload", avisar);
    return () => window.removeEventListener("beforeunload", avisar);
  }, [alterado]);
}

function BloqueioDeNavegacao({ alterado, saidaConfirmada }: Props) {
  const bloqueio = useBlocker(
    ({ currentLocation, nextLocation }) =>
      alterado &&
      saidaConfirmada?.current !== true &&
      currentLocation.pathname !== nextLocation.pathname,
  );
  return (
    <ConfirmacaoModal
      aberto={bloqueio.state === "blocked"}
      titulo="Sair sem salvar?"
      descricao="Você tem alterações que ainda não foram salvas. Se sair agora, elas serão perdidas."
      rotuloConfirmar="Sair sem salvar"
      aoConfirmar={() => bloqueio.state === "blocked" && bloqueio.proceed()}
      aoCancelar={() => bloqueio.state === "blocked" && bloqueio.reset()}
    />
  );
}
