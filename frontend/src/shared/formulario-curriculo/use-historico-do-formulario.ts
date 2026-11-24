import { useCallback, useMemo, useRef } from "react";
import type { FieldValues, UseFormReturn } from "react-hook-form";

/** Instantâneo do formulário antes de uma alteração, para o "Desfazer" (JOB-0046). */
export interface HistoricoDoFormulario {
  /** Guarda os valores atuais; chame antes de reordenar, adicionar, remover ou ordenar. */
  registrar: () => void;
  /** Restaura os valores guardados, mantendo o formulário sujo em relação ao salvo. */
  desfazer: () => void;
}

export function useHistoricoDoFormulario<T extends FieldValues>(
  form: UseFormReturn<T>,
): HistoricoDoFormulario {
  const instantaneo = useRef<T | null>(null);

  const registrar = useCallback(() => {
    instantaneo.current = structuredClone(form.getValues());
  }, [form]);

  const desfazer = useCallback(() => {
    if (instantaneo.current === null) return;
    form.reset(instantaneo.current, { keepDefaultValues: true });
    instantaneo.current = null;
  }, [form]);

  return useMemo(() => ({ registrar, desfazer }), [registrar, desfazer]);
}
