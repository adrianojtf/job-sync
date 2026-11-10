import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

export const API_TESTE = "http://api.test";

/**
 * Leituras com resposta padrão "vazia" (perfil sem currículo mestre e listas vazias), para telas que
 * carregam dados de outras áreas (ex.: Visão geral). Escritas sem handler continuam falhando o teste.
 */
const leiturasPadrao = [
  http.get(`${API_TESTE}/v1/usuarios/me`, () =>
    HttpResponse.json(
      {
        type: "t",
        title: "Não autenticado",
        status: 401,
        detail: "Faça login para continuar.",
        instance: "i",
      },
      { status: 401 },
    ),
  ),
  http.get(`${API_TESTE}/v1/provedores`, () =>
    HttpResponse.json({ provedores: ["google"], senha: true, login_simples: false }),
  ),
  http.get(`${API_TESTE}/v1/perfil-estruturado/:perfil`, () =>
    HttpResponse.json(
      {
        type: "t",
        title: "Não encontrado",
        status: 404,
        detail: "Perfil estruturado nao encontrado",
        instance: "i",
      },
      { status: 404 },
    ),
  ),
  http.get(`${API_TESTE}/v1/curriculos`, () => HttpResponse.json({ items: [], total: 0 })),
  http.get(`${API_TESTE}/v1/vagas`, () =>
    HttpResponse.json({ items: [], total: 0, limite: 100, offset: 0 }),
  ),
  http.get(`${API_TESTE}/v1/candidaturas`, () =>
    HttpResponse.json({
      por_status: { APLICADO: [], ENTREVISTA: [], OFERTA: [], REJEITADO: [] },
      total: 0,
    }),
  ),
];

/** Servidor MSW compartilhado: cada teste registra seus handlers com servidorApi.use(...). */
export const servidorApi = setupServer(...leiturasPadrao);
