import { useDroppable } from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import type { CSSProperties } from "react";
import type { Candidatura, StatusCandidatura } from "../../api/tipos";
import { CartaoCandidatura } from "./CartaoCandidatura";
import estilos from "./CandidaturasPage.module.css";
import { idDaColuna } from "./movimento";
import { COR_STATUS, ROTULO_STATUS } from "./status";

const contar = (quantidade: number) =>
  `${quantidade} ${quantidade === 1 ? "candidatura" : "candidaturas"}`;

interface Props {
  status: StatusCandidatura;
  candidaturas: Candidatura[];
  destacada: boolean;
  aoAbrir: (candidatura: Candidatura) => void;
}

/** Coluna do quadro: cabeçalho com contagem e área de soltura com os cartões ordenáveis. */
export function ColunaKanban({ status, candidaturas, destacada, aoAbrir }: Props) {
  const { setNodeRef } = useDroppable({ id: idDaColuna(status) });
  const classes = [estilos.coluna, destacada && estilos.colunaDestacada].filter(Boolean).join(" ");

  return (
    <section
      className={classes}
      aria-label={`${ROTULO_STATUS[status]}, ${contar(candidaturas.length)}`}
      style={{ "--cor-coluna": COR_STATUS[status] } as CSSProperties}
    >
      <h2 className={estilos.cabecalhoColuna}>
        {ROTULO_STATUS[status]}
        <span className={estilos.contagem} aria-hidden="true">
          {candidaturas.length}
        </span>
      </h2>
      <div ref={setNodeRef} className={estilos.areaSoltura}>
        <SortableContext
          items={candidaturas.map((candidatura) => candidatura.id)}
          strategy={verticalListSortingStrategy}
        >
          {candidaturas.length === 0 ? (
            <p className={estilos.vazio}>Nenhuma candidatura</p>
          ) : (
            <ul className={estilos.cartoes}>
              {candidaturas.map((candidatura) => (
                <CartaoCandidatura
                  key={candidatura.id}
                  candidatura={candidatura}
                  aoAbrir={() => aoAbrir(candidatura)}
                />
              ))}
            </ul>
          )}
        </SortableContext>
      </div>
    </section>
  );
}
