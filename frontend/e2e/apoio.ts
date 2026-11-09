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

export async function entrar(page: Page, perfil: string) {
  await page.goto("/entrar");
  await page.getByLabel("Identificador").fill(perfil);
  await page.getByRole("button", { name: "Entrar" }).click();
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
  await request.get(`/v1/perfis/${perfil}`);
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
