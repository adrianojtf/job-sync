import type { DadosVaga } from "../../api/tipos";

/** Campos de identificação que a tela que usa a leitura mostra e preenche. */
export type CampoIdentificacao = "cargo" | "empresa" | "local";

export interface ResumoDaLeitura {
  preenchidos: string[];
  ausentes: string[];
}

const ROTULOS: Record<CampoIdentificacao, string> = {
  cargo: "título",
  empresa: "empresa",
  local: "local",
};

export const TODOS_OS_CAMPOS: CampoIdentificacao[] = ["cargo", "empresa", "local"];

/** Separa o que a leitura preencheu do que não encontrou, só entre os campos que a tela usa. */
export function resumirLeitura(
  dados: DadosVaga,
  campos: CampoIdentificacao[] = TODOS_OS_CAMPOS,
): ResumoDaLeitura {
  const preenchidos = campos.filter((campo) => dados[campo]).map((campo) => ROTULOS[campo]);
  const ausentes = campos.filter((campo) => !dados[campo]).map((campo) => ROTULOS[campo]);
  return { preenchidos: [...preenchidos, "descrição"], ausentes };
}

/** "título", "título e empresa", "título, empresa e local". */
export function juntarEmPortugues(itens: string[]): string {
  if (itens.length <= 1) return itens.join("");
  return `${itens.slice(0, -1).join(", ")} e ${itens[itens.length - 1]}`;
}
