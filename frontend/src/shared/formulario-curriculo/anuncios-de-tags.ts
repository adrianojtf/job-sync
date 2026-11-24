import type { Announcements, ScreenReaderInstructions } from "@dnd-kit/core";
import type { CategoriaFormulario } from "./campos-curriculo";
import { lerIdDoArrasto } from "./competencias";

export const INSTRUCOES_DE_TAGS: ScreenReaderInstructions = {
  draggable:
    "Para mover uma tag, pressione Espaço para pegá-la, use as setas para escolher a posição ou a " +
    "categoria, pressione Espaço para soltar ou Esc para cancelar.",
};

const nomeDa = (categorias: CategoriaFormulario[], indice: number) =>
  categorias[indice]?.nome.trim() || `Categoria ${indice + 1}`;

function descrever(categorias: CategoriaFormulario[], id: string | number | undefined) {
  const alvo = id === undefined ? null : lerIdDoArrasto(String(id));
  if (alvo === null) return null;
  return { alvo, categoria: nomeDa(categorias, alvo.categoria) };
}

/**
 * Anúncios em português para leitores de tela durante o arrasto de uma tag. Recebe uma função para
 * ler as categorias atuais, porque elas mudam enquanto o editor é usado.
 */
export function anunciosDeTags(lerCategorias: () => CategoriaFormulario[]): Announcements {
  const tagDe = (id: string | number) => {
    const alvo = lerIdDoArrasto(String(id));
    return alvo?.tipo === "tag" ? alvo.tag : "selecionada";
  };
  const posicao = (id: string | number) => {
    const categorias = lerCategorias();
    const alvo = descrever(categorias, id);
    if (alvo === null) return null;
    return alvo.categoria;
  };

  return {
    onDragStart({ active }) {
      const origem = posicao(active.id);
      return origem === null
        ? `Tag ${tagDe(active.id)} pega.`
        : `Tag ${tagDe(active.id)} pega em ${origem}.`;
    },
    onDragOver({ active, over }) {
      if (!over) return `Tag ${tagDe(active.id)} fora das categorias.`;
      const destino = posicao(over.id);
      return destino === null
        ? `Tag ${tagDe(active.id)} fora das categorias.`
        : `Tag ${tagDe(active.id)} sobre ${destino}.`;
    },
    onDragEnd({ active, over }) {
      if (!over) return `Tag ${tagDe(active.id)} solta fora das categorias. Nada foi alterado.`;
      const destino = posicao(over.id);
      return destino === null
        ? `Tag ${tagDe(active.id)} solta.`
        : `Tag ${tagDe(active.id)} solta em ${destino}.`;
    },
    onDragCancel({ active }) {
      return `Movimento da tag ${tagDe(active.id)} cancelado. Nada foi alterado.`;
    },
  };
}
