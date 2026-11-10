import { expect, type APIRequestContext, type Page } from "@playwright/test";

export const SAUDACAO = /^(Bom dia|Boa tarde|Boa noite), /;

/** Identificador único por execução: o banco E2E é reaproveitado entre rodadas. */
export const novoPerfil = (prefixo: string) =>
  `${prefixo}-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

/**
 * Duas experiências com React: com uma vaga que cita Angular, o dublê de IA do E2E aponta
 * React → Angular, e o plano troca só na primeira (a última mantém React).
 */
export const EXPERIENCIAS_COM_REACT: ExperienciaSemeada[] = [
  { empresa: "Acme", cargo: "Front-end", periodo: "2022-2024", descricao: "Telas em React." },
  { empresa: "Initech", cargo: "Front-end", periodo: "2019-2022", descricao: "Portal em React." },
];

/** PDF mínimo para o upload (o backend guarda o arquivo sem interpretá-lo). */
export const PDF_MINIMO = {
  name: "curriculo-e2e.pdf",
  mimeType: "application/pdf",
  buffer: Buffer.from("%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"),
};

/** Entra pela tela, com o login por identificador que o app de E2E habilita só para testes. */
export async function entrar(page: Page, perfil: string) {
  await page.goto("/entrar");
  await page.getByLabel("Identificador (somente desenvolvimento)").fill(perfil);
  await page.getByRole("button", { name: "Entrar por identificador" }).click();
  // A própria tela de login tem um h1: sem esperar a saída dela, o teste segue (e recarrega a
  // página) antes de a sessão ser gravada e volta para o login.
  await expect(page).not.toHaveURL(/\/entrar$/);
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
}

interface ExperienciaSemeada {
  empresa: string;
  cargo: string;
  periodo: string;
  descricao: string;
}

const EXPERIENCIAS_PADRAO: ExperienciaSemeada[] = [
  { empresa: "Olist", cargo: "Backend", periodo: "2021-2024", descricao: "APIs em Python." },
];

/** Prepara dados pela API (mesma origem, via proxy /v1) para telas que precisam de conteúdo. */
export async function semearPerfilCompleto(
  request: APIRequestContext,
  perfil: string,
  experiencias: ExperienciaSemeada[] = EXPERIENCIAS_PADRAO,
) {
  // O contexto de API tem o próprio cookie: sem sessão, todas as rotas de dados respondem 401.
  const sessao = await request.post("/v1/sessoes/simples", { data: { identificador: perfil } });
  expect(sessao.ok()).toBeTruthy();
  await request.post("/v1/perfil-estruturado", {
    data: {
      perfil_identificador: perfil,
      nome_completo: "Pessoa Teste",
      email: "pessoa@jobsync.test",
      linkedin: "",
      resumo_profissional: "Backend Python.",
      experiencias,
      formacoes: [],
      certificacoes: [],
      idiomas: [],
      tecnologias: ["Python", "FastAPI"],
    },
  });
  await request.post("/v1/curriculos", {
    data: {
      perfil_identificador: perfil,
      nome_referencia: "CV E2E",
      pdf_base64: PDF_MINIMO.buffer.toString("base64"),
    },
  });
  const vaga = await request.post("/v1/vagas", {
    data: {
      perfil_identificador: perfil,
      texto_descricao: "Senior Python Engineer\nPython e Kafka.",
      url_origem: "https://example.com/1",
    },
  });
  const { id: vagaId } = await vaga.json();
  await request.post("/v1/vagas", {
    data: {
      perfil_identificador: perfil,
      texto_descricao: "Platform Engineer\nGo e Kubernetes.",
      url_origem: null,
    },
  });
  const curriculos = await (
    await request.get(`/v1/curriculos?perfil_identificador=${perfil}`)
  ).json();
  await request.post("/v1/candidaturas", {
    data: {
      perfil_identificador: perfil,
      vaga_id: vagaId,
      curriculo_salvo_id: curriculos.items[0].id,
      empresa: "Globex",
      cargo: "Senior Python Engineer",
    },
  });
}

export type StatusSemeado = "aplicado" | "entrevista" | "oferta" | "rejeitado";

export interface CandidaturaSemeada {
  cargo: string;
  empresa: string;
  status?: StatusSemeado;
}

/**
 * Cria candidaturas pela API, já nas colunas pedidas. A ordem de cada coluna no board é a ordem
 * em que os itens aparecem em `itens` (a API coloca o último criado no topo, então cria ao contrário).
 * O perfil precisa ter sido semeado com `semearPerfilCompleto`.
 */
export async function semearCandidaturas(
  request: APIRequestContext,
  perfil: string,
  itens: CandidaturaSemeada[],
) {
  const vagas = await (await request.get(`/v1/vagas?perfil_identificador=${perfil}`)).json();
  const curriculos = await (
    await request.get(`/v1/curriculos?perfil_identificador=${perfil}`)
  ).json();
  for (const item of [...itens].reverse()) {
    const criada = await request.post("/v1/candidaturas", {
      data: {
        perfil_identificador: perfil,
        vaga_id: vagas.items[0].id,
        curriculo_salvo_id: curriculos.items[0].id,
        empresa: item.empresa,
        cargo: item.cargo,
      },
    });
    const { id } = await criada.json();
    if (item.status && item.status !== "aplicado") {
      await request.post(`/v1/candidaturas/${id}/submissao`, {
        data: { novo_status: item.status, posicao: 0 },
      });
    }
  }
}

/** O app de E2E expõe fora de /v1 a caixa de e-mail e o Google simulado (porta da API, sem proxy). */
export const API_E2E = "http://localhost:8010";

export const novoEmail = (prefixo: string) =>
  `${prefixo}-${Date.now()}-${Math.floor(Math.random() * 1000)}@jobsync.test`;

/** Lê o token do último link enviado por e-mail ao destinatário. */
export async function tokenDoUltimoEmail(request: APIRequestContext, email: string) {
  const resposta = await request.get(`${API_E2E}/e2e/emails`, { params: { para: email } });
  const emails = (await resposta.json()) as { corpo: string }[];
  for (const { corpo } of emails.reverse()) {
    const encontrado = corpo.match(/token=([\w-]+)/);
    if (encontrado) return encontrado[1]!;
  }
  throw new Error(`Nenhum e-mail com link para ${email}.`);
}

/** Define quem o "Google" diz que está entrando no próximo login. */
export async function definirIdentidadeDoGoogle(
  request: APIRequestContext,
  identidade: { subject: string; email: string; email_verificado?: boolean; nome?: string },
) {
  const resposta = await request.put(`${API_E2E}/e2e/idp/identidade`, { data: identidade });
  expect(resposta.ok()).toBeTruthy();
}
