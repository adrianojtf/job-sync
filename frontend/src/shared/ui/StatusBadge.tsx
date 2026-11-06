import type { ReactNode } from "react";
import estilos from "./StatusBadge.module.css";

export type TomStatus = "sucesso" | "alerta" | "erro" | "destaque" | "neutro";

interface Props {
  tom?: TomStatus;
  children: ReactNode;
}

/** Selo de status. O texto sempre descreve o estado: a cor não é a única pista. */
export function StatusBadge({ tom = "neutro", children }: Props) {
  return <span className={`${estilos.selo} ${estilos[tom]}`}>{children}</span>;
}
