import type { StatusCandidatura } from "../../api/tipos";
import type { TomStatus } from "../../shared/ui/StatusBadge";

/** Ordem das colunas do Kanban (JOB-0006). */
export const ORDEM_STATUS: StatusCandidatura[] = ["APLICADO", "ENTREVISTA", "OFERTA", "REJEITADO"];

export const ROTULO_STATUS: Record<StatusCandidatura, string> = {
  APLICADO: "Aplicado",
  ENTREVISTA: "Entrevista",
  OFERTA: "Oferta",
  REJEITADO: "Rejeitado",
};

export const TOM_STATUS: Record<StatusCandidatura, TomStatus> = {
  APLICADO: "destaque",
  ENTREVISTA: "alerta",
  OFERTA: "sucesso",
  REJEITADO: "neutro",
};

export function rotuloStatus(status: string): string {
  return ROTULO_STATUS[status as StatusCandidatura] ?? status;
}
