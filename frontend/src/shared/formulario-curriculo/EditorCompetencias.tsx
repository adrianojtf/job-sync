import {
  DndContext,
  KeyboardSensor,
  MouseSensor,
  TouchSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import { sortableKeyboardCoordinates } from "@dnd-kit/sortable";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { Button } from "../ui/Button";
import { Field } from "../ui/Field";
import { Panel } from "../ui/Panel";
import { CATEGORIA_VAZIA, type CategoriaFormulario } from "./campos-curriculo";
import { anunciosDeTags, INSTRUCOES_DE_TAGS } from "./anuncios-de-tags";
import { idDaCategoria, soltarTag } from "./competencias";
import { EditorTags } from "./EditorTags";
import estilos from "./FormularioCurriculo.module.css";

interface Props {
  valor: CategoriaFormulario[];
  aoMudar: (valor: CategoriaFormulario[]) => void;
  titulo?: string;
  /** Conteúdo extra no fim do painel (ex.: sugestão de IA). */
  complemento?: ReactNode;
}

/**
 * Competências do currículo por categoria e tag (JOB-0041): cada categoria tem um nome editável
 * e tags que se criam com Enter, vírgula ou ao sair do campo, e se removem pelo botão da tag.
 * Componente controlado: quem usa guarda o valor (no formulário da revisão, via Controller).
 */
export function EditorCompetencias({
  valor,
  aoMudar,
  titulo = "Competências",
  complemento,
}: Props) {
  const [anuncio, setAnuncio] = useState("");
  const indiceParaFocar = useRef<number | null>(null);
  const camposDeNome = useRef<(HTMLInputElement | null)[]>([]);

  const quantidade = valor.length;
  useEffect(() => {
    if (indiceParaFocar.current === null) return;
    camposDeNome.current[indiceParaFocar.current]?.focus();
    indiceParaFocar.current = null;
  }, [quantidade]);

  const sensores = useSensors(
    useSensor(MouseSensor, { activationConstraint: { distance: 5 } }),
    useSensor(TouchSensor, { activationConstraint: { delay: 200, tolerance: 8 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const soltar = ({ active, over }: DragEndEvent) => {
    const movimento = soltarTag(valor, String(active.id), over ? String(over.id) : null);
    if (movimento === null) return;
    aoMudar(movimento.categorias);
    const origem = valor[movimento.de];
    const destino = valor[movimento.para];
    if (origem && destino) {
      setAnuncio(
        movimento.de === movimento.para
          ? `Tag ${movimento.tag} reordenada em ${nomeDe(destino, movimento.para)}.`
          : `Tag ${movimento.tag} movida de ${nomeDe(origem, movimento.de)} para ${nomeDe(destino, movimento.para)}.`,
      );
    }
  };

  const alterar = (indice: number, categoria: CategoriaFormulario) =>
    aoMudar(valor.map((atual, posicao) => (posicao === indice ? categoria : atual)));

  const adicionarCategoria = () => {
    aoMudar([...valor, { ...CATEGORIA_VAZIA, tags: [] }]);
    indiceParaFocar.current = valor.length;
  };

  const excluirCategoria = (indice: number) => {
    const categoria = valor[indice];
    if (!categoria) return;
    setAnuncio(`Categoria ${nomeDe(categoria, indice)} excluída.`);
    aoMudar(valor.filter((_, posicao) => posicao !== indice));
  };

  return (
    <Panel
      titulo={titulo}
      subtitulo="Agrupe as competências por categoria. Digite uma tag e tecle Enter ou vírgula; arraste uma tag para reordená-la ou movê-la para outra categoria."
      acoes={
        <Button variante="text" onClick={adicionarCategoria}>
          Adicionar categoria
        </Button>
      }
    >
      {valor.length === 0 && <p className={estilos.vazio}>Nenhuma categoria adicionada.</p>}
      <DndContext
        sensors={sensores}
        collisionDetection={closestCenter}
        onDragEnd={soltar}
        accessibility={{
          announcements: anunciosDeTags(() => valor),
          screenReaderInstructions: INSTRUCOES_DE_TAGS,
        }}
      >
        {valor.map((categoria, indice) => (
          <fieldset key={indice} className={estilos.item}>
            <legend className={estilos.legenda}>{nomeDe(categoria, indice)}</legend>
            <Field
              ref={(elemento) => {
                camposDeNome.current[indice] = elemento as HTMLInputElement | null;
              }}
              rotulo="Nome da categoria"
              value={categoria.nome}
              onChange={(evento) => alterar(indice, { ...categoria, nome: evento.target.value })}
            />
            <EditorTags
              tags={categoria.tags}
              aoMudar={(tags) => alterar(indice, { ...categoria, tags })}
              nome={nomeDe(categoria, indice)}
              aoAnunciar={setAnuncio}
              arrastavel={{ idLista: idDaCategoria(indice), indice }}
            />
            <div className={estilos.acoesItem}>
              <Button
                aria-label={`Excluir categoria ${nomeDe(categoria, indice)}`}
                onClick={() => excluirCategoria(indice)}
              >
                Excluir categoria
              </Button>
            </div>
          </fieldset>
        ))}
      </DndContext>
      {complemento}
      <p role="status" className="sr-only">
        {anuncio}
      </p>
    </Panel>
  );
}

function nomeDe(categoria: CategoriaFormulario, indice: number): string {
  return categoria.nome.trim() || `Categoria ${indice + 1}`;
}
