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
import { useContext, useState } from "react";
import { Panel } from "../ui/Panel";
import { ToastContext } from "../ui/toast-context";
import { anunciosDeTags, INSTRUCOES_DE_TAGS } from "./anuncios-de-tags";
import { idDaCategoria, soltarTag } from "./competencias";
import { EditorTags } from "./EditorTags";
import type { HistoricoDoFormulario } from "./use-historico-do-formulario";

interface Props {
  valor: string[];
  aoMudar: (tags: string[]) => void;
  titulo?: string;
  subtitulo?: string;
  /** Instantâneo para o "Desfazer" da remoção e da reordenação. */
  historico?: HistoricoDoFormulario;
}

const NOME_DA_LISTA = "Tecnologias";

/**
 * Tecnologias gerais do perfil como tags (JOB-0046): criam-se com Enter ou vírgula, excluem-se
 * pelo botão da tag e reordenam-se por arrastar (mouse, toque ou teclado). A ordem é a do currículo.
 * Reaproveita a regra de soltar tags das competências, tratando a lista como uma só categoria.
 */
export function ListaDeTecnologias({
  valor,
  aoMudar,
  titulo = "Tecnologias e ferramentas",
  subtitulo = "Arraste as tags para reordenar. As skills das experiências que faltarem aqui entram no fim ao salvar.",
  historico,
}: Props) {
  const toast = useContext(ToastContext);
  const [anuncio, setAnuncio] = useState("");
  const comDesfazer = historico
    ? { acao: { rotulo: "Desfazer", aoClicar: historico.desfazer } }
    : undefined;

  const sensores = useSensors(
    useSensor(MouseSensor, { activationConstraint: { distance: 5 } }),
    useSensor(TouchSensor, { activationConstraint: { delay: 200, tolerance: 8 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const mudar = (tags: string[]) => {
    if (tags.length < valor.length) {
      historico?.registrar();
      aoMudar(tags);
      toast?.notificar("Tecnologia removida.", "info", comDesfazer);
      return;
    }
    aoMudar(tags);
  };

  const soltar = ({ active, over }: DragEndEvent) => {
    const movimento = soltarTag(
      [{ nome: NOME_DA_LISTA, tags: valor }],
      String(active.id),
      over ? String(over.id) : null,
    );
    if (movimento === null) return;
    aoMudar(movimento.categorias[0]!.tags);
    setAnuncio(`Tecnologia ${movimento.tag} reordenada.`);
    toast?.notificar("Ordem alterada.", "info", comDesfazer);
  };

  return (
    <Panel titulo={titulo} subtitulo={subtitulo}>
      <DndContext
        sensors={sensores}
        collisionDetection={closestCenter}
        onDragStart={() => historico?.registrar()}
        onDragEnd={soltar}
        accessibility={{
          announcements: anunciosDeTags(() => [{ nome: NOME_DA_LISTA, tags: valor }]),
          screenReaderInstructions: INSTRUCOES_DE_TAGS,
        }}
      >
        <EditorTags
          tags={valor}
          aoMudar={mudar}
          nome={NOME_DA_LISTA.toLowerCase()}
          aoAnunciar={setAnuncio}
          rotuloNovaTag="Nova tecnologia"
          ajuda="Digite e tecle Enter ou vírgula."
          arrastavel={{ idLista: idDaCategoria(0), indice: 0 }}
        />
      </DndContext>
      <p aria-live="polite" className="sr-only">
        {anuncio}
      </p>
    </Panel>
  );
}
