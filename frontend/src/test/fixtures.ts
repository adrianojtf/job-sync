import { http, HttpResponse } from "msw";
import type { CurriculoSalvo, PerfilEstruturado, Vaga } from "../api/tipos";
import { API_TESTE } from "./renderizar-app";
import { servidorApi } from "./servidor-api";

export const PERFIL_ESTRUTURADO: PerfilEstruturado = {
  perfil_identificador: "adriano",
  nome_completo: "Adriano Teixeira",
  email: "adriano@email.com",
  linkedin: "",
  resumo_profissional: "Backend Java.",
  experiencias: [
    { empresa: "Neoway", cargo: "Dev Java", periodo: "2020-2024", descricao: "APIs." },
  ],
  formacoes: [],
  certificacoes: [],
  idiomas: [],
  tecnologias: ["Java"],
};

export const CURRICULO_SALVO: CurriculoSalvo = {
  id: "c1",
  perfil_identificador: "adriano",
  nome_referencia: "CV LinkedIn",
  data_upload: "2026-11-01T10:00:00",
};

export const VAGA_SALVA: Vaga = {
  id: "v1",
  perfil_identificador: "adriano",
  texto_descricao: "Senior Java Backend Developer\nRequisitos: Java, Kafka, AWS.",
  url_origem: "https://example.com/vaga/1",
  data_captura: "2026-11-05T09:00:00",
};

export const PROBLEMA_404 = {
  type: "t",
  title: "Não encontrado",
  status: 404,
  detail: "Perfil estruturado nao encontrado",
  instance: "i",
};

export const dimensao = (score: number, nivel = "adequado") => ({ score, nivel, confianca: 0.9 });

export const AVALIACAO_VAGA = {
  score: 78,
  completude: dimensao(75, "adequada"),
  clareza: dimensao(80, "clara"),
  relevancia: dimensao(85, "relevante"),
  inclusao: dimensao(72, "inclusiva"),
};

interface Base {
  perfil?: PerfilEstruturado | null;
  curriculos?: CurriculoSalvo[];
  vagas?: Vaga[];
}

/** Handlers de leitura usados pelas telas: perfil estruturado, biblioteca e vagas salvas. */
export function servirDadosBase({
  perfil = PERFIL_ESTRUTURADO,
  curriculos = [CURRICULO_SALVO],
  vagas = [VAGA_SALVA],
}: Base = {}) {
  servidorApi.use(
    http.get(`${API_TESTE}/v1/perfil-estruturado/:perfil`, () =>
      perfil ? HttpResponse.json(perfil) : HttpResponse.json(PROBLEMA_404, { status: 404 }),
    ),
    http.get(`${API_TESTE}/v1/curriculos`, () =>
      HttpResponse.json({ items: curriculos, total: curriculos.length }),
    ),
    http.get(`${API_TESTE}/v1/curriculos/:id/conteudo`, ({ params }) =>
      HttpResponse.json({
        id: params.id,
        nome_referencia: "CV LinkedIn",
        pdf_base64: btoa("%PDF-biblioteca"),
      }),
    ),
    http.get(`${API_TESTE}/v1/vagas`, () =>
      HttpResponse.json({ items: vagas, total: vagas.length, limite: 100, offset: 0 }),
    ),
  );
}

export const CANDIDATURA = {
  id: "cand-1",
  perfil_identificador: "adriano",
  vaga_id: "v0",
  curriculo_salvo_id: "c1",
  empresa: "Neoway",
  cargo: "Senior Java Backend Developer",
  status: "APLICADO",
  data_aplicacao: "2026-11-02T09:00:00",
  historico_status: [{ status: "APLICADO", data: "2026-11-02T09:00:00" }],
};
