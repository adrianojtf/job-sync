import { expect, test, type APIRequestContext, type Locator, type Page } from "@playwright/test";
import { avisoDeStatus, entrar, novoPerfil } from "./apoio";

const REGIAO = {
  experiencias: "Experiências profissionais",
  formacoes: "Formação acadêmica",
  certificacoes: "Certificações",
  idiomas: "Idiomas",
} as const;

interface Semente {
  formacoes?: { instituicao: string; curso: string; periodo: string }[];
  certificacoes?: { nome: string; instituicao: string; ano: string }[];
}

/** Perfil com três experiências, duas formações, duas certificações e dois idiomas. */
async function semearPerfil(request: APIRequestContext, perfil: string, extra: Semente = {}) {
  const sessao = await request.post("/v1/sessoes/simples", { data: { identificador: perfil } });
  expect(sessao.ok()).toBeTruthy();
  const resposta = await request.post("/v1/perfil-estruturado", {
    data: {
      perfil_identificador: perfil,
      nome_completo: "Pessoa Teste",
      email: "pessoa@jobsync.test",
      linkedin: "",
      resumo_profissional: "Backend Python.",
      experiencias: ["Alfa", "Beta", "Gama"].map((empresa, indice) => ({
        empresa,
        cargo: "Dev",
        periodo: `${2018 + indice * 2} - ${2020 + indice * 2}`,
        descricao: "",
      })),
      formacoes: extra.formacoes ?? [
        { instituicao: "USP", curso: "Computação", periodo: "2012 - 2016" },
        { instituicao: "FIAP", curso: "MBA", periodo: "2019 - 2020" },
      ],
      certificacoes: extra.certificacoes ?? [
        { nome: "AWS SAA", instituicao: "AWS", ano: "2021" },
        { nome: "Scrum PSM", instituicao: "Scrum.org", ano: "2023" },
      ],
      idiomas: [
        { idioma: "Português", nivel: "NATIVO" },
        { idioma: "Inglês", nivel: "AVANCADO" },
      ],
      tecnologias: ["Python", "FastAPI"],
    },
  });
  expect(resposta.ok()).toBeTruthy();
}

async function abrirPerfil(page: Page, perfil: string) {
  await entrar(page, perfil);
  await page.goto("/perfil");
  await expect(page.getByRole("region", { name: REGIAO.experiencias })).toBeVisible();
}

/** Títulos na ordem da tela, lidos das alças "Mover X. Posição n de m" de cada item. */
async function titulos(page: Page, lista: keyof typeof REGIAO) {
  return page
    .getByRole("region", { name: REGIAO[lista] })
    .getByRole("button", { name: /^Mover .*\. Posição \d+ de \d+$/ })
    .evaluateAll((alcas) =>
      alcas.map(
        (alca) =>
          alca.getAttribute("aria-label")?.replace(/^Mover (.*)\. Posição \d+ de \d+$/, "$1") ?? "",
      ),
    );
}

/** Arrasta com passos intermediários: o sensor do dnd-kit só ativa depois de alguns pixels. */
async function arrastar(page: Page, origem: Locator, destino: Locator) {
  const de = (await origem.boundingBox())!;
  const para = (await destino.boundingBox())!;
  await page.mouse.move(de.x + de.width / 2, de.y + de.height / 2);
  await page.mouse.down();
  await page.mouse.move(de.x + de.width / 2 + 12, de.y + de.height / 2 + 12, { steps: 5 });
  await page.mouse.move(para.x + para.width / 2, para.y + para.height / 2, { steps: 15 });
  await page.mouse.up();
}

const alca = (page: Page, lista: keyof typeof REGIAO, titulo: string) =>
  page.getByRole("region", { name: REGIAO[lista] }).getByRole("button", {
    name: new RegExp(`^Mover ${titulo}\\. Posição`),
  });

/**
 * Teclado: Espaço pega o item, seta move, Espaço solta. O dnd-kit só passa a ouvir as setas depois
 * de um instante (setTimeout), então espera o anúncio de "pegou" antes de mover.
 */
async function moverComTeclado(page: Page, alcaDoItem: Locator, tecla: "ArrowDown" | "ArrowUp") {
  await alcaDoItem.focus();
  await page.keyboard.press("Space");
  await expect(
    page.locator("[id^=DndLiveRegion]").filter({ hasText: /sobre a posição/ }),
  ).toHaveCount(1);
  await page.waitForTimeout(100);
  await page.keyboard.press(tecla);
  await page.waitForTimeout(100);
  await page.keyboard.press("Space");
}

test("arrastar com o mouse reordena as experiências e a ordem sobrevive ao salvar", async ({
  page,
  request,
}) => {
  const perfil = novoPerfil("e2e-listas-mouse");
  await semearPerfil(request, perfil);
  await abrirPerfil(page, perfil);
  expect(await titulos(page, "experiencias")).toEqual(["Dev · Alfa", "Dev · Beta", "Dev · Gama"]);
  // Traz a lista para o topo: o rodapé fixo da tela pode cobrir as alças perto da borda inferior.
  await page
    .getByRole("region", { name: REGIAO.experiencias })
    .evaluate((regiao) => regiao.scrollIntoView({ block: "start" }));

  await arrastar(
    page,
    alca(page, "experiencias", "Dev · Gama"),
    alca(page, "experiencias", "Dev · Alfa"),
  );

  await expect
    .poll(() => titulos(page, "experiencias"))
    .toEqual(["Dev · Gama", "Dev · Alfa", "Dev · Beta"]);
  await expect(page.getByText("Alterações não salvas")).toBeVisible();
  await page.getByRole("button", { name: "Salvar perfil" }).click();
  await expect(avisoDeStatus(page)).toHaveText("Perfil salvo.");

  await page.reload();
  await expect(page.getByRole("region", { name: REGIAO.experiencias })).toBeVisible();
  expect(await titulos(page, "experiencias")).toEqual(["Dev · Gama", "Dev · Alfa", "Dev · Beta"]);
});

test("o teclado reordena formações e idiomas, e os botões reordenam as certificações", async ({
  page,
  request,
}) => {
  const perfil = novoPerfil("e2e-listas-teclado");
  await semearPerfil(request, perfil);
  await abrirPerfil(page, perfil);

  await moverComTeclado(page, alca(page, "formacoes", "MBA"), "ArrowUp");
  await moverComTeclado(page, alca(page, "idiomas", "Português"), "ArrowDown");
  await page
    .getByRole("region", { name: REGIAO.certificacoes })
    .getByRole("button", { name: "Mover AWS SAA para baixo" })
    .click();

  await expect.poll(() => titulos(page, "formacoes")).toEqual(["MBA", "Computação"]);
  await expect.poll(() => titulos(page, "idiomas")).toEqual(["Inglês", "Português"]);
  expect(await titulos(page, "certificacoes")).toEqual(["Scrum PSM", "AWS SAA"]);

  await page.getByRole("button", { name: "Salvar perfil" }).click();
  await expect(avisoDeStatus(page)).toHaveText("Perfil salvo.");
  await page.reload();
  await expect(page.getByRole("region", { name: REGIAO.formacoes })).toBeVisible();
  expect(await titulos(page, "formacoes")).toEqual(["MBA", "Computação"]);
  expect(await titulos(page, "idiomas")).toEqual(["Inglês", "Português"]);
  expect(await titulos(page, "certificacoes")).toEqual(["Scrum PSM", "AWS SAA"]);
});

test("período fora do formato bloqueia o salvar e mostra o erro no cartão", async ({
  page,
  request,
}) => {
  const perfil = novoPerfil("e2e-listas-periodo");
  await semearPerfil(request, perfil);
  await abrirPerfil(page, perfil);
  const cartao = page.getByRole("group", { name: "Experiência 1", exact: true });
  await cartao.getByRole("button", { name: "Editar Dev · Alfa" }).click();
  await cartao.getByLabel("Período").fill("ontem");

  await page.getByRole("button", { name: "Salvar perfil" }).click();

  await expect(cartao.getByText("Use o formato Mar 2024 - Atual ou 2020 - 2022.")).toBeVisible();
  await expect(page.getByText("Perfil salvo.")).toHaveCount(0);

  await cartao.getByLabel("Período").fill("Mar 2024 - Atual");
  await page.getByRole("button", { name: "Salvar perfil" }).click();
  await expect(avisoDeStatus(page)).toHaveText("Perfil salvo.");
});

test("lembra os cartões abertos depois de recarregar a página", async ({ page, request }) => {
  const perfil = novoPerfil("e2e-listas-lembrar");
  await semearPerfil(request, perfil);
  await abrirPerfil(page, perfil);
  const segundo = page.getByRole("group", { name: "Experiência 2", exact: true });
  await expect(segundo.getByLabel("Empresa")).toBeHidden();
  await segundo.getByRole("button", { name: "Editar Dev · Beta" }).click();
  await expect(segundo.getByLabel("Empresa")).toBeVisible();

  await page.reload();

  await expect(
    page.getByRole("group", { name: "Experiência 2", exact: true }).getByLabel("Empresa"),
  ).toBeVisible();
  await expect(
    page.getByRole("group", { name: "Experiência 1", exact: true }).getByLabel("Empresa"),
  ).toBeHidden();
});

test("pergunta antes de sair com alterações não salvas", async ({ page, request }) => {
  const perfil = novoPerfil("e2e-listas-aviso");
  await semearPerfil(request, perfil);
  await abrirPerfil(page, perfil);
  await page
    .getByRole("region", { name: REGIAO.idiomas })
    .getByRole("button", { name: "Mover Português para baixo" })
    .click();

  await page.getByRole("link", { name: /Visão geral/ }).click();
  const dialogo = page.getByRole("dialog", { name: "Sair sem salvar?" });
  await expect(dialogo).toBeVisible();
  await dialogo.getByRole("button", { name: "Cancelar" }).click();
  await expect(page).toHaveURL(/\/perfil$/);

  await page.getByRole("link", { name: /Visão geral/ }).click();
  await page
    .getByRole("dialog", { name: "Sair sem salvar?" })
    .getByRole("button", { name: /Sair/ })
    .click();
  await expect(page).not.toHaveURL(/\/perfil$/);
});

test("no limite de 15 itens não dá para adicionar outro", async ({ page, request }) => {
  const perfil = novoPerfil("e2e-listas-limite");
  await semearPerfil(request, perfil, {
    certificacoes: Array.from({ length: 15 }, (_, n) => ({
      nome: `Cert ${n + 1}`,
      instituicao: "Org",
      ano: "2022",
    })),
  });
  await abrirPerfil(page, perfil);
  const regiao = page.getByRole("region", { name: REGIAO.certificacoes });

  await expect(regiao.getByRole("button", { name: "Adicionar certificação" })).toBeDisabled();
  await expect(regiao.getByRole("note")).toContainText("limite de 15 itens");
});
