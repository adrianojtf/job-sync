import { createContext } from "react";

export const CHAVE_SESSAO = "jobsync.perfil";

export interface Sessao {
  perfil: string | null;
  entrar: (perfil: string) => void;
  sair: () => void;
}

export const SessaoContext = createContext<Sessao | null>(null);
