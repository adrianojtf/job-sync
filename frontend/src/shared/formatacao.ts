const FORMATO_DATA = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
});

/** Formata datas ISO da API como dd/mm/aaaa. */
export function formatarData(iso: string): string {
  return FORMATO_DATA.format(new Date(iso));
}
