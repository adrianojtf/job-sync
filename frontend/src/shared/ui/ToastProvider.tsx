import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { ToastContext, type TomToast } from "./toast-context";
import estilos from "./Toast.module.css";

interface Aviso {
  mensagem: string;
  tom: TomToast;
  id: number;
}

interface Props {
  children: ReactNode;
  duracaoMs?: number;
}

/** Mostra avisos curtos no canto da tela (comportamento do protótipo). Erros usam role="alert". */
export function ToastProvider({ children, duracaoMs = 2600 }: Props) {
  const [aviso, setAviso] = useState<Aviso | null>(null);

  const notificar = useCallback((mensagem: string, tom: TomToast = "info") => {
    setAviso({ mensagem, tom, id: Date.now() });
  }, []);

  useEffect(() => {
    if (!aviso) return;
    const temporizador = setTimeout(() => setAviso(null), duracaoMs);
    return () => clearTimeout(temporizador);
  }, [aviso, duracaoMs]);

  const contexto = useMemo(() => ({ notificar }), [notificar]);
  const erro = aviso?.tom === "erro";

  return (
    <ToastContext.Provider value={contexto}>
      {children}
      <div className={estilos.toast} role="status" aria-live="polite">
        {!erro && aviso?.mensagem}
      </div>
      <div className={`${estilos.toast} ${estilos.erro}`} role="alert">
        {erro && aviso?.mensagem}
      </div>
    </ToastContext.Provider>
  );
}
