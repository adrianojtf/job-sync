import type { ReactNode } from "react";
import estilos from "./Aviso.module.css";

interface Props {
  tom?: "info" | "alerta" | "erro";
  children: ReactNode;
  acao?: ReactNode;
}

/** Caixa de aviso em linha (estado vazio, alerta ou falha de carregamento). */
export function Aviso({ tom = "info", children, acao }: Props) {
  return (
    <div className={`${estilos.aviso} ${estilos[tom]}`} role={tom === "erro" ? "alert" : undefined}>
      <p className={estilos.texto}>{children}</p>
      {acao}
    </div>
  );
}
