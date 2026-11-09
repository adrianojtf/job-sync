import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import {
  entrar,
  EXPERIENCIAS_COM_REACT,
  novoPerfil,
  PDF_MINIMO,
  SAUDACAO,
  semearPerfilCompleto,
} from "./apoio";

test("primeiro acesso: entrar, ver a Visão geral vazia e salvar o currículo mestre", async ({
  page,
}) => {
  const perfil = novoPerfil("e2e-perfil");

  await entrar(page, perfil);

  await expect(page.getByRole("heading", { level: 1 })).toHaveText(SAUDACAO);
  await expect(page.getByRole("heading", { name: "Complete seu currículo mestre" })).toBeVisible();
  await expect(page.getByRole("group", { name: "Vagas salvas" })).toContainText("0");

  await page.getByRole("link", { name: "Preencher meu perfil" }).click();
  await page.getByLabel("Nome completo").fill("Ana Lima");
  await page.getByLabel("E-mail").fill("ana@jobsync.test");
  await page.getByRole("button", { name: "Adicionar experiência" }).click();
  const experiencia = page.getByRole("group", { name: "Experiência 1" });
  await experiencia.getByLabel("Empresa").fill("Neoway");
  await experiencia.getByLabel("Cargo").fill("Desenvolvedora Python");
  await page.getByLabel("Tecnologias", { exact: true }).fill("Python, FastAPI");
  await page.getByRole("button", { name: "Salvar perfil" }).click();
  await expect(page.getByRole("status")).toHaveText("Perfil salvo.");

  await page.reload();
  await expect(page.getByLabel("Nome completo")).toHaveValue("Ana Lima");
  await expect(
    page.getByRole("group", { name: "Experiência 1" }).getByLabel("Empresa"),
  ).toHaveValue("Neoway");

  await page.getByRole("link", { name: /Visão geral/ }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(/, Ana$/);
  await expect(page.getByRole("heading", { name: "Complete seu currículo mestre" })).toBeHidden();
  await expect(
    page.getByRole("progressbar", { name: "Completude do currículo mestre" }),
  ).toHaveAttribute("aria-valuenow", "43");
});

test("ajustar para uma vaga, revisar, baixar o PDF, criar a candidatura e mover no Kanban", async ({
  page,
}) => {
  const perfil = novoPerfil("e2e-fluxo");
  await entrar(page, perfil);

  await page.getByRole("link", { name: /Meu perfil/ }).click();
  await page.getByLabel("Nome completo").fill("Bruno Costa");
  await page.getByLabel("E-mail").fill("bruno@jobsync.test");
  await page.getByRole("button", { name: "Adicionar experiência" }).click();
  const experiencia = page.getByRole("group", { name: "Experiência 1" });
  await experiencia.getByLabel("Empresa").fill("Olist");
  await experiencia.getByLabel("Cargo").fill("Backend");
  await experiencia.getByLabel("Descrição").fill("APIs em Python e FastAPI.");
  await page.getByRole("button", { name: "Salvar perfil" }).click();
  await expect(page.getByRole("status")).toHaveText("Perfil salvo.");

  await page.getByRole("link", { name: /Meus currículos/ }).click();
  await page.getByRole("button", { name: "Enviar currículo" }).click();
  const envio = page.getByRole("dialog", { name: "Enviar currículo" });
  await envio.getByLabel("Nome de referência").fill("CV Backend");
  await envio.getByLabel("Arquivo PDF").setInputFiles(PDF_MINIMO);
  await envio.getByRole("button", { name: "Enviar" }).click();
  await expect(page.getByText("CV Backend")).toBeVisible();

  await page.getByRole("link", { name: /Vagas salvas/ }).click();
  await page.getByRole("button", { name: "Colar vaga" }).click();
  const colar = page.getByRole("dialog", { name: "Colar vaga" });
  await colar
    .getByLabel("Descrição da vaga")
    .fill("Senior Python Engineer\nPython, FastAPI e Kafka.");
  await colar.getByRole("button", { name: "Salvar vaga" }).click();
  await page.getByRole("button", { name: "Detalhes da vaga Senior Python Engineer" }).click();
  await page.getByRole("button", { name: "Ajustar currículo" }).click();

  await expect(
    page.getByRole("heading", { level: 1, name: "Ajustar para uma vaga" }),
  ).toBeVisible();
  await page.getByLabel("Empresa").fill("Globex");
  await page.getByRole("button", { name: "Analisar vaga" }).click();
  await expect(page.getByRole("meter", { name: "Relevância" })).toHaveAttribute(
    "aria-valuenow",
    "85",
  );
  await page.getByRole("button", { name: "Gerar currículo adaptado" }).click();
  await expect(page.getByRole("heading", { name: "Revise o currículo adaptado" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Baixar PDF" })).toBeHidden();
  const revisada = page.getByRole("group", { name: "Experiência 1" });
  await expect(page.getByText(/A IA pode ter estimado métricas e volumes/)).toBeVisible();
  await expect(revisada.getByLabel("Conquistas")).toHaveValue("APIs em Python e FastAPI.");
  await expect(revisada.getByLabel("Contexto")).toHaveValue("Contexto de Olist.");
  await revisada.getByLabel("Conquistas").fill("APIs em Python, FastAPI e Kafka.");
  await page.getByRole("button", { name: "Confirmar e gerar PDF" }).click();
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: "Baixar PDF" }).click(),
  ]);
  expect(download.suggestedFilename()).toMatch(
    /^BrunoCosta-\d{4}-\d{2}-\d{2}-SeniorPythonEngineer-Globex\.pdf$/,
  );
  const conteudo = await readFile((await download.path())!);
  expect(conteudo.subarray(0, 5).toString()).toBe("%PDF-");
  await page.getByRole("button", { name: "Analisar aderência ATS" }).click();
  await expect(page.getByRole("region", { name: "Aderência ATS" })).toContainText("Kafka");

  await page.getByRole("link", { name: /Vagas salvas/ }).click();
  await page.getByRole("button", { name: "Criar candidatura para Senior Python Engineer" }).click();
  const candidatura = page.getByRole("dialog", { name: "Criar candidatura" });
  await candidatura.getByLabel("Empresa").fill("Globex");
  await candidatura.getByRole("button", { name: "Criar candidatura" }).click();
  await expect(page.getByText("Nenhuma vaga salva")).toBeVisible();

  await page.getByRole("link", { name: /Candidaturas/ }).click();
  await page.getByLabel("Mover Senior Python Engineer para").selectOption("ENTREVISTA");
  await expect(page.getByRole("region", { name: "Entrevista, 1 candidatura" })).toContainText(
    "Senior Python Engineer",
  );
  await page.reload();
  await expect(page.getByRole("region", { name: "Entrevista, 1 candidatura" })).toContainText(
    "Senior Python Engineer",
  );
});

test("confirmar candidatura na tela de ajuste: Aplicado no board, PDF no detalhe e vaga fora de Vagas salvas", async ({
  page,
  request,
}) => {
  const perfil = novoPerfil("e2e-confirmar");
  await semearPerfilCompleto(request, perfil);
  await entrar(page, perfil);
  await page.goto("/ajustar-vaga");
  await page.getByLabel("Título da vaga").fill("Staff Platform Engineer");
  await page.getByLabel("Empresa").fill("Initech");
  await page
    .getByLabel("Descrição da vaga")
    .fill("Staff Platform Engineer\nGo, Kubernetes e Kafka.");
  await page.getByRole("button", { name: "Gerar currículo adaptado" }).click();
  await expect(page.getByRole("heading", { name: "Revise o currículo adaptado" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Confirmar candidatura" })).toBeHidden();
  await page.getByRole("button", { name: "Confirmar e gerar PDF" }).click();
  await expect(page.getByRole("button", { name: "Baixar PDF" })).toBeVisible();

  await page.getByRole("button", { name: "Confirmar candidatura" }).click();

  const confirmacao = page.getByText("Candidatura confirmada em Aplicado.");
  await expect(confirmacao).toBeFocused();
  await expect(page.getByRole("button", { name: "Candidatura confirmada" })).toBeDisabled();

  await page.getByRole("link", { name: "Ver no board" }).click();
  await expect(page.getByRole("heading", { level: 1, name: "Candidaturas" })).toBeVisible();
  const aplicado = page.getByRole("region", { name: /^Aplicado/ });
  await expect(aplicado).toContainText("Staff Platform Engineer");
  await expect(aplicado).toContainText("Initech");

  await page.getByRole("button", { name: "Detalhes de Staff Platform Engineer" }).click();
  const detalhe = page.getByRole("dialog", { name: "Staff Platform Engineer" });
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    detalhe.getByRole("button", { name: "Baixar PDF do currículo usado" }).click(),
  ]);
  expect(download.suggestedFilename()).toMatch(/-StaffPlatformEngineer-Initech\.pdf$/);
  const conteudo = await readFile((await download.path())!);
  expect(conteudo.subarray(0, 5).toString()).toBe("%PDF-");
  await page.keyboard.press("Escape");

  await page.getByRole("link", { name: /Vagas salvas/ }).click();
  await expect(
    page.getByRole("button", { name: "Detalhes da vaga Platform Engineer", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Detalhes da vaga Staff Platform Engineer", exact: true }),
  ).toHaveCount(0);

  await page.getByRole("link", { name: /Meus currículos/ }).click();
  await expect(page.getByText(/-StaffPlatformEngineer-Initech\.pdf/)).toBeVisible();

  await page.getByRole("link", { name: /Candidaturas/ }).click();
  await page.reload();
  await expect(page.getByRole("region", { name: /^Aplicado/ })).toContainText(
    "Staff Platform Engineer",
  );
});

test("revisão do currículo adaptado: pede, aplica uma sugestão de IA e gera o PDF", async ({
  page,
  request,
}) => {
  const perfil = novoPerfil("e2e-sugestao-revisao");
  await semearPerfilCompleto(request, perfil);
  await entrar(page, perfil);
  await page.goto("/ajustar-vaga");
  await page.getByLabel("Título da vaga").fill("Senior Python Engineer");
  await page.getByLabel("Empresa").fill("Globex");
  await page.getByLabel("Descrição da vaga").fill("Python, FastAPI e Kafka.");
  await page.getByRole("button", { name: "Gerar currículo adaptado" }).click();
  await expect(page.getByRole("heading", { name: "Revise o currículo adaptado" })).toBeVisible();

  const experiencia = page.getByRole("group", { name: "Experiência 1" });
  await experiencia.getByLabel("Conquistas").fill("APIs em Python e Kafka.");
  await page.getByRole("button", { name: "Sugestões de IA para experiência 1" }).click();
  const sugestao = page.getByRole("region", { name: "Sugestão da IA para experiência 1" });
  await expect(sugestao).toContainText("- Sugestão com vaga: APIs em Python e Kafka.");
  await expect(sugestao).toContainText("Contexto: Sugestão com vaga: Contexto de Olist.");
  await expect(experiencia.getByLabel("Conquistas")).toHaveValue("APIs em Python e Kafka.");
  await page.getByRole("button", { name: "Aplicar sugestão em experiência 1" }).click();
  await expect(experiencia.getByLabel("Conquistas")).toHaveValue(
    "Sugestão com vaga: APIs em Python e Kafka.",
  );
  await expect(experiencia.getByLabel("Contexto")).toHaveValue(
    "Sugestão com vaga: Contexto de Olist.",
  );
  await expect(experiencia.getByLabel("Conquistas")).toBeFocused();

  const [download] = await Promise.all([
    page.waitForEvent("download"),
    (async () => {
      await page.getByRole("button", { name: "Confirmar e gerar PDF" }).click();
      await page.getByRole("button", { name: "Baixar PDF" }).click();
    })(),
  ]);
  expect(download.suggestedFilename()).toMatch(/-SeniorPythonEngineer-Globex\.pdf$/);
});

test("Meu perfil: sugestão de IA sem vaga altera o campo, mas não salva o perfil", async ({
  page,
  request,
}) => {
  const perfil = novoPerfil("e2e-sugestao-perfil");
  await semearPerfilCompleto(request, perfil);
  await entrar(page, perfil);
  await page.goto("/perfil");

  await page.getByRole("button", { name: "Sugestões de IA para resumo" }).click();
  await expect(page.getByRole("region", { name: "Sugestão da IA para resumo" })).toContainText(
    "Sugestão de escrita: Backend Python.",
  );
  await page.getByRole("button", { name: "Aplicar sugestão em resumo" }).click();
  await expect(page.getByLabel("Resumo profissional")).toHaveValue(
    "Sugestão de escrita: Backend Python.",
  );
  await expect(page.getByText("Alterações não salvas")).toBeVisible();

  await page.reload();
  await expect(page.getByLabel("Resumo profissional")).toHaveValue("Backend Python.");
});

test("revisão mostra a troca de tecnologia equivalente pedida pela vaga só na experiência mais recente", async ({
  page,
  request,
}) => {
  const perfil = novoPerfil("e2e-ajustes-tecnologia");
  await semearPerfilCompleto(request, perfil, EXPERIENCIAS_COM_REACT);
  await entrar(page, perfil);
  await page.goto("/ajustar-vaga");
  await page.getByLabel("Título da vaga").fill("Desenvolvedor Angular");
  await page.getByLabel("Empresa").fill("Globex");
  await page.getByLabel("Descrição da vaga").fill("Java e Angular.");
  await page.getByRole("button", { name: "Gerar currículo adaptado" }).click();
  await expect(page.getByRole("heading", { name: "Revise o currículo adaptado" })).toBeVisible();

  const ajustes = page.getByRole("list", { name: "Ajustes de tecnologia" });
  await expect(ajustes.getByRole("listitem")).toHaveCount(1);
  await expect(ajustes).toContainText("React → Angular em Front-end — Acme");
  await expect(
    page.getByRole("group", { name: "Experiência 1" }).getByLabel("Contexto"),
  ).toHaveValue("Contexto de Acme. Com Angular.");
  await expect(
    page.getByRole("group", { name: "Experiência 2" }).getByLabel("Contexto"),
  ).toHaveValue("Contexto de Initech.");
  await expect(page.getByText(/defender em entrevista/)).toBeVisible();
});

test("pedidos seguidos de sugestão na revisão mudam o foco da IA", async ({ page, request }) => {
  const perfil = novoPerfil("e2e-refino");
  await semearPerfilCompleto(request, perfil);
  await entrar(page, perfil);
  await page.goto("/ajustar-vaga");
  await page.getByLabel("Título da vaga").fill("Senior Python Engineer");
  await page.getByLabel("Empresa").fill("Globex");
  await page.getByLabel("Descrição da vaga").fill("Python, FastAPI e Kafka.");
  await page.getByRole("button", { name: "Gerar currículo adaptado" }).click();
  await expect(page.getByRole("heading", { name: "Revise o currículo adaptado" })).toBeVisible();
  const sugestao = page.getByRole("region", { name: "Sugestão da IA para resumo" });

  await page.getByRole("button", { name: "Sugestões de IA para resumo" }).click();
  await expect(sugestao).toContainText("Foco: aderência à vaga");
  await page.getByRole("button", { name: "Descartar sugestão de resumo" }).click();
  await page.getByRole("button", { name: "Sugestões de IA para resumo" }).click();

  await expect(sugestao).toContainText("Foco: impacto e resultados");
});
