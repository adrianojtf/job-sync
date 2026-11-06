import { formatarData } from "../../shared/formatacao";

const MINUTO = 60_000;
const DIA_DA_SEMANA_E_MES = new Intl.DateTimeFormat("pt-BR", {
  weekday: "long",
  day: "2-digit",
  month: "long",
});

/** "Bom dia" (5h–11h59), "Boa tarde" (12h–17h59) ou "Boa noite". */
export function saudacao(agora: Date): string {
  const hora = agora.getHours();
  if (hora >= 5 && hora < 12) return "Bom dia";
  if (hora >= 12 && hora < 18) return "Boa tarde";
  return "Boa noite";
}

/** Ex.: "quinta-feira, 06 de novembro" (o cabeçalho exibe em maiúsculas, como no protótipo). */
export function dataPorExtenso(agora: Date): string {
  return DIA_DA_SEMANA_E_MES.format(agora);
}

function inicioDoDia(data: Date): number {
  return new Date(data.getFullYear(), data.getMonth(), data.getDate()).getTime();
}

/** Tempo decorrido para a lista de atividades: "Agora", "Há 20 min", "Há 2 horas", "Ontem", "Há 3 dias" ou a data. */
export function tempoRelativo(iso: string, agora: Date): string {
  const data = new Date(iso);
  const dias = Math.round((inicioDoDia(agora) - inicioDoDia(data)) / (24 * 60 * MINUTO));
  if (dias === 0) {
    const minutos = Math.floor((agora.getTime() - data.getTime()) / MINUTO);
    if (minutos < 1) return "Agora";
    if (minutos < 60) return `Há ${minutos} min`;
    const horas = Math.floor(minutos / 60);
    return horas === 1 ? "Há 1 hora" : `Há ${horas} horas`;
  }
  if (dias === 1) return "Ontem";
  if (dias > 1 && dias < 7) return `Há ${dias} dias`;
  return formatarData(iso);
}
