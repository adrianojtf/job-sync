const FORMATO_DATA = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
});

/** Formata datas ISO da API como dd/mm/aaaa. */
export function formatarData(iso: string): string {
  return FORMATO_DATA.format(new Date(iso));
}

/** Primeira linha não vazia de um texto, encurtada para listas e seletores. */
export function primeiraLinha(texto: string, maximo = 80): string {
  const linha =
    texto
      .split("\n")
      .map((trecho) => trecho.trim())
      .find(Boolean) ?? "";
  return linha.length > maximo ? `${linha.slice(0, maximo - 1)}…` : linha;
}

/** Trecho seguro para nomes de arquivo: minúsculas, sem acentos, palavras separadas por hífen. */
export function paraSlug(texto: string): string {
  return texto
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

const FORMATO_DATA_HORA = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

/** Formata datas ISO da API como dd/mm/aaaa hh:mm. */
export function formatarDataHora(iso: string): string {
  return FORMATO_DATA_HORA.format(new Date(iso)).replace(",", "");
}

/** Domínio de uma URL sem "www." (ex.: linkedin.com); vazio se não houver URL válida. */
export function dominioDaUrl(url: string | null | undefined): string {
  if (!url) return "";
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}
