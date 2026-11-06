/** Dados que outras telas passam ao abrir "Ajustar para uma vaga" (RF6.5). */
export interface EstadoAjustarVaga {
  cargo?: string;
  empresa?: string;
  descricao?: string;
  /** Dispara "Analisar vaga" ao abrir (botão do modal do protótipo). */
  analisarAoAbrir?: boolean;
  /** Identifica um novo pedido: reabrir a tela com outro pedido recomeça o fluxo. */
  pedido?: number;
}

/** Dados que outras telas passam ao abrir "Analisar ATS". */
export interface EstadoAnalisarAts {
  descricao?: string;
}

export const ROTA_AJUSTAR_VAGA = "/ajustar-vaga";
export const ROTA_ANALISAR_ATS = "/analisar-ats";
