import type { Announcements, ScreenReaderInstructions } from "@dnd-kit/core";

export const INSTRUCOES_DE_LISTA: ScreenReaderInstructions = {
  draggable:
    "Para mover um item, pressione Espaço para pegá-lo, use as setas para escolher a posição, " +
    "pressione Espaço para soltar ou Esc para cancelar.",
};

export interface ItemAnunciavel {
  id: string;
  titulo: string;
}

/**
 * Anúncios em português para leitores de tela durante o arrasto de um item da lista. Recebe uma
 * função para ler os itens atuais, porque a lista muda enquanto o formulário é usado.
 */
export function anunciosDeLista(lerItens: () => ItemAnunciavel[]): Announcements {
  const posicao = (id: string | number) => {
    const itens = lerItens();
    const indice = itens.findIndex((item) => item.id === String(id));
    return { indice, total: itens.length, titulo: itens[indice]?.titulo || "Item" };
  };

  return {
    onDragStart({ active }) {
      const { indice, total, titulo } = posicao(active.id);
      return `${titulo} pego. Posição ${indice + 1} de ${total}.`;
    },
    onDragOver({ active, over }) {
      const { titulo } = posicao(active.id);
      if (!over) return `${titulo} fora da lista.`;
      const { indice, total } = posicao(over.id);
      return `${titulo} sobre a posição ${indice + 1} de ${total}.`;
    },
    onDragEnd({ active, over }) {
      const { titulo } = posicao(active.id);
      if (!over) return `${titulo} solto fora da lista. Nada foi alterado.`;
      const { indice, total } = posicao(over.id);
      return `${titulo} solto na posição ${indice + 1} de ${total}.`;
    },
    onDragCancel({ active }) {
      return `Movimento de ${posicao(active.id).titulo} cancelado. Nada foi alterado.`;
    },
  };
}
