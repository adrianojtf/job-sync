import type { ReactNode } from "react";
import estilos from "./CabecalhoPagina.module.css";

interface Props {
  titulo: string;
  sobrelinha?: string;
  descricao?: string;
  acoes?: ReactNode;
}

/** Cabeçalho padrão das páginas (bloco "welcome" do protótipo). */
export function CabecalhoPagina({ titulo, sobrelinha, descricao, acoes }: Props) {
  return (
    <header className={estilos.cabecalho}>
      <div>
        {sobrelinha && <div className={estilos.sobrelinha}>{sobrelinha}</div>}
        <h1 className={estilos.titulo}>{titulo}</h1>
        {descricao && <p className={estilos.descricao}>{descricao}</p>}
      </div>
      {acoes}
    </header>
  );
}
