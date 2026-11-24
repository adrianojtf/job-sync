import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { ToastContext, type AcaoDoToast, type OpcoesDoToast, type TomToast } from "./toast-context";
import estilos from "./Toast.module.css";

interface Aviso {
  mensagem: string;
  tom: TomToast;
  id: number;
  acao?: AcaoDoToast;
  duracaoMs?: number;
}

/** Com uma ação, o aviso fica mais tempo na tela para o usuário conseguir usá-la. */
const DURACAO_COM_ACAO_MS = 6000;

interface Props {
  children: ReactNode;
  duracaoMs?: number;
}

/** Mostra avisos curtos no canto da tela (comportamento do protótipo). Erros usam role="alert". */
export function ToastProvider({ children, duracaoMs = 2600 }: Props) {
  const [aviso, setAviso] = useState<Aviso | null>(null);

  const notificar = useCallback(
    (mensagem: string, tom: TomToast = "info", opcoes: OpcoesDoToast = {}) => {
      setAviso({ mensagem, tom, id: Date.now(), ...opcoes });
    },
    [],
  );

  useEffect(() => {
    if (!aviso) return;
    const duracao = aviso.duracaoMs ?? (aviso.acao ? DURACAO_COM_ACAO_MS : duracaoMs);
    const temporizador = setTimeout(() => setAviso(null), duracao);
    return () => clearTimeout(temporizador);
  }, [aviso, duracaoMs]);

  const usarAcao = (acao: AcaoDoToast) => {
    acao.aoClicar();
    setAviso(null);
  };

  const contexto = useMemo(() => ({ notificar }), [notificar]);
  const erro = aviso?.tom === "erro";

  return (
    <ToastContext.Provider value={contexto}>
      {children}
      <div className={estilos.toast} role="status" aria-live="polite">
        {aviso && !erro && (
          <>
            <span>{aviso.mensagem}</span>
            {aviso.acao && (
              <button type="button" className={estilos.acao} onClick={() => usarAcao(aviso.acao!)}>
                {aviso.acao.rotulo}
              </button>
            )}
          </>
        )}
      </div>
      <div className={`${estilos.toast} ${estilos.erro}`} role="alert">
        {erro && aviso?.mensagem}
      </div>
    </ToastContext.Provider>
  );
}
