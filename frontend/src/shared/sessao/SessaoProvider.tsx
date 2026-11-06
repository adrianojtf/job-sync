import { useCallback, useMemo, useState, type ReactNode } from "react";
import { CHAVE_SESSAO, SessaoContext } from "./sessao-context";

// O armazenamento pode estar bloqueado (aba privada, dados limpos): a sessão segue em memória.
function lerPerfilSalvo(): string | null {
  try {
    return localStorage.getItem(CHAVE_SESSAO);
  } catch {
    return null;
  }
}

function gravarPerfil(perfil: string | null): void {
  try {
    if (perfil === null) localStorage.removeItem(CHAVE_SESSAO);
    else localStorage.setItem(CHAVE_SESSAO, perfil);
  } catch {
    // Sem persistência: a sessão vale até fechar a aba.
  }
}

/** Guarda o perfil ativo (login por identificador do JOB-0004) até o usuário clicar em Sair. */
export function SessaoProvider({ children }: { children: ReactNode }) {
  const [perfil, setPerfil] = useState<string | null>(lerPerfilSalvo);

  const entrar = useCallback((novoPerfil: string) => {
    gravarPerfil(novoPerfil);
    setPerfil(novoPerfil);
  }, []);

  const sair = useCallback(() => {
    gravarPerfil(null);
    setPerfil(null);
  }, []);

  const valor = useMemo(() => ({ perfil, entrar, sair }), [perfil, entrar, sair]);
  return <SessaoContext.Provider value={valor}>{children}</SessaoContext.Provider>;
}
