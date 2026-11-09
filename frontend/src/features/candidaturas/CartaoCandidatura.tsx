import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import type { Candidatura } from "../../api/tipos";
import { formatarData, formatarTempoRelativo, inicialDe } from "../../shared/formatacao";
import { DESCRICAO_CARTAO } from "./anuncios";
import estilos from "./CandidaturasPage.module.css";

interface PropsCartao {
  candidatura: Candidatura;
  aoAbrir: () => void;
}

/**
 * Cartão do quadro. O cartão inteiro é o ativador do arrasto (inclusive por teclado) e o título é o
 * único botão, que abre o detalhe. O `role` padrão do dnd-kit ("button") é removido para não aninhar
 * botão dentro de botão (spike da tarefa 4.0).
 */
export function CartaoCandidatura({ candidatura, aoAbrir }: PropsCartao) {
  const {
    attributes,
    listeners,
    setNodeRef,
    setActivatorNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: candidatura.id,
    attributes: { roleDescription: DESCRICAO_CARTAO },
  });

  const classes = [estilos.cartao, estilos.cartaoArrastavel, isDragging && estilos.cartaoOrigem]
    .filter(Boolean)
    .join(" ");

  return (
    <li
      ref={(no) => {
        setNodeRef(no);
        setActivatorNodeRef(no);
      }}
      className={classes}
      style={{ transform: CSS.Transform.toString(transform), transition }}
      {...attributes}
      role={undefined}
      {...listeners}
    >
      <button type="button" className={estilos.tituloCartao} onClick={aoAbrir}>
        {candidatura.cargo}
      </button>
      <DadosDoCartao candidatura={candidatura} />
    </li>
  );
}

/** Cartão levantado que acompanha o ponteiro durante o arrasto (sem hooks de ordenação). */
export function CartaoFlutuante({ candidatura }: { candidatura: Candidatura }) {
  return (
    <div className={`${estilos.cartao} ${estilos.cartaoFlutuante}`}>
      <strong className={estilos.cargo}>{candidatura.cargo}</strong>
      <DadosDoCartao candidatura={candidatura} />
    </div>
  );
}

function DadosDoCartao({ candidatura }: { candidatura: Candidatura }) {
  return (
    <div className={estilos.rodapeCartao}>
      <span className={estilos.avatar} aria-hidden="true">
        {inicialDe(candidatura.empresa)}
      </span>
      <span className={estilos.empresa}>{candidatura.empresa}</span>
      <time
        className={estilos.data}
        dateTime={candidatura.data_aplicacao}
        title={`Aplicada em ${formatarData(candidatura.data_aplicacao)}`}
      >
        {formatarTempoRelativo(candidatura.data_aplicacao)}
      </time>
    </div>
  );
}
