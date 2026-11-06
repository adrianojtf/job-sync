import { useContext } from "react";
import { SessaoContext, type Sessao } from "./sessao-context";

export function useSessao(): Sessao {
  const sessao = useContext(SessaoContext);
  if (sessao === null) {
    throw new Error("useSessao precisa estar dentro de <SessaoProvider>.");
  }
  return sessao;
}
