import { useId, type ReactNode } from "react";
import estilos from "./Panel.module.css";

interface Props {
  titulo?: string;
  subtitulo?: string;
  acoes?: ReactNode;
  children: ReactNode;
}

export function Panel({ titulo, subtitulo, acoes, children }: Props) {
  const idTitulo = useId();
  return (
    <section className={estilos.painel} aria-labelledby={titulo ? idTitulo : undefined}>
      {titulo && (
        <header className={estilos.cabecalho}>
          <div>
            <h2 id={idTitulo} className={estilos.titulo}>
              {titulo}
            </h2>
            {subtitulo && <p className={estilos.subtitulo}>{subtitulo}</p>}
          </div>
          {acoes}
        </header>
      )}
      <div className={estilos.corpo}>{children}</div>
    </section>
  );
}
