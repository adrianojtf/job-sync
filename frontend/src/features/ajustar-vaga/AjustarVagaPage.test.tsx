import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { AVALIACAO_VAGA, CURRICULO_SALVO, dimensao, servirDadosBase } from "../../test/fixtures";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

const ADAPTADO = {
  nome_arquivo: "AdrianoTeixeira-2026-11-06-SeniorJava-Olist.pdf",
  pdf_base64: btoa("%PDF-adaptado"),
  nome_completo: "Adriano Teixeira",
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
    http.post(`${API_TESTE}/v1/curriculos/:id/adaptacoes`, async (info) => {
      await registrar(`adaptacoes:${info.params.id}`)(info);
      return HttpResponse.json(ADAPTADO);
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

  it("gera com o perfil estruturado, baixa o PDF e mostra as avaliações das experiências", async () => {
    servirDadosBase();
    const chamadas = servirIa();
    const downloads = capturarDownloads();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await preencherVaga();
    await userEvent.selectOptions(screen.getByLabelText("Idioma do currículo"), "en");

    await userEvent.click(screen.getByRole("button", { name: "Gerar currículo adaptado" }));

    expect(await screen.findByText(ADAPTADO.nome_arquivo)).toBeInTheDocument();
    expect(chamadas.find((c) => c.rota.startsWith("adaptacoes"))?.corpo).toMatchObject({
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

    expect(downloads).toEqual([ADAPTADO.nome_arquivo]);
  });

  it("gera a partir de um currículo da biblioteca enviando o PDF", async () => {
    servirDadosBase();
    const chamadas = servirIa();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await preencherVaga();
    await userEvent.selectOptions(screen.getByLabelText("Currículo base"), CURRICULO_SALVO.id);

    await userEvent.click(screen.getByRole("button", { name: "Gerar currículo adaptado" }));

    await screen.findByText(ADAPTADO.nome_arquivo);
    const adaptacao = chamadas.find((c) => c.rota.startsWith("adaptacoes"))!;
    expect(adaptacao.rota).toBe("adaptacoes:c1");
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
      http.post(`${API_TESTE}/v1/curriculos/:id/adaptacoes`, () =>
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
      http.post(`${API_TESTE}/v1/curriculos/:id/adaptacoes`, () =>
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
