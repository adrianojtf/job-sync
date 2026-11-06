import type { ReactNode } from "react";
import estilos from "./EmptyState.module.css";

interface Props {
  titulo: string;
  descricao?: string;
  /** Texto com links ou outros elementos, no lugar de `descricao`. */
  children?: ReactNode;
  acao?: ReactNode;
}

export function EmptyState({ titulo, descricao, children, acao }: Props) {
  const texto = children ?? descricao;
  return (
    <div className={estilos.vazio}>
      <h3 className={estilos.titulo}>{titulo}</h3>
      {texto && <p className={estilos.descricao}>{texto}</p>}
      {acao}
    </div>
  );
}
