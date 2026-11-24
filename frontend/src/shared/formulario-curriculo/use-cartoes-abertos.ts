import { useState } from "react";

/** Lê as chaves guardadas; storage ausente, bloqueado ou com texto inválido vira lista vazia. */
export function lerChavesAbertas(chaveDeArmazenamento: string | undefined): string[] {
  if (!chaveDeArmazenamento) return [];
  try {
    const guardado = JSON.parse(
      window.localStorage.getItem(chaveDeArmazenamento) ?? "[]",
    ) as unknown;
    return Array.isArray(guardado)
      ? guardado.filter((chave): chave is string => typeof chave === "string")
      : [];
  } catch {
    return [];
  }
}

function gravarChavesAbertas(chaveDeArmazenamento: string | undefined, chaves: string[]): void {
  if (!chaveDeArmazenamento) return;
  try {
    window.localStorage.setItem(chaveDeArmazenamento, JSON.stringify(chaves));
  } catch {
    // Sem storage (modo privado, bloqueado ou cheio) a tela funciona igual, só não lembra.
  }
}

interface Entrada {
  /** Chave do `localStorage`; sem ela, nada é lembrado. */
  chaveDeArmazenamento?: string;
  /** Identificadores atuais dos itens (os `id` do `useFieldArray`), na ordem da lista. */
  ids: string[];
  /** Chave estável de cada item, pelo conteúdo (ex.: `empresa|cargo|período`); vazia = não guardar. */
  chavesDosItens: string[];
}

function abrirGuardados(
  chaveDeArmazenamento: string | undefined,
  ids: string[],
  chaves: string[],
): Set<string> {
  const guardadas = new Set(lerChavesAbertas(chaveDeArmazenamento));
  return new Set(ids.filter((_, indice) => guardadas.has(chaves[indice] ?? "")));
}

/**
 * Cartões abertos de uma lista (JOB-0046). Em memória o estado é por `id` do item, então editar o
 * título não fecha o cartão. No `localStorage` ficam as chaves por conteúdo: ao montar, e quando o
 * formulário é reiniciado e todos os `id` mudam, abrem-se os itens cuja chave foi guardada. Ao
 * remover um item, os demais cartões abertos continuam abertos.
 */
export function useCartoesAbertos({ chaveDeArmazenamento, ids, chavesDosItens }: Entrada) {
  const [guardado, setGuardado] = useState<Set<string>>(() =>
    abrirGuardados(chaveDeArmazenamento, ids, chavesDosItens),
  );

  const presentes = new Set(ids);
  const obsoletos = [...guardado].filter((id) => !presentes.has(id));
  let abertos = guardado;
  if (obsoletos.length > 0) {
    const algumPresente = obsoletos.length < guardado.size;
    abertos = algumPresente
      ? new Set([...guardado].filter((id) => presentes.has(id)))
      : abrirGuardados(chaveDeArmazenamento, ids, chavesDosItens);
  }

  const definir = (proximos: Set<string>) => {
    setGuardado(proximos);
    const chavesAbertas = ids
      .map((id, indice) => (proximos.has(id) ? (chavesDosItens[indice] ?? "") : ""))
      .filter((chave) => chave !== "");
    gravarChavesAbertas(chaveDeArmazenamento, chavesAbertas);
  };

  const alternar = (id: string) => {
    const proximos = new Set(abertos);
    if (!proximos.delete(id)) proximos.add(id);
    definir(proximos);
  };

  const abrir = (id: string) => definir(new Set(abertos).add(id));

  return { abertos, alternar, abrir, definir };
}
