import type { Candidatura, CandidaturasPorStatus } from "../../api/tipos";

/** Coluna e posição (índice a partir de 0) em que o cartão ficará depois do movimento. */
export interface Destino {
  status: string;
  posicao: number;
}

/** Prefixo do id da área de soltura de cada coluna (usado quando o alvo é a coluna, não um cartão). */
export const PREFIXO_COLUNA = "coluna:";

export const idDaColuna = (status: string) => `${PREFIXO_COLUNA}${status}`;

/** Candidatura com o `id` informado, em qualquer coluna do quadro. */
export function encontrarCandidatura(
  quadro: CandidaturasPorStatus,
  id: string,
): Candidatura | undefined {
  return Object.values(colunas(quadro))
    .flat()
    .find((cartao) => cartao.id === id);
}

interface Posicao {
  status: string;
  indice: number;
}

const colunas = (quadro: CandidaturasPorStatus) => quadro.por_status ?? {};

const coluna = (quadro: CandidaturasPorStatus, status: string): Candidatura[] =>
  colunas(quadro)[status] ?? [];

function localizar(quadro: CandidaturasPorStatus, id: string): Posicao | null {
  for (const [status, cartoes] of Object.entries(colunas(quadro))) {
    const indice = cartoes.findIndex((cartao) => cartao.id === id);
    if (indice >= 0) return { status, indice };
  }
  return null;
}

/** Destino do cartão `ativoId` solto sobre `sobreId` (outro cartão ou `coluna:STATUS`); `null` se nada muda. */
export function calcularDestino(
  quadro: CandidaturasPorStatus,
  ativoId: string,
  sobreId: string,
): Destino | null {
  const origem = localizar(quadro, ativoId);
  if (!origem || ativoId === sobreId) return null;

  const destino = sobreId.startsWith(PREFIXO_COLUNA)
    ? destinoNoFimDaColuna(quadro, origem, sobreId.slice(PREFIXO_COLUNA.length))
    : destinoSobreCartao(quadro, sobreId);

  const semMudanca =
    destino && destino.status === origem.status && destino.posicao === origem.indice;
  return !destino || semMudanca ? null : destino;
}

function destinoNoFimDaColuna(
  quadro: CandidaturasPorStatus,
  origem: Posicao,
  status: string,
): Destino | null {
  if (!(status in colunas(quadro))) return null;
  const tamanho = coluna(quadro, status).length;
  return { status, posicao: status === origem.status ? tamanho - 1 : tamanho };
}

function destinoSobreCartao(quadro: CandidaturasPorStatus, sobreId: string): Destino | null {
  const alvo = localizar(quadro, sobreId);
  return alvo && { status: alvo.status, posicao: alvo.indice };
}

const numerar = (cartoes: Candidatura[]): Candidatura[] =>
  cartoes.map((cartao, posicao) => (cartao.posicao === posicao ? cartao : { ...cartao, posicao }));

/** Novo quadro com o cartão no destino e as posições das colunas afetadas renumeradas. */
export function aplicarMovimento(
  quadro: CandidaturasPorStatus,
  ativoId: string,
  destino: Destino,
): CandidaturasPorStatus {
  const origem = localizar(quadro, ativoId);
  if (!origem) return quadro;

  const movido: Candidatura = {
    ...coluna(quadro, origem.status)[origem.indice]!,
    status: destino.status,
  };
  const semMovido = (status: string) =>
    coluna(quadro, status).filter((cartao) => cartao.id !== ativoId);

  const alvo = semMovido(destino.status);
  const posicao = Math.max(0, Math.min(destino.posicao, alvo.length));
  alvo.splice(posicao, 0, movido);

  return {
    ...quadro,
    por_status: {
      ...colunas(quadro),
      [origem.status]: numerar(semMovido(origem.status)),
      [destino.status]: numerar(alvo),
    },
  };
}
