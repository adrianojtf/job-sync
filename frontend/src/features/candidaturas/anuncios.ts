import type { Announcements, ScreenReaderInstructions } from "@dnd-kit/core";
import type { CandidaturasPorStatus } from "../../api/tipos";
import { calcularDestino, encontrarCandidatura } from "./movimento";
import { rotuloStatus } from "./status";

export const DESCRICAO_CARTAO = "cartão arrastável";

export const INSTRUCOES_LEITOR_DE_TELA: ScreenReaderInstructions = {
  draggable:
    "Para mover uma candidatura, pressione Espaço para pegá-la, use as setas para escolher a posição ou a coluna, " +
    "pressione Espaço para soltar ou Esc para cancelar.",
};

interface Alvo {
  id: string | number;
}

/**
 * Anúncios em português para leitores de tela durante o arrasto (RF18).
 * Recebe uma função para ler o quadro atual, porque ele muda enquanto o board é usado.
 */
export function criarAnuncios(lerQuadro: () => CandidaturasPorStatus | undefined): Announcements {
  const cargo = (id: string) => {
    const quadro = lerQuadro();
    return (quadro && encontrarCandidatura(quadro, id)?.cargo) ?? "selecionada";
  };

  const descreverPosicao = (ativo: string, sobre: string) => {
    const quadro = lerQuadro();
    const destino = quadro && calcularDestino(quadro, ativo, sobre);
    if (!quadro || !destino) return null;
    const origem = encontrarCandidatura(quadro, ativo)?.status;
    const tamanhoAtual = quadro.por_status?.[destino.status]?.length ?? 0;
    const total = origem === destino.status ? tamanhoAtual : tamanhoAtual + 1;
    return `${rotuloStatus(destino.status)}, posição ${destino.posicao + 1} de ${total}`;
  };

  return {
    onDragStart({ active }) {
      const quadro = lerQuadro();
      const atual = quadro && encontrarCandidatura(quadro, String(active.id));
      if (!quadro || !atual) return `Candidatura ${cargo(String(active.id))} pega.`;
      const coluna = quadro.por_status?.[atual.status] ?? [];
      const indice = coluna.findIndex((item) => item.id === atual.id);
      return `Candidatura ${atual.cargo} pega. Posição ${indice + 1} de ${coluna.length} em ${rotuloStatus(atual.status)}.`;
    },
    onDragOver({ active, over }: { active: Alvo; over: Alvo | null }) {
      const nome = cargo(String(active.id));
      if (!over) return `Candidatura ${nome} fora das colunas.`;
      const posicao = descreverPosicao(String(active.id), String(over.id));
      return posicao
        ? `Candidatura ${nome} sobre ${posicao}.`
        : `Candidatura ${nome} na posição original.`;
    },
    onDragEnd({ active, over }: { active: Alvo; over: Alvo | null }) {
      const nome = cargo(String(active.id));
      if (!over) return `Candidatura ${nome} solta fora das colunas. Nada foi alterado.`;
      const posicao = descreverPosicao(String(active.id), String(over.id));
      return posicao
        ? `Candidatura ${nome} solta em ${posicao}.`
        : `Candidatura ${nome} solta na posição original.`;
    },
    onDragCancel({ active }) {
      return `Movimento cancelado. Candidatura ${cargo(String(active.id))} voltou à posição original.`;
    },
  };
}
