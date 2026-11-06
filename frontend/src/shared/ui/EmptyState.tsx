import type { ReactNode } from "react";
import estilos from "./EmptyState.module.css";

interface Props {
  titulo: string;
  descricao?: string;
  acao?: ReactNode;
}

export function EmptyState({ titulo, descricao, acao }: Props) {
  return (
    <div className={estilos.vazio}>
      <h3 className={estilos.titulo}>{titulo}</h3>
      {descricao && <p className={estilos.descricao}>{descricao}</p>}
      {acao}
    </div>
  );
}
