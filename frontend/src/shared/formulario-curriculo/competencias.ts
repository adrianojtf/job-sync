import type { CategoriaFormulario } from "./campos-curriculo";

/** Categoria que recebe as tecnologias escritas sem rótulo. Espelha o backend. */
export const CATEGORIA_PADRAO = "Tecnologias";
const MARCADORES = /^[-•*\s]+/;

/** Separa por vírgula, ignorando as que estão dentro de parênteses. Espelha o backend. */
export function separarTags(texto: string): string[] {
  const tags: string[] = [];
  let atual = "";
  let profundidade = 0;
  for (const caractere of texto) {
    if (caractere === "(") profundidade += 1;
    else if (caractere === ")" && profundidade > 0) profundidade -= 1;
    if (caractere === "," && profundidade === 0) {
      tags.push(atual);
      atual = "";
    } else {
      atual += caractere;
    }
  }
  tags.push(atual);
  return tags.map((tag) => tag.trim()).filter((tag) => tag !== "");
}

/** Uma vírgula só abre outra tag quando não há parêntese aberto no texto digitado. */
export function virgulaAbreNovaTag(texto: string): boolean {
  let profundidade = 0;
  for (const caractere of texto) {
    if (caractere === "(") profundidade += 1;
    else if (caractere === ")" && profundidade > 0) profundidade -= 1;
  }
  return profundidade === 0;
}

/** Acrescenta as tags novas ao fim, sem repetir as que já existem (sem diferenciar a caixa). */
export function adicionarTags(existentes: string[], novas: string[]): string[] {
  const vistas = new Set(existentes.map((tag) => tag.toLowerCase()));
  const resultado = [...existentes];
  for (const tag of novas) {
    const chave = tag.toLowerCase();
    if (!vistas.has(chave)) {
      vistas.add(chave);
      resultado.push(tag);
    }
  }
  return resultado;
}

/** Lê linhas "Rótulo: a, b"; linhas sem rótulo formam a categoria padrão. Espelha o backend. */
export function categoriasDeTexto(conteudo: string): CategoriaFormulario[] {
  const categorias: CategoriaFormulario[] = [];
  let semRotulo: string[] = [];
  for (const linha of conteudo.split("\n")) {
    const texto = linha.trim().replace(MARCADORES, "").trim();
    if (texto === "") continue;
    const posicao = texto.indexOf(":");
    const rotulo = posicao >= 0 ? texto.slice(0, posicao).trim() : "";
    if (rotulo !== "") {
      const tags = adicionarTags([], separarTags(texto.slice(posicao + 1)));
      if (tags.length > 0) categorias.push({ nome: rotulo, tags });
    } else {
      semRotulo = [...semRotulo, ...separarTags(texto)];
    }
  }
  const padrao = adicionarTags([], semRotulo);
  if (padrao.length > 0) categorias.push({ nome: CATEGORIA_PADRAO, tags: padrao });
  return categorias;
}

/** Uma categoria por linha; descarta as sem nome ou sem tags. Espelha o backend. */
export function categoriasParaTexto(categorias: CategoriaFormulario[]): string {
  return categorias
    .filter((categoria) => categoria.nome.trim() !== "" && categoria.tags.length > 0)
    .map((categoria) => `${categoria.nome.trim()}: ${categoria.tags.join(", ")}`)
    .join("\n");
}

/** Identificador do contêiner (a lista de tags) de uma categoria no arrastar e soltar. */
export const idDaCategoria = (categoria: number) => `categoria:${categoria}`;

/** Identificador de uma tag no arrastar e soltar; o da categoria evita colisão entre categorias. */
export const idDaTag = (categoria: number, tag: string) => `tag:${categoria}:${tag}`;

export type AlvoDoArrasto =
  | { tipo: "categoria"; categoria: number }
  | { tipo: "tag"; categoria: number; tag: string };

/** Lê um identificador gerado por `idDaCategoria` ou `idDaTag`; devolve null para qualquer outro. */
export function lerIdDoArrasto(id: string): AlvoDoArrasto | null {
  const categoria = /^categoria:(\d+)$/.exec(id);
  if (categoria) return { tipo: "categoria", categoria: Number(categoria[1]) };
  const tag = /^tag:(\d+):([\s\S]+)$/.exec(id);
  if (tag) return { tipo: "tag", categoria: Number(tag[1]), tag: tag[2]! };
  return null;
}

export interface ResultadoDoMovimento {
  categorias: CategoriaFormulario[];
  /** De qual categoria para qual a tag foi, para o anúncio ao leitor de tela. */
  de: number;
  para: number;
  tag: string;
}

/**
 * Soltar uma tag sobre outra tag (entra na posição dela) ou sobre uma categoria (entra no fim).
 * Reordena dentro da categoria e move entre categorias sem duplicar a tag no destino (sem
 * diferenciar a caixa): se ela já existe lá, só sai da origem. Devolve null quando nada muda.
 */
export function soltarTag(
  categorias: CategoriaFormulario[],
  idAtivo: string,
  idSobre: string | null,
): ResultadoDoMovimento | null {
  const ativo = lerIdDoArrasto(idAtivo);
  const sobre = idSobre === null ? null : lerIdDoArrasto(idSobre);
  if (ativo?.tipo !== "tag" || sobre === null) return null;
  const origem = categorias[ativo.categoria];
  const destino = categorias[sobre.categoria];
  if (!origem || !destino) return null;
  const posicaoOrigem = origem.tags.indexOf(ativo.tag);
  if (posicaoOrigem < 0) return null;

  if (ativo.categoria === sobre.categoria) {
    const posicaoDestino =
      sobre.tipo === "tag" ? origem.tags.indexOf(sobre.tag) : origem.tags.length - 1;
    if (posicaoDestino < 0 || posicaoDestino === posicaoOrigem) return null;
    const tags = [...origem.tags];
    tags.splice(posicaoOrigem, 1);
    tags.splice(posicaoDestino, 0, ativo.tag);
    return resultado(categorias, ativo.categoria, { ...origem, tags }, ativo);
  }

  const semAOrigem = origem.tags.filter((tag) => tag !== ativo.tag);
  const jaExisteNoDestino = destino.tags.some(
    (tag) => tag.toLowerCase() === ativo.tag.toLowerCase(),
  );
  const tagsDoDestino = [...destino.tags];
  if (!jaExisteNoDestino) {
    const posicao = sobre.tipo === "tag" ? tagsDoDestino.indexOf(sobre.tag) : tagsDoDestino.length;
    tagsDoDestino.splice(posicao < 0 ? tagsDoDestino.length : posicao, 0, ativo.tag);
  }
  const novas = categorias.map((categoria, indice) => {
    if (indice === ativo.categoria) return { ...categoria, tags: semAOrigem };
    if (indice === sobre.categoria) return { ...categoria, tags: tagsDoDestino };
    return categoria;
  });
  return { categorias: novas, de: ativo.categoria, para: sobre.categoria, tag: ativo.tag };
}

function resultado(
  categorias: CategoriaFormulario[],
  indice: number,
  nova: CategoriaFormulario,
  ativo: { categoria: number; tag: string },
): ResultadoDoMovimento {
  return {
    categorias: categorias.map((categoria, posicao) => (posicao === indice ? nova : categoria)),
    de: ativo.categoria,
    para: ativo.categoria,
    tag: ativo.tag,
  };
}
