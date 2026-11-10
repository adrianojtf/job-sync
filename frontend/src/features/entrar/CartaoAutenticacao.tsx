import type { ReactNode } from "react";
import estilos from "./EntrarPage.module.css";

interface Props {
  titulo: string;
  descricao?: string;
  children: ReactNode;
}

/** Moldura comum das telas públicas de autenticação (entrar, cadastrar, confirmar, redefinir). */
export function CartaoAutenticacao({ titulo, descricao, children }: Props) {
  return (
    <main className={estilos.pagina}>
      <div className={estilos.cartao}>
        <div className={estilos.marca}>
          <span className={estilos.marcaIcone} aria-hidden="true">
            js
          </span>
          job-sync
        </div>
        <h1 className={estilos.titulo}>{titulo}</h1>
        {descricao && <p className={estilos.descricao}>{descricao}</p>}
        {children}
      </div>
    </main>
  );
}
