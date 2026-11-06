import type {
  Candidatura,
  CandidaturasPorStatus,
  CurriculoSalvo,
  PerfilEstruturado,
  StatusCandidatura,
  Vaga,
} from "../../api/tipos";
import { dominioDaUrl, primeiraLinha } from "../../shared/formatacao";
import { rotuloStatus } from "../candidaturas/status";

export interface ItemRecente {
  id: string;
  tipo: "candidatura" | "vaga";
  titulo: string;
  subtitulo: string;
  data: string;
  status?: StatusCandidatura;
  destino: string;
}

export interface Atividade {
  tipo: "vaga_capturada" | "curriculo_salvo" | "status_candidatura";
  descricao: string;
  data: string;
}

export interface ResumoVisaoGeral {
  curriculos: number;
  vagasSalvas: number;
  candidaturasAtivas: number;
  aguardandoRetorno: number;
  emEntrevistaOuOferta: number;
  comOferta: number;
  itensRecentes: ItemRecente[];
  atividades: Atividade[];
}

export interface DadosVisaoGeral {
  curriculos: CurriculoSalvo[];
  vagas: Vaga[];
  candidaturas: CandidaturasPorStatus;
}

const LIMITE_ITENS_RECENTES = 5;
const LIMITE_ATIVIDADES = 6;

const maisRecentePrimeiro = <T extends { data: string }>(a: T, b: T) =>
  b.data.localeCompare(a.data);

/** Data da última mudança de status, ou a data em que a candidatura foi criada. */
function dataMaisRecente(candidatura: Candidatura): string {
  const historico = candidatura.historico_status ?? [];
  return historico[historico.length - 1]?.data ?? candidatura.data_aplicacao;
}

/** Agrega os dados das outras telas para a Visão geral (RF3.2, RF3.3, RF3.6). Função pura. */
export function montarResumo({
  curriculos,
  vagas,
  candidaturas,
}: DadosVisaoGeral): ResumoVisaoGeral {
  const doStatus = (status: StatusCandidatura) => candidaturas.por_status?.[status] ?? [];
  const todas = (["APLICADO", "ENTREVISTA", "OFERTA", "REJEITADO"] as const).flatMap(doStatus);

  const itensRecentes: ItemRecente[] = [
    ...todas.map((candidatura) => ({
      id: candidatura.id,
      tipo: "candidatura" as const,
      titulo: candidatura.cargo,
      subtitulo: candidatura.empresa,
      data: dataMaisRecente(candidatura),
      status: candidatura.status as StatusCandidatura,
      destino: "/candidaturas",
    })),
    ...vagas.map((vaga) => ({
      id: vaga.id,
      tipo: "vaga" as const,
      titulo: primeiraLinha(vaga.texto_descricao),
      subtitulo: dominioDaUrl(vaga.url_origem) || "Vaga colada",
      data: vaga.data_captura,
      destino: "/vagas-salvas",
    })),
  ]
    .sort(maisRecentePrimeiro)
    .slice(0, LIMITE_ITENS_RECENTES);

  const atividades: Atividade[] = [
    ...todas.flatMap((candidatura) =>
      (candidatura.historico_status ?? []).map((mudanca) => ({
        tipo: "status_candidatura" as const,
        descricao:
          mudanca.status === "APLICADO"
            ? `Candidatura criada: ${candidatura.cargo}`
            : `${candidatura.cargo} movida para ${rotuloStatus(mudanca.status)}`,
        data: mudanca.data,
      })),
    ),
    ...vagas.map((vaga) => ({
      tipo: "vaga_capturada" as const,
      descricao: `Vaga salva: ${primeiraLinha(vaga.texto_descricao, 60)}`,
      data: vaga.data_captura,
    })),
    ...curriculos.map((curriculo) => ({
      tipo: "curriculo_salvo" as const,
      descricao: `Currículo enviado: ${curriculo.nome_referencia}`,
      data: curriculo.data_upload,
    })),
  ]
    .sort(maisRecentePrimeiro)
    .slice(0, LIMITE_ATIVIDADES);

  return {
    curriculos: curriculos.length,
    vagasSalvas: vagas.length,
    candidaturasAtivas: doStatus("APLICADO").length + doStatus("ENTREVISTA").length,
    aguardandoRetorno: doStatus("APLICADO").length,
    emEntrevistaOuOferta: doStatus("ENTREVISTA").length + doStatus("OFERTA").length,
    comOferta: doStatus("OFERTA").length,
    itensRecentes,
    atividades,
  };
}

/** Percentual das 7 seções do currículo mestre que estão preenchidas (indicador visual, RF3.4). */
export function calcularCompletude(perfil: PerfilEstruturado | null): number {
  if (!perfil) return 0;
  const secoes = [
    perfil.nome_completo.trim() !== "" && perfil.email.trim() !== "",
    perfil.resumo_profissional.trim() !== "",
    (perfil.experiencias ?? []).length > 0,
    (perfil.formacoes ?? []).length > 0,
    (perfil.certificacoes ?? []).length > 0,
    (perfil.idiomas ?? []).length > 0,
    (perfil.tecnologias ?? []).length > 0,
  ];
  return Math.round((secoes.filter(Boolean).length / secoes.length) * 100);
}
