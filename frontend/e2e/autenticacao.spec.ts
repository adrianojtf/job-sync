import { expect, test } from "@playwright/test";
import {
  API_E2E,
  definirIdentidadeDoGoogle,
  entrar,
  novoEmail,
  novoPerfil,
  SAUDACAO,
  semearPerfilCompleto,
  tokenDoUltimoEmail,
} from "./apoio";

const SENHA = "uma-senha-bem-longa-1";

test.beforeEach(async ({ request }) => {
  await request.delete(`${API_E2E}/e2e/limites`);
});

test("cadastro por e-mail: confirmar o link, entrar, ver o usuário e sair", async ({
  page,
  request,
  context,
}) => {
  const email = novoEmail("cadastro");

  await page.goto("/cadastrar");
  await page.getByLabel("E-mail").fill(email);
  await page.getByLabel("Senha", { exact: true }).fill(SENHA);
  await page.getByLabel("Confirmar senha").fill(SENHA);
  await page.getByRole("button", { name: "Criar conta" }).click();
  await expect(page.getByRole("heading", { name: "Verifique seu e-mail" })).toBeVisible();

  const entrarAntesDeConfirmar = await request.post("/v1/sessoes", {
    data: { email, senha: SENHA },
  });
  expect(entrarAntesDeConfirmar.status()).toBe(401);

  const token = await tokenDoUltimoEmail(request, email);
  await page.goto(`/confirmar-email?token=${token}`);
  await page.getByRole("button", { name: "Confirmar meu e-mail" }).click();
  await expect(page.getByRole("heading", { name: "E-mail confirmado" })).toBeVisible();

  await page.getByRole("link", { name: "Entrar" }).click();
  await page.getByLabel("E-mail").fill(email);
  await page.getByLabel("Senha").fill(SENHA);
  await page.getByRole("button", { name: "Entrar", exact: true }).click();

  await expect(page.getByRole("heading", { level: 1 })).toHaveText(SAUDACAO);
  await expect(page.getByRole("complementary").getByText(email)).toBeVisible();

  const cookies = await context.cookies();
  const sessao = cookies.find((cookie) => cookie.name === "js_sessao");
  expect(sessao?.httpOnly).toBe(true);
  expect(sessao?.sameSite).toBe("Lax");
  expect(await page.evaluate(() => document.cookie)).not.toContain("js_sessao");
  expect(await page.evaluate(() => JSON.stringify(localStorage))).not.toContain(email);

  await page.reload();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(SAUDACAO);

  await page.getByRole("button", { name: "Sair" }).click();
  await expect(page.getByRole("heading", { name: "Entrar" })).toBeVisible();
  await page.goto("/candidaturas");
  await expect(page.getByRole("heading", { name: "Entrar" })).toBeVisible();
});

test("rota protegida sem sessão leva a Entrar e volta para a página pedida depois do login", async ({
  page,
}) => {
  const perfil = novoPerfil("e2e-destino");

  await page.goto("/candidaturas");
  await expect(page.getByRole("heading", { name: "Entrar" })).toBeVisible();
  await page.getByLabel("Identificador (somente desenvolvimento)").fill(perfil);
  await page.getByRole("button", { name: "Entrar por identificador" }).click();

  await expect(page).toHaveURL(/\/candidaturas$/);
});

test("senha errada mostra mensagem única e não abre sessão", async ({ page, request }) => {
  const email = novoEmail("senha-errada");
  await request.post("/v1/usuarios", { data: { email, senha: SENHA } });
  await request.put(`/v1/confirmacoes-email/${await tokenDoUltimoEmail(request, email)}`);

  await page.goto("/entrar");
  await page.getByLabel("E-mail").fill(email);
  await page.getByLabel("Senha").fill("senha-errada-123");
  await page.getByRole("button", { name: "Entrar", exact: true }).click();

  await expect(page.getByText(/E-mail ou senha incorretos\./)).toBeVisible();
  await expect(page.getByRole("heading", { name: "Entrar" })).toBeVisible();
});

test("recuperar a senha: o link troca a senha e a antiga deixa de valer", async ({
  page,
  request,
}) => {
  const email = novoEmail("recuperar");
  await request.post("/v1/usuarios", { data: { email, senha: SENHA } });
  await request.put(`/v1/confirmacoes-email/${await tokenDoUltimoEmail(request, email)}`);

  await page.goto("/recuperar-senha");
  await page.getByLabel("E-mail").fill(email);
  await page.getByRole("button", { name: "Enviar link" }).click();
  await expect(page.getByText(/Se esse e-mail tiver cadastro/)).toBeVisible();

  const token = await tokenDoUltimoEmail(request, email);
  await page.goto(`/redefinir-senha?token=${token}`);
  await page.getByLabel("Nova senha", { exact: true }).fill("outra-senha-bem-longa-2");
  await page.getByLabel("Confirmar nova senha").fill("outra-senha-bem-longa-2");
  await page.getByRole("button", { name: "Salvar nova senha" }).click();
  await expect(page.getByRole("heading", { name: "Senha redefinida" })).toBeVisible();

  const antiga = await request.post("/v1/sessoes", { data: { email, senha: SENHA } });
  const nova = await request.post("/v1/sessoes", {
    data: { email, senha: "outra-senha-bem-longa-2" },
  });
  expect(antiga.status()).toBe(401);
  expect(nova.status()).toBe(201);

  const reutilizado = await request.put(`/v1/redefinicoes-senha/${token}`, {
    data: { nova_senha: "mais-uma-senha-longa-3" },
  });
  expect(reutilizado.status()).toBe(400);
});

test("login com Google: cria o perfil, mantém a sessão e respeita o destino pedido", async ({
  page,
  request,
}) => {
  const email = novoEmail("google");
  await definirIdentidadeDoGoogle(request, {
    subject: `sub-${Date.now()}`,
    email,
    nome: "Pessoa Google",
  });

  await page.goto("/candidaturas");
  await page.getByRole("link", { name: "Entrar com Google" }).click();

  await expect(page).toHaveURL(/\/candidaturas$/);
  await expect(page.getByRole("heading", { level: 1, name: "Candidaturas" })).toBeVisible();
  await expect(page.getByRole("complementary").getByText("Pessoa Google")).toBeVisible();
  const cookies = await page.context().cookies();
  expect(cookies.find((cookie) => cookie.name === "js_oauth")).toBeUndefined();
  expect(cookies.find((cookie) => cookie.name === "js_sessao")?.httpOnly).toBe(true);

  await page.reload();
  await expect(page.getByRole("heading", { level: 1, name: "Candidaturas" })).toBeVisible();
});

test("login com Google de e-mail não verificado é recusado", async ({ page, request }) => {
  await definirIdentidadeDoGoogle(request, {
    subject: `sub-${Date.now()}`,
    email: novoEmail("nao-verificado"),
    email_verificado: false,
  });

  await page.goto("/entrar");
  await page.getByRole("link", { name: "Entrar com Google" }).click();

  await expect(page).toHaveURL(/\/entrar\?erro=email_nao_verificado$/);
  await expect(page.getByText(/não confirmou o e-mail/)).toBeVisible();
  const me = await page.request.get("/v1/usuarios/me");
  expect(me.status()).toBe(401);
});

test("perfil legado: o dono entra com Google no e-mail associado e vê os dados antigos", async ({
  page,
  request,
}) => {
  const perfil = novoPerfil("legado");
  const email = novoEmail("dono-legado");
  const criado = await request.post(`${API_E2E}/e2e/perfis-legados`, {
    data: { perfil, email, nome_completo: "Dono do Perfil Legado" },
  });
  expect(criado.ok()).toBeTruthy();
  await definirIdentidadeDoGoogle(request, { subject: `sub-${Date.now()}`, email });

  await page.goto("/entrar");
  await page.getByRole("link", { name: "Entrar com Google" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(SAUDACAO);

  const me = await (await page.request.get("/v1/usuarios/me")).json();
  expect(me.perfil_identificador).toBe(perfil);
  await page.goto("/perfil");
  await expect(page.getByLabel("Nome completo")).toHaveValue("Dono do Perfil Legado");
});

test("perfil legado não é acessível por quem não prova o e-mail do dono", async ({
  page,
  request,
  browser,
}) => {
  const perfil = novoPerfil("legado-protegido");
  const emailDoDono = novoEmail("dono-protegido");
  await request.post(`${API_E2E}/e2e/perfis-legados`, {
    data: { perfil, email: emailDoDono, nome_completo: "Dono Protegido" },
  });

  await definirIdentidadeDoGoogle(request, {
    subject: `sub-${Date.now()}`,
    email: novoEmail("intruso"),
  });
  await page.goto("/entrar");
  await page.getByRole("link", { name: "Entrar com Google" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(SAUDACAO);

  const leitura = await page.request.get(`/v1/perfil-estruturado/${perfil}`);
  expect(leitura.status()).toBe(403);
  const perfilDoIntruso = await (await page.request.get("/v1/usuarios/me")).json();
  expect(perfilDoIntruso.perfil_identificador).not.toBe(perfil);

  const contextoAnonimo = await browser.newContext({
    baseURL: page.url().split("/").slice(0, 3).join("/"),
  });
  const semSessao = await contextoAnonimo.request.get(`/v1/perfil-estruturado/${perfil}`);
  expect(semSessao.status()).toBe(401);
  await contextoAnonimo.close();
});

test("um usuário não lê nem altera dados de outro", async ({ request, browser }) => {
  const perfilA = novoPerfil("isolamento-a");
  await semearPerfilCompleto(request, perfilA);

  const contextoB = await browser.newContext({ baseURL: "http://localhost:5180" });
  const perfilB = novoPerfil("isolamento-b");
  await contextoB.request.post("/v1/sessoes/simples", { data: { identificador: perfilB } });

  const leitura = await contextoB.request.get(`/v1/perfil-estruturado/${perfilA}`);
  const listagem = await contextoB.request.get("/v1/curriculos", {
    params: { perfil_identificador: perfilA },
  });
  const escrita = await contextoB.request.post("/v1/curriculos", {
    data: { perfil_identificador: perfilA, nome_referencia: "invasor", pdf_base64: "JVBERi0=" },
  });
  const proprio = await contextoB.request.get("/v1/curriculos", {
    params: { perfil_identificador: perfilB },
  });
  await contextoB.close();

  expect([leitura.status(), listagem.status(), escrita.status()]).toEqual([403, 403, 403]);
  expect(proprio.status()).toBe(200);
});

test("origem estranha com cookie de sessão não consegue escrever (CSRF)", async ({ page }) => {
  const perfil = novoPerfil("e2e-csrf");
  await entrar(page, perfil);

  const resposta = await page.request.delete("/v1/sessoes/atual", {
    headers: { Origin: "https://site-malicioso.example" },
  });

  expect(resposta.status()).toBe(403);
  const me = await page.request.get("/v1/usuarios/me");
  expect(me.status()).toBe(200);
});
