import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import type { ReactNode } from "react";
import { Button } from "../ui/Button";
import estilos from "./FormularioCurriculo.module.css";

export interface ResumoDoItem {
  titulo: string;
  subtitulo?: string;
  /** Texto à direita (ex.: o período). */
  meta?: string;
  /** Letra do avatar; sem ela, a primeira letra do título. */
  inicial?: string;
  chips?: ReactNode;
}

interface Props {
  id: string;
  indice: number;
  total: number;
  rotuloItem: string;
  resumo: ResumoDoItem;
  aberto: boolean;
  reordenavel: boolean;
  aoAlternar: () => void;
  aoMover: (direcao: -1 | 1) => void;
  children: ReactNode;
}

/**
 * Item recolhível de uma lista do formulário (JOB-0046): alça de arrasto, resumo, botões de mover
 * e de abrir. O conteúdo (`children`) fica sempre montado, só escondido, para a validação e o
 * foco por erro continuarem enxergando os campos de um cartão recolhido.
 */
export function CartaoDaLista({
  id,
  indice,
  total,
  rotuloItem,
  resumo,
  aberto,
  reordenavel,
  aoAlternar,
  aoMover,
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
  const titulo = (resumo.titulo ?? "").trim() || `${rotuloItem} ${indice + 1}`;
  const classes = [
    estilos.cartao,
    aberto && estilos.cartaoAberto,
    isDragging && estilos.cartaoArrastando,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div
      ref={setNodeRef}
      role="group"
      aria-label={`${rotuloItem} ${indice + 1}`}
      data-item-id={id}
      className={classes}
      style={{ transform: CSS.Transform.toString(transform), transition }}
    >
      <div className={estilos.linhaDoCartao}>
        {reordenavel && (
          <button
            ref={setActivatorNodeRef}
            type="button"
            className={estilos.alca}
            data-alca-id={id}
            aria-label={`Mover ${titulo}. Posição ${indice + 1} de ${total}`}
            title="Arraste para reordenar"
            {...attributes}
            {...listeners}
          >
            <span aria-hidden="true">⠿</span>
          </button>
        )}
        <span className={estilos.avatar} aria-hidden="true">
          {(resumo.inicial ?? titulo).trim().charAt(0).toUpperCase() || "?"}
        </span>
        <div className={estilos.tituloDoCartao}>
          <button
            type="button"
            className={estilos.botaoDoTitulo}
            aria-expanded={aberto}
            aria-label={`Editar ${titulo}`}
            onClick={aoAlternar}
          >
            <strong>{(resumo.titulo ?? "").trim() || `${rotuloItem} sem título`}</strong>
          </button>
          {resumo.subtitulo && <small>{resumo.subtitulo}</small>}
        </div>
        {resumo.meta && <span className={estilos.metaDoCartao}>{resumo.meta}</span>}
        <div className={estilos.acoesDoCartao}>
          {reordenavel && (
            <span className={estilos.mover}>
              <button
                type="button"
                className={estilos.botaoIcone}
                data-mover="-1"
                disabled={indice === 0}
                aria-label={`Mover ${titulo} para cima`}
                onClick={() => aoMover(-1)}
              >
                ↑
              </button>
              <button
                type="button"
                className={estilos.botaoIcone}
                data-mover="1"
                disabled={indice === total - 1}
                aria-label={`Mover ${titulo} para baixo`}
                onClick={() => aoMover(1)}
              >
                ↓
              </button>
            </span>
          )}
          <button
            type="button"
            className={`${estilos.botaoIcone} ${estilos.chevron}`}
            aria-expanded={aberto}
            aria-label={aberto ? `Recolher ${titulo}` : `Abrir ${titulo}`}
            onClick={aoAlternar}
          >
            <span aria-hidden="true">⌄</span>
          </button>
        </div>
      </div>
      {resumo.chips && <div className={estilos.chipsDoCartao}>{resumo.chips}</div>}
      <div className={estilos.corpoDoCartao} hidden={!aberto}>
        {children}
        <div className={estilos.concluir}>
          <Button onClick={aoAlternar}>Concluir</Button>
        </div>
      </div>
    </div>
  );
}
