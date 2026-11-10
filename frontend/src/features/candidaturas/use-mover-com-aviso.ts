import { useCallback } from "react";
import type { StatusCandidatura } from "../../api/tipos";
import { useToast } from "../../shared/ui/use-toast";
import { ROTULO_STATUS } from "./status";
import { useMoverCandidatura } from "./use-candidaturas";

/** Move a candidatura e avisa o resultado (sucesso ou erro); usado pelo arrasto e pelo detalhe. */
export function useMoverComAviso() {
  const { mutate } = useMoverCandidatura();
  const { notificar } = useToast();

  return useCallback(
    (id: string, novoStatus: StatusCandidatura, posicao?: number) =>
      mutate(
        { id, novoStatus, posicao },
        {
          onSuccess: () =>
            notificar(`Candidatura movida para ${ROTULO_STATUS[novoStatus]}.`, "sucesso"),
          onError: (erro) => notificar(erro.message, "erro"),
        },
      ),
    [mutate, notificar],
  );
}
