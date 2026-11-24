import { expect, test, type Locator, type Page } from "@playwright/test";
import { abrirExperiencia, avisoDeStatus, entrar, novoPerfil, semearPerfilCompleto } from "./apoio";

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

test("perfil antigo: estruturar as experiências, salvar e ver as skills nas tecnologias", async ({
  page,
  request,
}) => {
  const perfil = novoPerfil("e2e-blocos-migracao");
  await semearPerfilCompleto(request, perfil);
  await entrar(page, perfil);
  await page.goto("/perfil");

  const experiencia = await abrirExperiencia(page, 1);
  await expect(experiencia.getByLabel("Descrição")).toHaveValue("APIs em Python.");
  await page.getByRole("button", { name: "Estruturar experiências" }).click();

  await expect(experiencia.getByLabel("Contexto")).toHaveValue("Contexto gerado de Olist.");
  await expect(experiencia.getByLabel("Principais responsabilidades")).toHaveValue(
    "Responsabilidade gerada de Olist.",
  );
  await expect(experiencia.getByRole("textbox", { name: "Conquista 1" })).toHaveValue(
    "Realização gerada de Olist.",
  );
  const skills = experiencia.getByRole("group", { name: "Skills da experiência 1" });
  await expect(skills.getByText("Python")).toBeVisible();
  await expect(skills.getByText("Flyway")).toBeVisible();
  await expect(page.getByText(/A IA pode ter estimado métricas e contextos/)).toBeVisible();

  await skills.getByLabel("Nova skill").fill("Kafka");
  await skills.getByLabel("Nova skill").press("Enter");
  await page.getByRole("button", { name: "Salvar perfil" }).click();
  await expect(avisoDeStatus(page)).toHaveText(
    "Perfil salvo. Tecnologias incluídas pelas skills: Flyway, Kafka.",
  );

  await page.reload();
  const reaberta = await abrirExperiencia(page, 1);
  await expect(reaberta.getByLabel("Contexto")).toHaveValue("Contexto gerado de Olist.");
  for (const tecnologia of ["Python", "FastAPI", "Flyway", "Kafka"]) {
    await expect(
      page.getByRole("button", { name: `Remover ${tecnologia}`, exact: true }).last(),
    ).toBeVisible();
  }
  await expect(page.getByRole("button", { name: "Estruturar experiências" })).toHaveCount(0);
});

test("currículo adaptado: mostra os quatro blocos e move uma tag para outra categoria arrastando", async ({
  page,
  request,
}) => {
  const perfil = novoPerfil("e2e-blocos-revisao");
  await semearPerfilCompleto(request, perfil);
  await request.put(`/v1/perfil-estruturado/${perfil}`, {
    data: {
      perfil_identificador: perfil,
      nome_completo: "Pessoa Teste",
      email: "pessoa@jobsync.test",
      linkedin: "",
      resumo_profissional: "Backend Python.",
      experiencias: [
        {
          empresa: "Olist",
          cargo: "Backend",
          periodo: "2021-2024",
          descricao: "",
          contexto: "Marketplace de e-commerce.",
          responsabilidades: ["Projetar APIs"],
          conquistas: [{ texto: "Reduzi o tempo de resposta em 40%.", origem: "MANUAL" }],
          skills: ["Python", "Flyway"],
        },
      ],
      formacoes: [],
      certificacoes: [],
      idiomas: [],
      tecnologias: ["Python", "FastAPI"],
    },
  });
  await entrar(page, perfil);

  await page.goto("/ajustar-vaga");
  await page.getByLabel("Título da vaga").fill("Senior Python Engineer");
  await page.getByLabel("Empresa").fill("Globex");
  await page.getByLabel("Descrição da vaga").fill("Python e FastAPI.");
  await page.getByRole("button", { name: "Gerar currículo adaptado" }).click();
  await expect(page.getByRole("heading", { name: "Revise o currículo adaptado" })).toBeVisible();

  const experiencia = page.getByRole("group", { name: "Experiência 1" });
  await expect(experiencia.getByLabel("Principais responsabilidades")).toHaveValue("Projetar APIs");
  await expect(experiencia.getByLabel("Principais realizações")).toHaveValue(
    "Reduzi o tempo de resposta em 40%.",
  );
  await expect(
    experiencia.getByRole("group", { name: "Skills da experiência 1" }).getByText("Flyway"),
  ).toBeVisible();

  const tecnologias = page.getByRole("group", { name: "Tecnologias", exact: true });
  await expect(tecnologias.getByText("Flyway")).toBeVisible();

  await page.getByRole("button", { name: "Adicionar categoria" }).click();
  await page.getByLabel("Nome da categoria").last().fill("Banco de dados");
  const banco = page.getByRole("group", { name: "Banco de dados", exact: true });
  await arrastar(
    page,
    tecnologias.getByRole("button", { name: "Mover Flyway", exact: true }),
    banco.getByRole("list"),
  );

  await expect(banco.getByText("Flyway")).toBeVisible();
  await expect(tecnologias.getByText("Flyway")).toHaveCount(0);
  await expect(tecnologias.getByText("Python")).toBeVisible();
});
