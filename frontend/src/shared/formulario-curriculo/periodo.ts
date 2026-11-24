/**
 * Período de uma experiência ou formação, em texto como o usuário digita. Espelha
 * `shared_kernel/domain/periodo.py` do backend; os dois lados leem a mesma tabela de casos
 * (`periodo.casos.json`).
 *
 * Formato: `início - fim`, em que cada lado é `aaaa`, `mmm aaaa` (mês abreviado ou por extenso, em
 * português ou inglês) ou `mm/aaaa`, e o fim também pode ser `Atual`, `Presente`, `Present` ou
 * `Current`. O separador é hífen ou travessão, com ou sem espaços. Uma data só vale como início e
 * fim iguais. O início não pode ser depois do fim.
 */

export const ANO_MINIMO = 1900;
export const ANO_MAXIMO = 2100;
export const MENSAGEM_DE_FORMATO = "Use o formato Mar 2024 - Atual ou 2020 - 2022.";
const MENSAGEM_DE_ANO = "Use um ano com quatro dígitos, como 2023.";

/** Ano e, quando informado, o mês (1 a 12). */
export type DataDoPeriodo = [ano: number, mes: number | null];

export interface Periodo {
  inicio: DataDoPeriodo;
  /** `null` quando o período segue em andamento. */
  fim: DataDoPeriodo | null;
}

const MESES: Record<string, number> = {
  jan: 1,
  fev: 2,
  feb: 2,
  mar: 3,
  abr: 4,
  apr: 4,
  mai: 5,
  may: 5,
  jun: 6,
  jul: 7,
  ago: 8,
  aug: 8,
  set: 9,
  sep: 9,
  out: 10,
  oct: 10,
  nov: 11,
  dez: 12,
  dec: 12,
};
const ATUAL = new Set(["atual", "presente", "present", "current"]);
const SEPARADOR = /\s*[-–—]\s*/;
const SO_ANO = /^(\d{4})$/;
const MES_NUMERICO = /^(\d{2})\/(\d{4})$/;
const MES_POR_NOME = /^(\p{L}{3,})\.?\s+(\d{4})$/u;

class FormatoInvalido extends Error {}

/** Minúsculas, sem acento e sem pontuação, com espaços simples (como `normalizar_texto` do backend). */
function normalizar(texto: string): string {
  return texto
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function lerAno(texto: string): number {
  const ano = Number(texto);
  if (ano < ANO_MINIMO || ano > ANO_MAXIMO) {
    throw new FormatoInvalido(
      `O ano deve estar entre ${ANO_MINIMO} e ${ANO_MAXIMO}. ${MENSAGEM_DE_FORMATO}`,
    );
  }
  return ano;
}

function lerData(texto: string): DataDoPeriodo {
  const limpo = texto.trim();
  let m = SO_ANO.exec(limpo);
  if (m) return [lerAno(m[1]!), null];
  m = MES_NUMERICO.exec(limpo);
  if (m) {
    const mes = Number(m[1]);
    if (mes < 1 || mes > 12) throw new FormatoInvalido(MENSAGEM_DE_FORMATO);
    return [lerAno(m[2]!), mes];
  }
  m = MES_POR_NOME.exec(limpo);
  if (m) {
    const mes = MESES[normalizar(m[1]!).slice(0, 3)];
    if (mes === undefined) throw new FormatoInvalido(MENSAGEM_DE_FORMATO);
    return [lerAno(m[2]!), mes];
  }
  throw new FormatoInvalido(MENSAGEM_DE_FORMATO);
}

const comoNumero = ([ano, mes]: DataDoPeriodo) => ano * 13 + (mes ?? 0);

function lerOuFalhar(texto: string): Periodo {
  const partes = texto.trim().split(SEPARADOR);
  if (partes.length === 1) {
    const data = lerData(partes[0]!);
    return { inicio: data, fim: data };
  }
  if (partes.length !== 2 || partes.some((parte) => parte === "")) {
    throw new FormatoInvalido(MENSAGEM_DE_FORMATO);
  }
  const inicio = lerData(partes[0]!);
  if (ATUAL.has(normalizar(partes[1]!))) return { inicio, fim: null };
  const fim = lerData(partes[1]!);
  if (comoNumero(inicio) > comoNumero(fim)) {
    throw new FormatoInvalido(`O início não pode ser depois do fim. ${MENSAGEM_DE_FORMATO}`);
  }
  return { inicio, fim };
}

/** Lê o período; devolve `null` se o texto não seguir o formato. */
export function lerPeriodo(texto: string): Periodo | null {
  try {
    return lerOuFalhar(texto);
  } catch (erro) {
    if (erro instanceof FormatoInvalido) return null;
    throw erro;
  }
}

/** Mensagem de erro de um período preenchido; `undefined` se vazio ou válido. */
export function validarPeriodo(texto: string): string | undefined {
  if (texto.trim() === "") return undefined;
  try {
    lerOuFalhar(texto);
    return undefined;
  } catch (erro) {
    if (erro instanceof FormatoInvalido) return erro.message;
    throw erro;
  }
}

/** Ano de quatro dígitos de uma certificação; `undefined` se vazio ou válido. */
export function validarAno(texto: string): string | undefined {
  const limpo = texto.trim();
  if (limpo === "") return undefined;
  if (!SO_ANO.test(limpo)) return MENSAGEM_DE_ANO;
  try {
    lerAno(limpo);
    return undefined;
  } catch (erro) {
    if (erro instanceof FormatoInvalido) return erro.message;
    throw erro;
  }
}

/** Chave de ordenação: período em andamento antes do encerrado, e o início mais recente antes. */
export type ChaveDeOrdem = { atual: boolean; inicio: number } | null;

export function chaveDePeriodo(texto: string): ChaveDeOrdem {
  const periodo = lerPeriodo(texto);
  if (periodo === null || texto.trim() === "") return null;
  return { atual: periodo.fim === null, inicio: comoNumero(periodo.inicio) };
}

export function chaveDeAno(texto: string): ChaveDeOrdem {
  return validarAno(texto) === undefined && texto.trim() !== ""
    ? { atual: false, inicio: Number(texto.trim()) }
    : null;
}

/**
 * Ordena do mais recente para o mais antigo. Período em andamento vem primeiro; vazio ou inválido
 * fica no fim, mantendo a ordem relativa; o desempate também mantém a ordem original.
 */
export function ordenarPorChave<T>(itens: readonly T[], chave: (item: T) => ChaveDeOrdem): T[] {
  const comChave = itens.map((item) => ({ item, chave: chave(item) }));
  return comChave
    .sort((a, b) => {
      if (a.chave === null || b.chave === null) {
        return a.chave === b.chave ? 0 : a.chave === null ? 1 : -1;
      }
      if (a.chave.atual !== b.chave.atual) return a.chave.atual ? -1 : 1;
      return b.chave.inicio - a.chave.inicio;
    })
    .map(({ item }) => item);
}
