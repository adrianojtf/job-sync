import { cleanup, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { delay, http, HttpResponse } from "msw";
import {
  AVALIACAO_VAGA,
  CANDIDATURA,
  CURRICULO_SALVO,
  dimensao,
  servirDadosBase,
} from "../../test/fixtures";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

const PDF_REVISADO = {
  nome_arquivo: "AdrianoTeixeira-2026-11-06-SeniorJava-Olist.pdf",
  pdf_base64: btoa("%PDF-adaptado"),
};

const RASCUNHO = {
  nome_completo: "Adriano Teixeira",
  email: "adriano@email.com",
  linkedin: "",
  secoes: [
    { tipo: "PERFIL", titulo: "Perfil", conteudo: "Resumo adaptado pela IA." },
    { tipo: "TECNOLOGIAS", titulo: "Tecnologias", conteudo: "Linguagens: Java" },
  ],
  experiencias: [
    {
      cargo: "Dev Java",
      empresa: "Neoway",
      periodo: "2020-2024",
      conquistas: ["APIs em Java."],
      contexto: "Empresa de dados.",
    },
  ],
  titulo_experiencias: "Experiências",
};

const ANALISE_VAGA = {
  requisitos: [
    { nome: "Java", categoria: "TECNOLOGIA", tipo: "EXPLICITO", origem: "DESCRICAO_VAGA" },
  ],
  ambiguidade: [],
  texto_original: "Java, Kafka e AWS.",
};

const ADAPTADO = {
  rascunho: RASCUNHO,
  analise_vaga: ANALISE_VAGA,
  avaliacao_vaga: AVALIACAO_VAGA,
  status_avaliacao_vaga: "avaliada",
  avaliacoes_experiencias: [
    {
      experiencia: {
        cargo: "Dev Java",
        empresa: "Neoway",
        periodo: "2020-2024",
        descricao: "APIs em Java e Kafka.",
      },
      status: "avaliada",
      avaliacao: {
        score: 81,
        clareza_escrita: dimensao(80),
        qualidade_detalhe: dimensao(75),
        aderencia_vaga: dimensao(90),
        consistencia_textual: dimensao(79),
      },
    },
    {
      experiencia: { cargo: "Estagiário", empresa: "UFSC", periodo: "2019", descricao: "Suporte." },
      status: "indisponivel",
      avaliacao: null,
    },
  ],
};

function servirIa() {
  const chamadas: { rota: string; corpo: Record<string, unknown> }[] = [];
  const registrar =
    (rota: string) =>
    async ({ request }: { request: Request }) => {
      chamadas.push({ rota, corpo: (await request.json()) as Record<string, unknown> });
    };
  servidorApi.use(
    http.post(`${API_TESTE}/v1/vagas/avaliacoes`, async (info) => {
      await registrar("avaliacoes")(info);
      return HttpResponse.json(AVALIACAO_VAGA);
    }),
    http.post(`${API_TESTE}/v1/curriculos/:id/rascunhos-adaptados`, async (info) => {
      await registrar(`rascunhos:${info.params.id}`)(info);
      return HttpResponse.json(ADAPTADO);
    }),
    http.post(`${API_TESTE}/v1/secoes-curriculo/sugestoes`, async (info) => {
      await registrar("sugestao-secao")(info);
      return HttpResponse.json({ conteudo_sugerido: "Resumo sugerido.", foco: "aderencia_vaga" });
    }),
    http.post(`${API_TESTE}/v1/curriculos-revisados`, async (info) => {
      await registrar("pdf")(info);
      return HttpResponse.json(PDF_REVISADO);
    }),
    http.post(`${API_TESTE}/v1/curriculos/:id/analises-ats`, async (info) => {
      await registrar("ats")(info);
      return HttpResponse.json({
        nome_completo: "Adriano Teixeira",
        nota: 67,
        requisitos_faltantes: [{ nome: "Kafka", categoria: "TECNOLOGIA", tipo: "EXPLICITO" }],
        sugestoes: ["Cite Kafka nas experiências em que foi usado."],
      });
    }),
    http.post(`${API_TESTE}/v1/cartas-apresentacao`, async (info) => {
      await registrar("carta")(info);
      return HttpResponse.json({ carta: "Prezados recrutadores, ..." });
    }),
  );
  return chamadas;
}

async function preencherVaga() {
  await userEvent.type(await screen.findByLabelText("Título da vaga"), "Senior Java");
  await userEvent.type(screen.getByLabelText("Empresa"), "Olist");
  await userEvent.type(screen.getByLabelText("Descrição da vaga"), "Java, Kafka e AWS.");
}

async function confirmarRevisao() {
  await screen.findByRole("heading", { name: "Revise o currículo adaptado" });
  await userEvent.click(screen.getByRole("button", { name: "Confirmar e gerar PDF" }));
}

function capturarDownloads() {
  const nomes: string[] = [];
  Object.assign(URL, { createObjectURL: vi.fn(() => "blob:x"), revokeObjectURL: vi.fn() });
  vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (
    this: HTMLAnchorElement,
  ) {
    nomes.push(this.download);
  });
  return nomes;
}

afterEach(() => vi.restoreAllMocks());

describe("Ajustar para uma vaga — modal do protótipo", () => {
  it("abre pela barra superior, valida e leva à tela já analisando a vaga", async () => {
    servirDadosBase();
    const chamadas = servirIa();
    renderizarApp({ caminho: "/", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("button", { name: "Ajustar para uma vaga" }));
    const modal = screen.getByRole("dialog", { name: "Ajustar currículo para uma vaga" });
    await userEvent.click(within(modal).getByRole("button", { name: "Analisar vaga" }));

    expect(within(modal).getByLabelText("Título da vaga")).toHaveAccessibleDescription(
      "Informe o título da vaga.",
    );
    expect(within(modal).getByLabelText("Descrição da vaga")).toHaveAccessibleDescription(
      "Cole a descrição da vaga.",
    );

    await userEvent.type(within(modal).getByLabelText("Título da vaga"), "Senior Java");
    await userEvent.type(within(modal).getByLabelText("Empresa"), "Olist");
    await userEvent.type(within(modal).getByLabelText("Descrição da vaga"), "Java e Kafka.");
    await userEvent.click(within(modal).getByRole("button", { name: "Analisar vaga" }));

    expect(
      await screen.findByRole("heading", { level: 1, name: "Ajustar para uma vaga" }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Título da vaga")).toHaveValue("Senior Java");
    expect(screen.getByLabelText("Empresa")).toHaveValue("Olist");
    expect(await screen.findByRole("meter", { name: "Relevância" })).toHaveAttribute(
      "aria-valuenow",
      "85",
    );
    expect(chamadas.filter((c) => c.rota === "avaliacoes")).toHaveLength(1);
  });
});

describe("Ajustar para uma vaga — análise automática só uma vez", () => {
  it("recarregar a página depois da análise não chama a IA de novo", async () => {
    servirDadosBase();
    const chamadas = servirIa();
    const { router } = renderizarApp({ caminho: "/", perfil: "adriano" });
    await userEvent.click(await screen.findByRole("button", { name: "Ajustar para uma vaga" }));
    const modal = screen.getByRole("dialog", { name: "Ajustar currículo para uma vaga" });
    await userEvent.type(within(modal).getByLabelText("Título da vaga"), "Senior Java");
    await userEvent.type(within(modal).getByLabelText("Descrição da vaga"), "Java e Kafka.");
    await userEvent.click(within(modal).getByRole("button", { name: "Analisar vaga" }));
    await screen.findByRole("meter", { name: "Relevância" });
    const entradaAtual = router.state.location;

    cleanup();
    renderizarApp({
      caminho: entradaAtual.pathname,
      estado: entradaAtual.state,
      perfil: "adriano",
    });

    expect(await screen.findByLabelText("Título da vaga")).toHaveValue("Senior Java");
    await new Promise((resolver) => setTimeout(resolver, 50));
    expect(chamadas.filter((chamada) => chamada.rota === "avaliacoes")).toHaveLength(1);
    expect(screen.queryByRole("meter")).not.toBeInTheDocument();
  });

  it("consumir a instrução não remonta a tela nem apaga o resultado", async () => {
    servirDadosBase();
    servirIa();
    const { router } = renderizarApp({
      caminho: "/ajustar-vaga",
      estado: { cargo: "Backend", descricao: "Vaga.", analisarAoAbrir: true, pedido: 1 },
      perfil: "adriano",
    });

    await screen.findByRole("meter", { name: "Relevância" });

    await waitFor(() =>
      expect(router.state.location.state).toMatchObject({
        analisarAoAbrir: false,
        pedido: 1,
        cargo: "Backend",
      }),
    );
    expect(screen.getByRole("meter", { name: "Relevância" })).toBeInTheDocument();
    expect(router.state.historyAction).toBe("REPLACE");
  });
});

describe("AjustarVagaPage", () => {
  it("sem perfil e sem currículos orienta a criar uma fonte de currículo", async () => {
    servirDadosBase({ perfil: null, curriculos: [] });

    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });

    expect(await screen.findByText(/Você ainda não tem um currículo base/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "preencha o currículo mestre" })).toHaveAttribute(
      "href",
      "/perfil",
    );
    expect(screen.getByRole("link", { name: "envie um PDF" })).toHaveAttribute(
      "href",
      "/curriculos",
    );
    expect(screen.getByRole("button", { name: "Gerar currículo adaptado" })).toBeDisabled();
  });

  it("gera com o perfil estruturado, revisa, baixa o PDF e mostra as avaliações das experiências", async () => {
    servirDadosBase();
    const chamadas = servirIa();
    const downloads = capturarDownloads();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await preencherVaga();
    await userEvent.selectOptions(screen.getByLabelText("Idioma do currículo"), "en");

    await userEvent.click(screen.getByRole("button", { name: "Gerar currículo adaptado" }));

    await screen.findByRole("heading", { name: "Revise o currículo adaptado" });
    expect(screen.queryByRole("button", { name: "Baixar PDF" })).not.toBeInTheDocument();
    expect(chamadas.map((c) => c.rota)).not.toContain("pdf");
    await userEvent.clear(screen.getByLabelText("Resumo profissional"));
    await userEvent.type(screen.getByLabelText("Resumo profissional"), "Resumo revisado.");
    await confirmarRevisao();

    expect(await screen.findByText(PDF_REVISADO.nome_arquivo)).toBeInTheDocument();
    expect(chamadas.find((c) => c.rota === "pdf")?.corpo).toEqual({
      rascunho: {
        ...RASCUNHO,
        secoes: [
          { tipo: "PERFIL", titulo: "Perfil", conteudo: "Resumo revisado." },
          { tipo: "TECNOLOGIAS", titulo: "Tecnologias", conteudo: "Linguagens: Java" },
        ],
      },
      idioma_alvo: "en",
      cargo_alvo: "Senior Java",
      empresa_alvo: "Olist",
    });
    expect(chamadas.find((c) => c.rota.startsWith("rascunhos"))?.corpo).toMatchObject({
      descricao_vaga: "Java, Kafka e AWS.",
      cargo_alvo: "Senior Java",
      empresa_alvo: "Olist",
      idioma_alvo: "en",
      perfil_identificador: "adriano",
    });
    const experiencias = screen.getByRole("region", { name: "Avaliação das experiências" });
    expect(within(experiencias).getByText(/Dev Java · Neoway/)).toBeInTheDocument();
    expect(
      within(experiencias).getByText("Avaliação indisponível para esta experiência."),
    ).toBeInTheDocument();
    expect(screen.getByRole("meter", { name: "Completude" })).toHaveAttribute(
      "aria-valuenow",
      "75",
    );

    await userEvent.click(screen.getByRole("button", { name: "Baixar PDF" }));

    expect(downloads).toEqual([PDF_REVISADO.nome_arquivo]);
  });

  it("gera a partir de um currículo da biblioteca enviando o PDF", async () => {
    servirDadosBase();
    const chamadas = servirIa();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await preencherVaga();
    await userEvent.selectOptions(screen.getByLabelText("Currículo base"), CURRICULO_SALVO.id);

    await userEvent.click(screen.getByRole("button", { name: "Gerar currículo adaptado" }));

    await screen.findByRole("heading", { name: "Revise o currículo adaptado" });
    const adaptacao = chamadas.find((c) => c.rota.startsWith("rascunhos"))!;
    expect(adaptacao.rota).toBe("rascunhos:c1");
    expect(atob(adaptacao.corpo.pdf_base64 as string)).toBe("%PDF-biblioteca");
    expect(adaptacao.corpo.perfil_identificador).toBeUndefined();
  });

  it("exige título, empresa e descrição para gerar", async () => {
    servirDadosBase();
    const chamadas = servirIa();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("button", { name: "Gerar currículo adaptado" }));

    expect(screen.getByLabelText("Empresa")).toHaveAccessibleDescription(/Informe a empresa/);
    expect(chamadas).toHaveLength(0);
  });

  it("avisa quando a avaliação da vaga ficou indisponível, sem bloquear o resultado", async () => {
    servirDadosBase();
    servirIa();
    servidorApi.use(
      http.post(`${API_TESTE}/v1/curriculos/:id/rascunhos-adaptados`, () =>
        HttpResponse.json({
          ...ADAPTADO,
          avaliacao_vaga: null,
          status_avaliacao_vaga: "indisponivel",
        }),
      ),
    );
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await preencherVaga();

    await userEvent.click(screen.getByRole("button", { name: "Gerar currículo adaptado" }));
    await confirmarRevisao();

    expect(
      await screen.findByText(/A avaliação automática da vaga não está disponível agora/),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Baixar PDF" })).toBeInTheDocument();
  });

  it("analisa a aderência ATS com requisitos faltantes e sugestões", async () => {
    servirDadosBase();
    const chamadas = servirIa();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await preencherVaga();

    await userEvent.click(screen.getByRole("button", { name: "Analisar aderência ATS" }));

    const ats = await screen.findByRole("region", { name: "Aderência ATS" });
    expect(await within(ats).findByText("67")).toBeInTheDocument();
    expect(within(ats).getByText("Kafka")).toBeInTheDocument();
    expect(
      within(ats).getByText("Cite Kafka nas experiências em que foi usado."),
    ).toBeInTheDocument();
    expect(chamadas.find((c) => c.rota === "ats")?.corpo).toEqual({
      descricao_vaga: "Java, Kafka e AWS.",
      perfil_identificador: "adriano",
    });
  });

  it("gera a carta e permite copiar e baixar", async () => {
    servirDadosBase();
    servirIa();
    const escrever = vi.fn(() => Promise.resolve());
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: escrever },
      configurable: true,
    });
    const downloads = capturarDownloads();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await preencherVaga();

    await userEvent.click(screen.getByRole("button", { name: "Gerar carta de apresentação" }));

    expect(await screen.findByLabelText("Texto da carta")).toHaveValue(
      "Prezados recrutadores, ...",
    );
    await userEvent.click(screen.getByRole("button", { name: "Copiar carta" }));
    expect(escrever).toHaveBeenCalledWith("Prezados recrutadores, ...");
    expect(await screen.findByRole("status")).toHaveTextContent("Carta copiada.");
    await userEvent.click(screen.getByRole("button", { name: "Baixar carta" }));
    expect(downloads).toEqual(["carta-apresentacao-senior-java-olist.txt"]);
  });

  it("mostra o erro da geração e mantém os dados digitados", async () => {
    servirDadosBase();
    servidorApi.use(
      http.post(`${API_TESTE}/v1/curriculos/:id/rascunhos-adaptados`, () =>
        HttpResponse.json(
          {
            type: "t",
            title: "Erro",
            status: 422,
            detail: "A empresa alvo é obrigatória.",
            instance: "i",
          },
          { status: 422 },
        ),
      ),
    );
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await preencherVaga();

    await userEvent.click(screen.getByRole("button", { name: "Gerar currículo adaptado" }));

    expect(await screen.findByText("A empresa alvo é obrigatória.")).toBeInTheDocument();
    expect(screen.getByLabelText("Título da vaga")).toHaveValue("Senior Java");
  });

  it("voltar da revisão descarta o rascunho e mantém os dados da vaga", async () => {
    servirDadosBase();
    const chamadas = servirIa();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await preencherVaga();
    await userEvent.click(screen.getByRole("button", { name: "Gerar currículo adaptado" }));
    await screen.findByRole("heading", { name: "Revise o currículo adaptado" });

    await userEvent.click(screen.getByRole("button", { name: "Voltar para a vaga" }));

    expect(screen.getByLabelText("Título da vaga")).toHaveValue("Senior Java");
    expect(screen.queryByRole("button", { name: "Baixar PDF" })).not.toBeInTheDocument();
    expect(chamadas.map((c) => c.rota)).not.toContain("pdf");
  });

  it("as sugestões da revisão usam a vaga adaptada e a análise devolvida com o rascunho", async () => {
    servirDadosBase();
    const chamadas = servirIa();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await preencherVaga();
    await userEvent.click(screen.getByRole("button", { name: "Gerar currículo adaptado" }));
    await screen.findByRole("heading", { name: "Revise o currículo adaptado" });

    await userEvent.click(screen.getByRole("button", { name: "Sugestões de IA para resumo" }));
    await userEvent.click(
      await screen.findByRole("button", { name: "Aplicar sugestão em resumo" }),
    );

    expect(chamadas.find((c) => c.rota === "sugestao-secao")?.corpo).toEqual({
      secao: { tipo: "PERFIL", titulo: "Perfil", conteudo: "Resumo adaptado pela IA." },
      contexto_vaga: {
        descricao_vaga: "Java, Kafka e AWS.",
        idioma_alvo: "pt",
        analise_vaga: ANALISE_VAGA,
        cargo_alvo: "Senior Java",
      },
      refino: { tentativa: 1, sugestoes_anteriores: [] },
    });
    expect(screen.getByLabelText("Resumo profissional")).toHaveValue("Resumo sugerido.");
  });

  it("falha ao gerar o PDF mantém a revisão com as edições", async () => {
    servirDadosBase();
    servirIa();
    servidorApi.use(
      http.post(`${API_TESTE}/v1/curriculos-revisados`, () =>
        HttpResponse.json(
          { type: "t", title: "Erro", status: 422, detail: "Rascunho inválido.", instance: "i" },
          { status: 422 },
        ),
      ),
    );
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await preencherVaga();
    await userEvent.click(screen.getByRole("button", { name: "Gerar currículo adaptado" }));
    await screen.findByRole("heading", { name: "Revise o currículo adaptado" });
    await userEvent.type(screen.getByLabelText("Resumo profissional"), " Editado.");

    await userEvent.click(screen.getByRole("button", { name: "Confirmar e gerar PDF" }));

    expect(await screen.findByText(/Rascunho inválido\./)).toBeInTheDocument();
    expect(screen.getByLabelText("Resumo profissional")).toHaveValue(
      "Resumo adaptado pela IA. Editado.",
    );
  });

  it("aceita dados pré-preenchidos pela navegação", async () => {
    servirDadosBase();
    servirIa();
    const { router } = renderizarApp({ caminho: "/", perfil: "adriano" });
    await screen.findByRole("heading", { level: 1 });

    await router.navigate("/ajustar-vaga", {
      state: { cargo: "Backend", empresa: "Neoway", descricao: "Vaga de backend." },
    });

    expect(await screen.findByLabelText("Título da vaga")).toHaveValue("Backend");
    expect(screen.getByLabelText("Descrição da vaga")).toHaveValue("Vaga de backend.");
    await waitFor(() => expect(screen.queryByRole("meter")).not.toBeInTheDocument());
  });
});

describe("Ajustar para uma vaga — confirmar candidatura", () => {
  const ROTULO = "Confirmar candidatura";
  const BIBLIOTECA_CHEIA =
    "Sua biblioteca de currículos está cheia. Remova um currículo para confirmar a candidatura.";

  function servirConfirmacao(
    resposta: () => Response | Promise<Response> = () =>
      HttpResponse.json(CANDIDATURA, { status: 201 }),
  ) {
    const corpos: Record<string, unknown>[] = [];
    servidorApi.use(
      http.post(`${API_TESTE}/v1/candidaturas-ajustadas`, async ({ request }) => {
        corpos.push((await request.json()) as Record<string, unknown>);
        return resposta();
      }),
    );
    return corpos;
  }

  async function gerarPdfDaVaga() {
    const app = renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await preencherVaga();
    await userEvent.click(screen.getByRole("button", { name: "Gerar currículo adaptado" }));
    await confirmarRevisao();
    await screen.findByText(PDF_REVISADO.nome_arquivo);
    return app;
  }

  const problema = (status: number, detail: string) =>
    HttpResponse.json({ type: "t", title: "Erro", status, detail, instance: "i" }, { status });

  it("o botão só aparece depois de o PDF ser gerado", async () => {
    servirDadosBase();
    servirIa();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await preencherVaga();
    expect(screen.queryByRole("button", { name: ROTULO })).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Gerar currículo adaptado" }));
    await screen.findByRole("heading", { name: "Revise o currículo adaptado" });
    expect(screen.queryByRole("button", { name: ROTULO })).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Confirmar e gerar PDF" }));

    expect(await screen.findByRole("button", { name: ROTULO })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Baixar PDF" })).toBeInTheDocument();
  });

  it("envia a vaga e o PDF gerado ao confirmar", async () => {
    servirDadosBase();
    servirIa();
    const corpos = servirConfirmacao();
    await gerarPdfDaVaga();

    await userEvent.click(screen.getByRole("button", { name: ROTULO }));

    await screen.findByText("Candidatura confirmada em Aplicado.");
    expect(corpos).toEqual([
      {
        perfil_identificador: "adriano",
        cargo: "Senior Java",
        empresa: "Olist",
        descricao_vaga: "Java, Kafka e AWS.",
        nome_arquivo: PDF_REVISADO.nome_arquivo,
        pdf_base64: PDF_REVISADO.pdf_base64,
      },
    ]);
  });

  it("envia a vaga do PDF gerado, não o que foi editado no formulário depois", async () => {
    servirDadosBase();
    servirIa();
    const corpos = servirConfirmacao();
    await gerarPdfDaVaga();
    await userEvent.clear(screen.getByLabelText("Título da vaga"));
    await userEvent.type(screen.getByLabelText("Título da vaga"), "Outro cargo");
    await userEvent.clear(screen.getByLabelText("Empresa"));
    await userEvent.type(screen.getByLabelText("Empresa"), "Outra empresa");

    await userEvent.click(screen.getByRole("button", { name: ROTULO }));

    await screen.findByText("Candidatura confirmada em Aplicado.");
    expect(corpos[0]).toMatchObject({ cargo: "Senior Java", empresa: "Olist" });
  });

  it("enquanto envia, indica o andamento e não permite um segundo clique", async () => {
    servirDadosBase();
    servirIa();
    const corpos = servirConfirmacao(async () => {
      await delay(150);
      return HttpResponse.json(CANDIDATURA, { status: 201 });
    });
    await gerarPdfDaVaga();

    await userEvent.click(screen.getByRole("button", { name: ROTULO }));
    const enviando = await screen.findByRole("button", { name: "Confirmando candidatura…" });
    await userEvent.click(enviando);

    expect(enviando).toHaveAttribute("aria-busy", "true");
    await screen.findByText("Candidatura confirmada em Aplicado.");
    expect(corpos).toHaveLength(1);
  });

  it("em caso de sucesso mostra a confirmação com o link do board e desabilita o botão", async () => {
    servirDadosBase();
    servirIa();
    const corpos = servirConfirmacao();
    await gerarPdfDaVaga();

    await userEvent.click(screen.getByRole("button", { name: ROTULO }));

    const mensagem = await screen.findByText("Candidatura confirmada em Aplicado.");
    expect(mensagem).toHaveAttribute("role", "status");
    expect(screen.getByRole("link", { name: "Ver no board" })).toHaveAttribute(
      "href",
      "/candidaturas",
    );
    const confirmado = screen.getByRole("button", { name: "Candidatura confirmada" });
    expect(confirmado).toBeDisabled();
    await userEvent.click(confirmado);
    expect(corpos).toHaveLength(1);
  });

  it("leva o foco para a confirmação quando o botão fica desabilitado", async () => {
    servirDadosBase();
    servirIa();
    servirConfirmacao();
    await gerarPdfDaVaga();

    await userEvent.click(screen.getByRole("button", { name: ROTULO }));

    expect(await screen.findByText("Candidatura confirmada em Aplicado.")).toHaveFocus();
  });

  it("biblioteca cheia mostra o aviso do servidor e permite tentar de novo", async () => {
    servirDadosBase();
    servirIa();
    servirConfirmacao(() => problema(409, BIBLIOTECA_CHEIA));
    await gerarPdfDaVaga();

    await userEvent.click(screen.getByRole("button", { name: ROTULO }));

    const aviso = await screen.findByText(BIBLIOTECA_CHEIA);
    expect(aviso.parentElement).toHaveAttribute("role", "alert");
    expect(screen.getByRole("button", { name: ROTULO })).toBeEnabled();
    expect(screen.queryByText("Candidatura confirmada em Aplicado.")).not.toBeInTheDocument();
  });

  it("outro erro mostra a mensagem e a nova tentativa funciona", async () => {
    servirDadosBase();
    servirIa();
    let tentativa = 0;
    servirConfirmacao(() =>
      ++tentativa === 1
        ? problema(500, "Falha ao gravar a candidatura.")
        : HttpResponse.json(CANDIDATURA, { status: 201 }),
    );
    await gerarPdfDaVaga();

    await userEvent.click(screen.getByRole("button", { name: ROTULO }));
    const aviso = await screen.findByText("Falha ao gravar a candidatura.");
    expect(aviso.parentElement).toHaveAttribute("role", "alert");
    await userEvent.click(screen.getByRole("button", { name: ROTULO }));

    expect(await screen.findByText("Candidatura confirmada em Aplicado.")).toBeInTheDocument();
    expect(screen.queryByText("Falha ao gravar a candidatura.")).not.toBeInTheDocument();
  });

  it("gerar um novo PDF depois de confirmar volta o botão ao estado inicial", async () => {
    servirDadosBase();
    servirIa();
    const corpos = servirConfirmacao();
    await gerarPdfDaVaga();
    await userEvent.click(screen.getByRole("button", { name: ROTULO }));
    await screen.findByText("Candidatura confirmada em Aplicado.");

    await userEvent.click(screen.getByRole("button", { name: "Gerar currículo adaptado" }));
    await confirmarRevisao();
    await screen.findByText(PDF_REVISADO.nome_arquivo);

    expect(screen.queryByText("Candidatura confirmada em Aplicado.")).not.toBeInTheDocument();
    const reiniciado = screen.getByRole("button", { name: ROTULO });
    expect(reiniciado).toBeEnabled();
    await userEvent.click(reiniciado);
    await screen.findByText("Candidatura confirmada em Aplicado.");
    expect(corpos).toHaveLength(2);
  });

  it("atualiza as listas de candidaturas, currículos e vagas do perfil", async () => {
    servirDadosBase();
    servirIa();
    servirConfirmacao();
    const { queryClient } = await gerarPdfDaVaga();
    const invalidar = vi.spyOn(queryClient, "invalidateQueries");

    await userEvent.click(screen.getByRole("button", { name: ROTULO }));
    await screen.findByText("Candidatura confirmada em Aplicado.");

    const chaves = invalidar.mock.calls.map(([filtro]) => filtro?.queryKey);
    expect(chaves).toEqual(
      expect.arrayContaining([
        ["candidaturas", "adriano"],
        ["curriculos", "adriano"],
        ["vagas", "adriano"],
      ]),
    );
  });
});
