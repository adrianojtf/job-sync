import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import type { ReactNode } from "react";
import estilos from "./FormularioCurriculo.module.css";

interface Props {
  id: string;
  indice: number;
  total: number;
  rotuloItem: string;
  titulo: string;
  reordenavel: boolean;
  aoMover: (direcao: -1 | 1) => void;
  aoRemover: () => void;
  children: ReactNode;
}

/** Item de uma linha só (ex.: idiomas, JOB-0046): alça, campos editáveis na própria linha e botões. */
export function LinhaDaLista({
  id,
  indice,
  total,
  rotuloItem,
  titulo,
  reordenavel,
  aoMover,
  aoRemover,
  children,
}: Props) {
  const {
    attributes,
    listeners,
    setNodeRef,
    setActivatorNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id,
    disabled: !reordenavel,
    attributes: { roleDescription: "item arrastável" },
  });
  const nome = titulo.trim() || `${rotuloItem} ${indice + 1}`;

  return (
    <div
      ref={setNodeRef}
      role="group"
      aria-label={`${rotuloItem} ${indice + 1}`}
      data-item-id={id}
      className={[estilos.linha, isDragging && estilos.cartaoArrastando].filter(Boolean).join(" ")}
      style={{ transform: CSS.Transform.toString(transform), transition }}
    >
      {reordenavel && (
        <button
          ref={setActivatorNodeRef}
          type="button"
          className={estilos.alca}
          data-alca-id={id}
          aria-label={`Mover ${nome}. Posição ${indice + 1} de ${total}`}
          title="Arraste para reordenar"
          {...attributes}
          {...listeners}
        >
          <span aria-hidden="true">⠿</span>
        </button>
      )}
      <div className={estilos.camposDaLinha}>{children}</div>
      <div className={estilos.acoesDoCartao}>
        {reordenavel && (
          <span className={estilos.mover}>
            <button
              type="button"
              className={estilos.botaoIcone}
              data-mover="-1"
              disabled={indice === 0}
              aria-label={`Mover ${nome} para cima`}
              onClick={() => aoMover(-1)}
            >
              ↑
            </button>
            <button
              type="button"
              className={estilos.botaoIcone}
              data-mover="1"
              disabled={indice === total - 1}
              aria-label={`Mover ${nome} para baixo`}
              onClick={() => aoMover(1)}
            >
              ↓
            </button>
          </span>
        )}
        <button
          type="button"
          className={estilos.botaoIcone}
          aria-label={`Remover ${rotuloItem.toLowerCase()} ${indice + 1}`}
          onClick={aoRemover}
        >
          <span aria-hidden="true">×</span>
        </button>
      </div>
    </div>
  );
}
