import { expect, test } from "@playwright/test";
import { avisoDeStatus, entrar, novoPerfil, semearPerfilCompleto, violacoesGraves } from "./apoio";

/** Link como chega de um e-mail do LinkedIn, com parâmetros de rastreamento. */
const LINK_COM_RASTREAMENTO =
  "https://br.linkedin.com/jobs/view/engenheiro-at-empresa-e2e-1234567890?trk=eml-email_jobs_saved_job_reminder_01-saved~jobs-0-company_logo";
const LINK_NORMALIZADO = "https://www.linkedin.com/jobs/view/1234567890/";
const LINK_BLOQUEADO = "https://www.linkedin.com/jobs/view/9999999999/";
const AVISO_LEITURA =
  "Dados lidos do link: título, empresa e descrição. Confira antes de continuar.";

test.describe("leitura de vaga por link", () => {
  let perfil: string;

  test.beforeAll(async ({ request }) => {
    perfil = novoPerfil("e2e-link");
    await semearPerfilCompleto(request, perfil);
  });

  test("Ajustar vaga: o link preenche os campos e o fluxo segue até a revisão do currículo", async ({
    page,
  }) => {
    await entrar(page, perfil);
    await page.goto("/ajustar-vaga");

    await page.getByLabel("Link da vaga").fill(LINK_COM_RASTREAMENTO);
    await page.getByRole("button", { name: "Ler vaga" }).click();

    await expect(page.getByText(AVISO_LEITURA)).toBeVisible();
    await expect(page.getByLabel("Título da vaga")).toHaveValue("Engenheiro de Software Sênior");
    await expect(page.getByLabel("Empresa", { exact: true })).toHaveValue("Empresa E2E");
    await expect(page.getByLabel("Descrição da vaga")).toHaveValue(/Construímos plataformas/);

    await page.getByRole("button", { name: "Analisar vaga" }).click();
    await expect(page.getByRole("meter", { name: "Relevância" })).toBeVisible();
    await page.getByRole("button", { name: "Gerar currículo adaptado" }).click();
    await expect(page.getByRole("heading", { name: "Revise o currículo adaptado" })).toBeVisible();
  });

  test("Ajustar vaga: com o site bloqueado, mostra o motivo e continua pelo texto colado", async ({
    page,
  }) => {
    await entrar(page, perfil);
    await page.goto("/ajustar-vaga");

    await page.getByLabel("Link da vaga").fill(LINK_BLOQUEADO);
    await page.getByRole("button", { name: "Ler vaga" }).click();
    await expect(
      page.getByText(
        "O site não permitiu a leitura desta vaga. Cole o texto da vaga para continuar.",
      ),
    ).toBeVisible();
    await expect(page.getByLabel("Título da vaga")).toHaveValue("");

    await page.getByLabel("Descrição da vaga").fill("Engenheiro Backend\nPython e FastAPI.");
    await page.getByRole("button", { name: "Preencher os campos pelo texto" }).click();

    await expect(
      page.getByText(
        "Dados identificados no texto: título, empresa e descrição. Confira antes de continuar.",
      ),
    ).toBeVisible();
    await expect(page.getByLabel("Título da vaga")).toHaveValue("Engenheiro Backend");
    await expect(page.getByLabel("Empresa", { exact: true })).toHaveValue("Empresa do texto E2E");
  });

  test("Captura: lê o link, confere o rascunho e salva com a URL normalizada", async ({ page }) => {
    await entrar(page, perfil);
    await page.goto("/vagas-salvas");
    await page.getByRole("button", { name: "Colar vaga" }).click();
    const colar = page.getByRole("dialog", { name: "Colar vaga" });

    await colar.getByLabel("Link da vaga (opcional)").fill(LINK_COM_RASTREAMENTO);
    await colar.getByRole("button", { name: "Ler vaga" }).click();

    await expect(
      colar.getByText(
        "Dados lidos do link: título, empresa, local e descrição. Confira antes de continuar.",
      ),
    ).toBeVisible();
    await expect(colar.getByLabel("Título (opcional)")).toHaveValue(
      "Engenheiro de Software Sênior",
    );
    await expect(colar.getByLabel("Empresa (opcional)")).toHaveValue("Empresa E2E");
    await expect(colar.getByLabel("Local (opcional)")).toHaveValue("Brasil");
    await expect(colar.getByLabel("Link da vaga (opcional)")).toHaveValue(LINK_NORMALIZADO);

    await colar.getByRole("button", { name: "Salvar vaga" }).click();

    await expect(colar).toBeHidden();
    await expect(avisoDeStatus(page)).toHaveText("Vaga salva.");
    const resposta = await page.request.get(`/v1/vagas?perfil_identificador=${perfil}`);
    const salvas = (await resposta.json()).items as Record<string, string>[];
    const salva = salvas.find((vaga) => vaga.url_origem === LINK_NORMALIZADO);
    expect(salva).toMatchObject({
      cargo: "Engenheiro de Software Sênior",
      empresa: "Empresa E2E",
      local: "Brasil",
    });
    await expect(page.getByText("Sobre a Empresa E2E")).toBeVisible();
  });

  test("Ajustar vaga com o link lido, sem violações graves de acessibilidade", async ({ page }) => {
    await entrar(page, perfil);
    await page.goto("/ajustar-vaga");
    await page.getByLabel("Link da vaga").fill(LINK_COM_RASTREAMENTO);
    await page.getByRole("button", { name: "Ler vaga" }).click();
    await expect(page.getByText(AVISO_LEITURA)).toBeVisible();

    expect(await violacoesGraves(page)).toEqual([]);
  });

  test("Ajustar vaga com a leitura do link bloqueada, sem violações graves de acessibilidade", async ({
    page,
  }) => {
    await entrar(page, perfil);
    await page.goto("/ajustar-vaga");
    await page.getByLabel("Link da vaga").fill(LINK_BLOQUEADO);
    await page.getByRole("button", { name: "Ler vaga" }).click();
    await expect(page.getByText(/O site não permitiu a leitura desta vaga/)).toBeVisible();

    expect(await violacoesGraves(page)).toEqual([]);
  });

  test("Captura com o rascunho lido, sem violações graves de acessibilidade", async ({ page }) => {
    await entrar(page, perfil);
    await page.goto("/vagas-salvas");
    await page.getByRole("button", { name: "Colar vaga" }).click();
    const colar = page.getByRole("dialog", { name: "Colar vaga" });
    await colar.getByLabel("Link da vaga (opcional)").fill(LINK_COM_RASTREAMENTO);
    await colar.getByRole("button", { name: "Ler vaga" }).click();
    await expect(colar.getByText(/Dados lidos do link/)).toBeVisible();

    expect(await violacoesGraves(page)).toEqual([]);
  });
});
