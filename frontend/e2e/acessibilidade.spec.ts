import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { entrar, EXPERIENCIAS_COM_REACT, novoPerfil, semearPerfilCompleto } from "./apoio";

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

/** Falha só com violações "serious" ou "critical" (WCAG 2.1 A/AA), como define a tarefa 10.0. */
async function violacoesGraves(page: Page) {
  const resultado = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
    .analyze();
  return resultado.violations
    .filter((violacao) => violacao.impact === "serious" || violacao.impact === "critical")
    .map((violacao) => ({
      regra: violacao.id,
      impacto: violacao.impact,
      elementos: violacao.nodes.map((no) => no.target.join(" ")),
    }));
}

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
  await page.getByRole("button", { name: "Detalhes de Staff Platform Engineer" }).click();
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
