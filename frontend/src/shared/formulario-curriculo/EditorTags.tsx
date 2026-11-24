import { useDroppable } from "@dnd-kit/core";
import { SortableContext, horizontalListSortingStrategy, useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { useState, type KeyboardEvent } from "react";
import { Field } from "../ui/Field";
import { adicionarTags, idDaTag, separarTags, virgulaAbreNovaTag } from "./competencias";
import estilos from "./EditorCompetencias.module.css";

interface Props {
  tags: string[];
  aoMudar: (tags: string[]) => void;
  /** Nome do grupo de tags, usado nos rótulos acessíveis e nos anúncios (ex.: "Linguagens"). */
  nome: string;
  /** Recebe o texto de cada criação ou remoção, para o leitor de tela. */
  aoAnunciar?: (mensagem: string) => void;
  rotuloNovaTag?: string;
  ajuda?: string;
  /**
   * Habilita arrastar as tags (JOB-0045). Exige um `DndContext` acima: quem o fornece decide o que
   * fazer ao soltar. `idLista` identifica esta lista como destino e `indice` a prefixa nas tags.
   */
  arrastavel?: { idLista: string; indice: number };
}

/**
 * Tags editáveis: criam-se com Enter, vírgula ou ao sair do campo, e removem-se pelo botão da tag.
 * Componente controlado, usado nas competências por categoria (JOB-0041) e nas skills de cada
 * experiência (JOB-0045).
 */
export function EditorTags({
  tags,
  aoMudar,
  nome,
  aoAnunciar,
  rotuloNovaTag = "Nova tag",
  ajuda,
  arrastavel,
}: Props) {
  const criar = (texto: string) => {
    const novas = adicionarTags(tags, separarTags(texto));
    const criadas = novas.slice(tags.length);
    if (criadas.length === 0) return;
    aoMudar(novas);
    aoAnunciar?.(
      `${criadas.length === 1 ? `Tag ${criadas[0]} adicionada` : `${criadas.length} tags adicionadas`} em ${nome}.`,
    );
  };

  const remover = (tag: string) => {
    aoMudar(tags.filter((atual) => atual !== tag));
    aoAnunciar?.(`Tag ${tag} removida de ${nome}.`);
  };

  return (
    <>
      {arrastavel ? (
        <ListaArrastavel
          tags={tags}
          nome={nome}
          idLista={arrastavel.idLista}
          indice={arrastavel.indice}
          aoRemover={remover}
        />
      ) : (
        tags.length > 0 && (
          <ul className={estilos.tags} aria-label={`Tags de ${nome}`}>
            {tags.map((tag) => (
              <li key={tag} className={estilos.tag}>
                <span>{tag}</span>
                <BotaoRemover tag={tag} aoRemover={remover} />
              </li>
            ))}
          </ul>
        )
      )}
      <CampoNovaTag rotulo={rotuloNovaTag} ajuda={ajuda} aoCriar={criar} />
    </>
  );
}

function CampoNovaTag({
  rotulo,
  ajuda,
  aoCriar,
}: {
  rotulo: string;
  ajuda?: string;
  aoCriar: (texto: string) => void;
}) {
  const [texto, setTexto] = useState("");

  const confirmar = () => {
    if (texto.trim() !== "") aoCriar(texto);
    setTexto("");
  };

  const aoTeclar = (evento: KeyboardEvent<HTMLInputElement>) => {
    if (evento.key === "Enter" || (evento.key === "," && virgulaAbreNovaTag(texto))) {
      evento.preventDefault();
      confirmar();
    }
  };

  return (
    <Field
      rotulo={rotulo}
      ajuda={ajuda}
      placeholder="Digite e tecle Enter"
      value={texto}
      onChange={(evento) => setTexto(evento.target.value)}
      onKeyDown={aoTeclar}
      onBlur={confirmar}
    />
  );
}

function BotaoRemover({ tag, aoRemover }: { tag: string; aoRemover: (tag: string) => void }) {
  return (
    <button
      type="button"
      className={estilos.removerTag}
      aria-label={`Remover ${tag}`}
      onClick={() => aoRemover(tag)}
    >
      <span aria-hidden="true">×</span>
    </button>
  );
}

interface PropsListaArrastavel {
  tags: string[];
  nome: string;
  idLista: string;
  indice: number;
  aoRemover: (tag: string) => void;
}

/** Lista que também é destino de soltura: existe mesmo sem tags, para receber uma tag arrastada. */
function ListaArrastavel({ tags, nome, idLista, indice, aoRemover }: PropsListaArrastavel) {
  const { setNodeRef, isOver } = useDroppable({ id: idLista });
  return (
    <SortableContext
      items={tags.map((tag) => idDaTag(indice, tag))}
      strategy={horizontalListSortingStrategy}
    >
      <ul
        ref={setNodeRef}
        className={[estilos.tags, estilos.areaDeSoltura, isOver && estilos.areaSobre]
          .filter(Boolean)
          .join(" ")}
        aria-label={`Tags de ${nome}`}
      >
        {tags.map((tag) => (
          <TagArrastavel key={tag} id={idDaTag(indice, tag)} tag={tag} aoRemover={aoRemover} />
        ))}
      </ul>
    </SortableContext>
  );
}

function TagArrastavel({
  id,
  tag,
  aoRemover,
}: {
  id: string;
  tag: string;
  aoRemover: (tag: string) => void;
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    setActivatorNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id, attributes: { roleDescription: "tag arrastável" } });
  return (
    <li
      ref={setNodeRef}
      className={[estilos.tag, isDragging && estilos.tagOrigem].filter(Boolean).join(" ")}
      style={{ transform: CSS.Transform.toString(transform), transition }}
    >
      <span
        ref={setActivatorNodeRef}
        className={estilos.alca}
        aria-label={`Mover ${tag}`}
        {...attributes}
        {...listeners}
      >
        {tag}
      </span>
      <BotaoRemover tag={tag} aoRemover={aoRemover} />
    </li>
  );
}
