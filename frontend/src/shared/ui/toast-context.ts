import { createContext } from "react";

export type TomToast = "info" | "sucesso" | "erro";

export interface AcaoDoToast {
  rotulo: string;
  aoClicar: () => void;
}

export interface OpcoesDoToast {
  /** Botão no aviso (ex.: "Desfazer"); com ele o aviso dura mais, para dar tempo de usá-lo. */
  acao?: AcaoDoToast;
  duracaoMs?: number;
}

export interface ToastContexto {
  notificar: (mensagem: string, tom?: TomToast, opcoes?: OpcoesDoToast) => void;
}

export const ToastContext = createContext<ToastContexto | null>(null);
