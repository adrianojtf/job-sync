import { createContext } from "react";

export type TomToast = "info" | "sucesso" | "erro";

export interface ToastContexto {
  notificar: (mensagem: string, tom?: TomToast) => void;
}

export const ToastContext = createContext<ToastContexto | null>(null);
