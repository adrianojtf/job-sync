import { useCallback, useEffect, useState } from "react";

/** Há algo guardado para essa chave (mesmo uma lista vazia)? Storage bloqueado conta como não. */
function existeGuardado(chaveDeArmazenamento: string | undefined): boolean {
  if (!chaveDeArmazenamento) return false;
  try {
    return window.localStorage.getItem(chaveDeArmazenamento) !== null;
  } catch {
    return false;
  }
}

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
  /** Quando nada foi guardado ainda, começa com todos abertos (ex.: perfil novo, ainda vazio). */
  abertosPorPadrao?: boolean;
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
export function useCartoesAbertos({
  chaveDeArmazenamento,
  ids,
  chavesDosItens,
  abertosPorPadrao = false,
}: Entrada) {
  const [guardado, setGuardado] = useState<Set<string>>(() =>
    abertosPorPadrao && !existeGuardado(chaveDeArmazenamento)
      ? new Set(ids)
      : abrirGuardados(chaveDeArmazenamento, ids, chavesDosItens),
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

  // As chaves guardadas acompanham o conteúdo atual dos itens abertos, inclusive títulos editados.
  const assinatura = JSON.stringify(
    ids
      .map((id, indice) => (abertos.has(id) ? (chavesDosItens[indice] ?? "") : ""))
      .filter(Boolean),
  );
  useEffect(() => {
    if (!existeGuardado(chaveDeArmazenamento) && assinatura === "[]") return;
    gravarChavesAbertas(chaveDeArmazenamento, JSON.parse(assinatura) as string[]);
  }, [chaveDeArmazenamento, assinatura]);

  const definir = (proximos: Set<string>) => setGuardado(proximos);

  const alternar = (id: string) => {
    const proximos = new Set(abertos);
    if (!proximos.delete(id)) proximos.add(id);
    setGuardado(proximos);
  };

  const abrir = (id: string) => setGuardado(new Set(abertos).add(id));

  /** Abre vários de uma vez; estável, para ser usada em callbacks de fora do React (ex.: erros do formulário). */
  const abrirVarios = useCallback(
    (novos: string[]) => setGuardado((anteriores) => new Set([...anteriores, ...novos])),
    [],
  );

  return { abertos, alternar, abrir, abrirVarios, definir };
}
