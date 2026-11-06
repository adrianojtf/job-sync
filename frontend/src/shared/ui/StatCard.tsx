import type { ReactNode } from "react";
import estilos from "./StatCard.module.css";

interface Props {
  rotulo: string;
  valor: ReactNode;
  icone?: string;
  rodape?: ReactNode;
}

export function StatCard({ rotulo, valor, icone, rodape }: Props) {
  return (
    <div className={estilos.cartao} role="group" aria-label={rotulo}>
      <div className={estilos.cabecalho}>
        <span>{rotulo}</span>
        {icone && (
          <span className={estilos.icone} aria-hidden="true">
            {icone}
          </span>
        )}
      </div>
      <strong className={estilos.valor}>{valor}</strong>
      {rodape && <div className={estilos.rodape}>{rodape}</div>}
    </div>
  );
}
