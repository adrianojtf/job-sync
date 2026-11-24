import { expect, test } from "@playwright/test";
import {
  abrirDadosPessoais,
  entrar,
  EXPERIENCIAS_COM_REACT,
  novoPerfil,
  semearCandidaturas,
  semearPerfilCompleto,
  violacoesGraves,
} from "./apoio";

const TELAS = [
  "/",
  "/perfil",
  "/curriculos",
  "/vagas-salvas",
  "/descobrir-vagas",
  "/candidaturas",
  "/configuracoes",
  "/ajustar-vaga",
  "/analisar-ats",
];

test("Entrar sem violações graves", async ({ page }) => {
  await page.goto("/entrar");
  await expect(page.getByRole("heading", { name: "Entrar" })).toBeVisible();

  expect(await violacoesGraves(page)).toEqual([]);
});

test.describe("telas autenticadas", () => {
  let perfil: string;

  test.beforeAll(async ({ request }) => {
    perfil = novoPerfil("e2e-a11y");
    await semearPerfilCompleto(request, perfil);
  });

  for (const tela of TELAS) {
    test(`${tela} sem violações graves`, async ({ page }) => {
      await entrar(page, perfil);
      await page.goto(tela);
      await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
      await page.waitForLoadState("networkidle");

      expect(await violacoesGraves(page)).toEqual([]);
    });
  }

  test("revisão do currículo adaptado sem violações graves", async ({ page }) => {
    await entrar(page, perfil);
    await page.goto("/ajustar-vaga");
    await page.getByLabel("Título da vaga").fill("Senior Python Engineer");
    await page.getByLabel("Empresa").fill("Globex");
    await page.getByLabel("Descrição da vaga").fill("Python, FastAPI e Kafka.");
    await page.getByRole("button", { name: "Gerar currículo adaptado" }).click();
    await expect(page.getByRole("heading", { name: "Revise o currículo adaptado" })).toBeFocused();

    expect(await violacoesGraves(page)).toEqual([]);
  });

  test("revisão com a sugestão de IA aberta sem violações graves", async ({ page }) => {
    await entrar(page, perfil);
    await page.goto("/ajustar-vaga");
    await page.getByLabel("Título da vaga").fill("Senior Python Engineer");
    await page.getByLabel("Empresa").fill("Globex");
    await page.getByLabel("Descrição da vaga").fill("Python, FastAPI e Kafka.");
    await page.getByRole("button", { name: "Gerar currículo adaptado" }).click();
    await page.getByRole("button", { name: "Sugestões de IA para resumo" }).click();
    await expect(page.getByRole("region", { name: "Sugestão da IA para resumo" })).toBeVisible();

    expect(await violacoesGraves(page)).toEqual([]);
  });

  test("revisão com a sugestão de uma experiência aberta sem violações graves", async ({
    page,
  }) => {
    await entrar(page, perfil);
    await page.goto("/ajustar-vaga");
    await page.getByLabel("Título da vaga").fill("Senior Python Engineer");
    await page.getByLabel("Empresa").fill("Globex");
    await page.getByLabel("Descrição da vaga").fill("Python, FastAPI e Kafka.");
    await page.getByRole("button", { name: "Gerar currículo adaptado" }).click();
    await expect(page.getByText(/A IA pode ter estimado métricas e volumes/)).toBeVisible();
    await page.getByRole("button", { name: "Sugestões de IA para experiência 1" }).click();
    await expect(
      page.getByRole("region", { name: "Sugestão da IA para experiência 1" }),
    ).toBeVisible();

    expect(await violacoesGraves(page)).toEqual([]);
  });

  test("Meu perfil com botões de sugestão sem violações graves", async ({ page }) => {
    await entrar(page, perfil);
    await page.goto("/perfil");
    await abrirDadosPessoais(page);
    await page.getByRole("button", { name: "Sugestões de IA para resumo" }).click();
    await expect(page.getByRole("region", { name: "Sugestão da IA para resumo" })).toBeVisible();

    expect(await violacoesGraves(page)).toEqual([]);
  });

  test("modal Ajustar para uma vaga sem violações graves", async ({ page }) => {
    await entrar(page, perfil);
    await page.getByRole("button", { name: "Ajustar para uma vaga" }).click();
    await expect(page.getByRole("dialog")).toBeVisible();

    expect(await violacoesGraves(page)).toEqual([]);
  });
});

test("confirmar candidatura: botão, confirmação e detalhe com download sem violações graves", async ({
  page,
  request,
}) => {
  const perfil = novoPerfil("e2e-a11y-confirmar");
  await semearPerfilCompleto(request, perfil);
  await entrar(page, perfil);
  await page.goto("/ajustar-vaga");
  await page.getByLabel("Título da vaga").fill("Staff Platform Engineer");
  await page.getByLabel("Empresa").fill("Initech");
  await page
    .getByLabel("Descrição da vaga")
    .fill("Staff Platform Engineer\nGo, Kubernetes e Kafka.");
  await page.getByRole("button", { name: "Gerar currículo adaptado" }).click();
  await page.getByRole("button", { name: "Confirmar e gerar PDF" }).click();
  await expect(page.getByRole("button", { name: "Confirmar candidatura" })).toBeVisible();

  expect(await violacoesGraves(page)).toEqual([]);

  await page.getByRole("button", { name: "Confirmar candidatura" }).click();
  await expect(page.getByText("Candidatura confirmada em Aplicado.")).toBeFocused();

  expect(await violacoesGraves(page)).toEqual([]);

  await page.getByRole("link", { name: "Ver no board" }).click();
  await page.getByRole("button", { name: "Staff Platform Engineer", exact: true }).click();
  await expect(page.getByRole("button", { name: "Baixar PDF do currículo usado" })).toBeVisible();

  expect(await violacoesGraves(page)).toEqual([]);
});

test("revisão com ajustes de tecnologia e foco da sugestão sem violações graves", async ({
  page,
  request,
}) => {
  const perfil = novoPerfil("e2e-a11y-ajustes");
  await semearPerfilCompleto(request, perfil, EXPERIENCIAS_COM_REACT);
  await entrar(page, perfil);
  await page.goto("/ajustar-vaga");
  await page.getByLabel("Título da vaga").fill("Desenvolvedor Angular");
  await page.getByLabel("Empresa").fill("Globex");
  await page.getByLabel("Descrição da vaga").fill("Java e Angular.");
  await page.getByRole("button", { name: "Gerar currículo adaptado" }).click();
  await expect(page.getByRole("list", { name: "Ajustes de tecnologia" })).toBeVisible();
  await page.getByRole("button", { name: "Sugestões de IA para resumo" }).click();
  await expect(page.getByRole("region", { name: "Sugestão da IA para resumo" })).toContainText(
    "Foco:",
  );

  expect(await violacoesGraves(page)).toEqual([]);
});

test("board de candidaturas com cartões, durante o arrasto por teclado e com o detalhe aberto, sem violações graves", async ({
  page,
  request,
}) => {
  const perfil = novoPerfil("e2e-a11y-board");
  await semearPerfilCompleto(request, perfil);
  await semearCandidaturas(request, perfil, [
    { cargo: "Backend Um", empresa: "Globex" },
    { cargo: "Platform Um", empresa: "Hooli", status: "entrevista" },
    { cargo: "Oferta Um", empresa: "Wayne", status: "oferta" },
  ]);
  await entrar(page, perfil);
  await page.setViewportSize({ width: 1600, height: 900 });
  await page.goto("/candidaturas");
  await expect(page.getByRole("region", { name: /^Aplicado/ })).toContainText("Backend Um");

  expect(await violacoesGraves(page)).toEqual([]);

  await page.getByRole("listitem").filter({ hasText: "Backend Um" }).focus();
  await page.keyboard.press("Space");
  await expect(page.getByText("Candidatura Backend Um na posição original.")).toBeAttached();
  expect(await violacoesGraves(page)).toEqual([]);
  await page.keyboard.press("Escape");
  await expect(page.getByText(/Movimento cancelado/)).toBeAttached();

  await page.getByRole("button", { name: "Backend Um", exact: true }).click();
  await expect(page.getByLabel("Mover para")).toBeVisible();
  expect(await violacoesGraves(page)).toEqual([]);
});

test("board de candidaturas em tela de celular sem violações graves", async ({ page, request }) => {
  const perfil = novoPerfil("e2e-a11y-board-celular");
  await semearPerfilCompleto(request, perfil);
  await semearCandidaturas(request, perfil, [{ cargo: "Backend Um", empresa: "Globex" }]);
  await entrar(page, perfil);
  await page.setViewportSize({ width: 375, height: 740 });
  await page.goto("/candidaturas");
  await expect(page.getByRole("region", { name: /^Aplicado/ })).toContainText("Backend Um");

  expect(await violacoesGraves(page)).toEqual([]);
});
