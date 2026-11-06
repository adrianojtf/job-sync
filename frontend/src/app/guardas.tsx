import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useSessao } from "../shared/sessao/use-sessao";

export interface EstadoEntrar {
  de?: string;
}

/** Só renderiza com sessão ativa; sem ela, vai para Entrar lembrando a página pedida. */
export function RotaProtegida({ children }: { children: ReactNode }) {
  const { perfil } = useSessao();
  const local = useLocation();
  if (!perfil) {
    const estado: EstadoEntrar = { de: `${local.pathname}${local.search}` };
    return <Navigate to="/entrar" replace state={estado} />;
  }
  return children;
}

/** Entrar só faz sentido sem sessão: com ela, segue para a página pedida antes do login. */
export function SomenteSemSessao({ children }: { children: ReactNode }) {
  const { perfil } = useSessao();
  const destino = (useLocation().state as EstadoEntrar | null)?.de ?? "/";
  return perfil ? <Navigate to={destino} replace /> : children;
}
