import {
  expect,
  test,
  type APIRequestContext,
  type CDPSession,
  type Locator,
  type Page,
} from "@playwright/test";
import {
  entrar,
  novoPerfil,
  semearCandidaturas,
  semearPerfilCompleto,
  type CandidaturaSemeada,
} from "./apoio";

const coluna = (page: Page, nome: string) =>
  page.getByRole("region", { name: new RegExp(`^${nome}`) });
const cartao = (page: Page, cargo: string) =>
  page
    .getByRole("listitem")
    .filter({ has: page.getByRole("button", { name: cargo, exact: true }) });
const titulos = (page: Page, nome: string) =>
  coluna(page, nome).getByRole("listitem").getByRole("button").allTextContents();

/**
 * Arrasto com o mouse em passos curtos, como o dnd-kit espera. O destino é decidido pelo retângulo do
 * cartão arrastado, então ele é agarrado pelo centro (ou pelo centro do `pegarEm`) e o centro dele é
 * levado ao ponto indicado do destino.
 */
async function arrastar(
  page: Page,
  origem: Locator,
  destino: Locator,
  { alturaRelativa = 0.5, pegarEm = origem }: { alturaRelativa?: number; pegarEm?: Locator } = {},
) {
  const cartaoDe = (await origem.boundingBox())!;
  const ponto = (await pegarEm.boundingBox())!;
  const para = (await destino.boundingBox())!;
  const x = ponto.x + ponto.width / 2;
  const y = ponto.y + ponto.height / 2;
  const deslocX = cartaoDe.x + cartaoDe.width / 2 - x;
  await page.mouse.move(x, y);
  await page.mouse.down();
  await page.mouse.move(x, y + 20, { steps: 4 });
  await page.mouse.move(para.x + para.width / 2 - deslocX, para.y + para.height * alturaRelativa, {
    steps: 15,
  });
  await page.waitForTimeout(200);
  await page.mouse.up();
}

/** Área rolável de uma coluna (filha direta da seção; as outras `div` são rodapés de cartões). */
const areaDaColuna = (page: Page, nome: string) => coluna(page, nome).locator(":scope > div");

const PRE_EXISTENTE = "Senior Python Engineer";

const ITENS: CandidaturaSemeada[] = [
  { cargo: "Backend Um", empresa: "Globex" },
  { cargo: "Backend Dois", empresa: "Initech" },
  { cargo: "Backend Três", empresa: "Umbrella" },
  { cargo: "Platform Um", empresa: "Hooli", status: "entrevista" },
  { cargo: "Platform Dois", empresa: "Stark", status: "entrevista" },
  { cargo: "Oferta Um", empresa: "Wayne", status: "oferta" },
];

test.describe("board de candidaturas: mouse", () => {
  test.beforeEach(async ({ page, request }) => {
    const perfil = novoPerfil("e2e-board");
    await semearPerfilCompleto(request, perfil);
    await semearCandidaturas(request, perfil, ITENS);
    await entrar(page, perfil);
    await page.setViewportSize({ width: 1600, height: 900 });
    await page.goto("/candidaturas");
    await expect(coluna(page, "Aplicado")).toContainText("Backend Um");
  });

  test("a ordem inicial segue a ordem semeada", async ({ page }) => {
    expect(await titulos(page, "Aplicado")).toEqual([
      "Backend Um",
      "Backend Dois",
      "Backend Três",
      PRE_EXISTENTE,
    ]);
    expect(await titulos(page, "Entrevista")).toEqual(["Platform Um", "Platform Dois"]);
  });

  test("arrastar para outra coluna move o cartão e persiste ao recarregar", async ({ page }) => {
    await arrastar(
      page,
      cartao(page, "Backend Dois"),
      coluna(page, "Oferta").getByRole("listitem"),
    );

    await expect(coluna(page, "Oferta")).toContainText("Backend Dois");
    await expect(page.getByText("Candidatura movida para Oferta.")).toBeVisible();
    await page.reload();
    await expect.poll(() => titulos(page, "Oferta")).toContain("Backend Dois");
    expect(await titulos(page, "Aplicado")).toEqual(["Backend Um", "Backend Três", PRE_EXISTENTE]);
  });

  test("arrastar sobre um cartão de outra coluna usa a posição dele", async ({ page }) => {
    await arrastar(page, cartao(page, "Backend Um"), cartao(page, "Platform Dois"), {
      alturaRelativa: 0.7,
    });

    await expect(coluna(page, "Entrevista")).toContainText("Backend Um");
    await page.reload();
    await expect.poll(() => titulos(page, "Entrevista")).toContain("Backend Um");
    expect(await titulos(page, "Entrevista")).toHaveLength(3);
  });

  test("arrastar para uma coluna vazia funciona", async ({ page }) => {
    await expect(coluna(page, "Rejeitado")).toContainText("Arraste um cartão até aqui");

    await arrastar(page, cartao(page, "Oferta Um"), coluna(page, "Rejeitado"), {
      alturaRelativa: 0.3,
    });

    await expect(coluna(page, "Rejeitado")).toContainText("Oferta Um");
    await expect(coluna(page, "Oferta")).toContainText("Nenhuma candidatura");
    await page.reload();
    await expect.poll(() => titulos(page, "Rejeitado")).toEqual(["Oferta Um"]);
  });

  test("reordenar dentro da coluna persiste a nova ordem", async ({ page }) => {
    await arrastar(page, cartao(page, "Backend Um"), cartao(page, "Backend Três"), {
      alturaRelativa: 0.7,
    });

    const esperada = ["Backend Dois", "Backend Três", "Backend Um", PRE_EXISTENTE];
    await expect.poll(() => titulos(page, "Aplicado")).toEqual(esperada);
    await page.reload();
    await expect.poll(() => titulos(page, "Aplicado")).toEqual(esperada);
  });

  test("soltar o cartão no mesmo lugar não altera nada", async ({ page }) => {
    const antes = await titulos(page, "Aplicado");

    await arrastar(page, cartao(page, "Backend Dois"), cartao(page, "Backend Dois"));
    await page.waitForTimeout(300);

    expect(await titulos(page, "Aplicado")).toEqual(antes);
    await expect(page.getByText(/Candidatura movida/)).toHaveCount(0);
  });

  test("Esc durante o arrasto cancela o movimento", async ({ page }) => {
    const de = (await cartao(page, "Backend Um").boundingBox())!;
    const para = (await coluna(page, "Oferta").boundingBox())!;
    await page.mouse.move(de.x + de.width - 12, de.y + de.height / 2);
    await page.mouse.down();
    await page.mouse.move(de.x + de.width - 12, de.y + 40, { steps: 4 });
    await page.mouse.move(para.x + 100, para.y + 200, { steps: 10 });
    await page.keyboard.press("Escape");
    await page.mouse.up();
    await page.waitForTimeout(300);

    expect(await titulos(page, "Aplicado")).toContain("Backend Um");
    await expect(page.getByText(/Candidatura movida/)).toHaveCount(0);
  });

  test("o clique no título abre o detalhe; arrastar pelo título não abre", async ({ page }) => {
    await page.getByRole("button", { name: "Backend Dois", exact: true }).click();
    const detalhe = page.getByRole("dialog", { name: "Backend Dois" });
    await expect(detalhe).toBeVisible();
    await expect(detalhe).toContainText("Initech");
    await page.keyboard.press("Escape");
    await expect(detalhe).toBeHidden();

    const titulo = page.getByRole("button", { name: "Backend Três", exact: true });
    await arrastar(
      page,
      cartao(page, "Backend Três"),
      coluna(page, "Oferta").getByRole("listitem"),
      {
        pegarEm: titulo,
      },
    );

    await expect(coluna(page, "Oferta")).toContainText("Backend Três");
    await expect(page.getByRole("dialog")).toHaveCount(0);
  });

  test('"Mover para" no detalhe move a candidatura e o board reflete', async ({ page }) => {
    await page.getByRole("button", { name: "Backend Um", exact: true }).click();
    const detalhe = page.getByRole("dialog", { name: "Backend Um" });

    await detalhe.getByLabel("Mover para").selectOption("OFERTA");

    await expect(page.getByText("Candidatura movida para Oferta.")).toBeVisible();
    await expect(detalhe.getByLabel("Mover para")).toHaveValue("OFERTA");
    await page.keyboard.press("Escape");
    await expect.poll(async () => (await titulos(page, "Oferta"))[0]).toBe("Backend Um");
    await page.reload();
    await expect.poll(async () => (await titulos(page, "Oferta"))[0]).toBe("Backend Um");
  });

  test("movimento por teclado: Espaço, duas setas para o lado (a primeira cai no fim da própria coluna) e Espaço", async ({
    page,
  }) => {
    await cartao(page, "Backend Um").focus();
    await page.keyboard.press("Space");
    await page.waitForTimeout(200);
    await page.keyboard.press("ArrowRight");
    await page.waitForTimeout(400);
    await page.keyboard.press("ArrowRight");
    await expect(
      page.getByText(/Candidatura Backend Um sobre Entrevista, posição \d de 3\./),
    ).toBeAttached();
    await page.keyboard.press("Space");

    await expect(coluna(page, "Entrevista")).toContainText("Backend Um");
    await page.reload();
    await expect.poll(() => titulos(page, "Entrevista")).toContain("Backend Um");
  });
});

test.describe("board de candidaturas: larguras", () => {
  const MUITAS: CandidaturaSemeada[] = Array.from({ length: 12 }, (_, indice) => ({
    cargo: `Vaga ${indice + 1}`,
    empresa: `Empresa ${indice + 1}`,
    status: (["aplicado", "entrevista", "oferta", "rejeitado"] as const)[indice % 4],
  }));

  for (const [largura, altura] of [
    [375, 740],
    [768, 900],
    [1280, 800],
  ] as const) {
    test(`${largura}px: a página não rola na horizontal e o board mantém colunas lado a lado`, async ({
      page,
      request,
    }) => {
      const perfil = novoPerfil("e2e-largura");
      await semearPerfilCompleto(request, perfil);
      await semearCandidaturas(request, perfil, MUITAS);
      await entrar(page, perfil);
      await page.setViewportSize({ width: largura, height: altura });
      await page.goto("/candidaturas");
      await expect(coluna(page, "Aplicado")).toBeVisible();

      const medidas = await page.evaluate(() => {
        const secoes = Array.from(document.querySelectorAll("section"));
        const quadro = secoes[0]!.parentElement!;
        const raiz = document.documentElement;
        return {
          paginaRolaNaHorizontal: raiz.scrollWidth > raiz.clientWidth,
          quadroRola: quadro.scrollWidth > quadro.clientWidth,
          larguras: secoes.map((secao) => Math.round(secao.getBoundingClientRect().width)),
          topos: secoes.map((secao) => Math.round(secao.getBoundingClientRect().top)),
          alturaDaPagina: raiz.scrollHeight,
        };
      });

      expect(medidas.paginaRolaNaHorizontal).toBe(false);
      expect(medidas.quadroRola).toBe(true);
      expect(new Set(medidas.larguras).size).toBe(1);
      expect(new Set(medidas.topos).size).toBe(1);
      expect(medidas.alturaDaPagina).toBeLessThanOrEqual(altura);
      if (largura <= 700) expect(medidas.larguras[0]).toBeLessThanOrEqual(320);
      else expect(medidas.larguras[0]).toBe(272);
    });
  }

  test("com muitos cartões, só a coluna rola na vertical; o cabeçalho continua visível", async ({
    page,
    request,
  }) => {
    const perfil = novoPerfil("e2e-rolagem");
    await semearPerfilCompleto(request, perfil);
    await semearCandidaturas(
      request,
      perfil,
      Array.from({ length: 14 }, (_, indice) => ({
        cargo: `Cartão ${indice + 1}`,
        empresa: "Acme",
      })),
    );
    await entrar(page, perfil);
    await page.setViewportSize({ width: 1280, height: 700 });
    await page.goto("/candidaturas");
    await expect(coluna(page, "Aplicado")).toContainText("Cartão 1");

    const area = areaDaColuna(page, "Aplicado");
    await area.hover();
    await page.mouse.wheel(0, 600);

    await expect.poll(() => area.evaluate((no) => no.scrollTop)).toBeGreaterThan(0);
    await expect(
      coluna(page, "Aplicado").getByRole("heading", { name: /Aplicado/ }),
    ).toBeInViewport();
    expect(await page.evaluate(() => window.scrollY)).toBe(0);
  });
});

test.describe("board de candidaturas: toque", () => {
  test.use({ hasTouch: true, isMobile: true, viewport: { width: 390, height: 740 } });

  const DOZE_CARTOES: CandidaturaSemeada[] = Array.from({ length: 12 }, (_, indice) => ({
    cargo: `Toque ${indice + 1}`,
    empresa: "Acme",
  }));

  async function abrirComToque(page: Page, request: APIRequestContext) {
    const perfil = novoPerfil("e2e-toque");
    await semearPerfilCompleto(request, perfil);
    await semearCandidaturas(request, perfil, DOZE_CARTOES);
    await entrar(page, perfil);
    await page.goto("/candidaturas");
    await expect(coluna(page, "Aplicado")).toContainText("Toque 1");
  }

  const dedo =
    (cdp: CDPSession) =>
    (tipo: "touchStart" | "touchMove" | "touchEnd", x = 0, y = 0) =>
      cdp.send("Input.dispatchTouchEvent", {
        type: tipo,
        touchPoints: tipo === "touchEnd" ? [] : [{ x, y }],
      });

  test("deslizar rola a coluna sem mover cartões", async ({ page, request, context }) => {
    await abrirComToque(page, request);
    const toque = dedo(await context.newCDPSession(page));
    const antes = await titulos(page, "Aplicado");
    const area = areaDaColuna(page, "Aplicado");
    const caixa = (await area.boundingBox())!;
    const x = caixa.x + caixa.width - 14;

    await toque("touchStart", x, caixa.y + caixa.height - 30);
    for (let passo = 1; passo <= 10; passo++) {
      await toque("touchMove", x, caixa.y + caixa.height - 30 - passo * 25);
      await page.waitForTimeout(12);
    }
    await toque("touchEnd");

    await expect.poll(() => area.evaluate((no) => no.scrollTop)).toBeGreaterThan(0);
    expect(await titulos(page, "Aplicado")).toEqual(antes);
    await expect(page.getByText(/Candidatura movida/)).toHaveCount(0);
  });

  test("toque longo seguido de movimento reordena o cartão e persiste", async ({
    page,
    request,
    context,
  }) => {
    await abrirComToque(page, request);
    const toque = dedo(await context.newCDPSession(page));
    const primeiro = (await cartao(page, "Toque 1").boundingBox())!;
    const terceiro = (await cartao(page, "Toque 3").boundingBox())!;
    const x = primeiro.x + primeiro.width / 2;
    const y = primeiro.y + primeiro.height - 10;
    const alvoY = terceiro.y + terceiro.height * 0.8;

    await toque("touchStart", x, y);
    await page.waitForTimeout(400);
    for (let passo = 1; passo <= 15; passo++) {
      await toque("touchMove", x, y + ((alvoY - y) * passo) / 15);
      await page.waitForTimeout(15);
    }
    await page.waitForTimeout(200);
    await toque("touchEnd");

    const esperada = ["Toque 2", "Toque 3", "Toque 1"];
    await expect.poll(async () => (await titulos(page, "Aplicado")).slice(0, 3)).toEqual(esperada);
    await page.reload();
    await expect.poll(async () => (await titulos(page, "Aplicado")).slice(0, 3)).toEqual(esperada);
  });

  test("toque simples no título abre o detalhe", async ({ page, request }) => {
    await abrirComToque(page, request);
    const titulo = (await page
      .getByRole("button", { name: "Toque 2", exact: true })
      .boundingBox())!;

    await page.touchscreen.tap(titulo.x + 10, titulo.y + 8);

    await expect(page.getByRole("dialog", { name: "Toque 2" })).toBeVisible();
  });
});
