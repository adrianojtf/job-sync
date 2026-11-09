import type { FocoRefino } from "../../api/tipos";

/** Como cada foco de refino da IA (JOB-0037) aparece no painel da sugestão. */
export const ROTULO_FOCO: Record<FocoRefino, string> = {
  aderencia_vaga: "aderência à vaga",
  impacto: "impacto e resultados",
  palavras_chave: "palavras-chave da vaga",
  clareza_concisao: "clareza e concisão",
  enfase_tecnica: "ênfase técnica",
};
