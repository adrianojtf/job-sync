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

const MS_POR_DIA = 24 * 60 * 60 * 1000;

const diaCivil = (data: Date) => Date.UTC(data.getFullYear(), data.getMonth(), data.getDate());

const plural = (quantidade: number, singular: string, pluralizado: string) =>
  `há ${quantidade} ${quantidade === 1 ? singular : pluralizado}`;

/** Tempo decorrido em linguagem natural ("hoje", "há 3 dias", "há 2 semanas"), contado em dias de calendário. */
export function formatarTempoRelativo(iso: string, agora: Date = new Date()): string {
  const dias = Math.max(0, Math.round((diaCivil(agora) - diaCivil(new Date(iso))) / MS_POR_DIA));
  if (dias === 0) return "hoje";
  if (dias < 7) return plural(dias, "dia", "dias");
  if (dias < 30) return plural(Math.floor(dias / 7), "semana", "semanas");
  if (dias < 365) return plural(Math.floor(dias / 30), "mês", "meses");
  return plural(Math.floor(dias / 365), "ano", "anos");
}

/** Primeira letra, em maiúscula, para avatares (ex.: empresa); "?" se o texto estiver vazio. */
export function inicialDe(texto: string): string {
  return texto.trim().charAt(0).toLocaleUpperCase("pt-BR") || "?";
}
