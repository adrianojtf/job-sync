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
