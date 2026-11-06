import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { servirDadosBase } from "../../test/fixtures";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

const VAGAS = [
  {
    titulo: "Python Developer",
    empresa: "Acme",
    descricao: "Python e Django.",
    url: "https://remoteok.com/1",
    fonte: "REMOTEOK",
    data_publicacao: "2026-11-03",
    nota: 61,
    requisitos_faltantes: [{ nome: "Django" }],
  },
  {
    titulo: "Senior Backend Engineer",
    empresa: "Globex",
    descricao: "Python, FastAPI e Kafka.",
    url: "https://weworkremotely.com/2",
    fonte: "WE_WORK_REMOTELY",
    data_publicacao: null,
    nota: 88,
    requisitos_faltantes: [],
  },
];

function servirDescoberta(vagas = VAGAS, base?: Parameters<typeof servirDadosBase>[0]) {
  const corpos: { rota: string; corpo: Record<string, unknown> }[] = [];
  servirDadosBase(base);
  servidorApi.use(
    http.post(`${API_TESTE}/v1/vagas/descobrir`, async ({ request }) => {
      corpos.push({ rota: "descobrir", corpo: (await request.json()) as Record<string, unknown> });
      return HttpResponse.json({ items: vagas, total: vagas.length });
    }),
    http.post(`${API_TESTE}/v1/vagas/descobertas/candidaturas`, async ({ request }) => {
      corpos.push({ rota: "candidatar", corpo: (await request.json()) as Record<string, unknown> });
      return HttpResponse.json({
        nome_arquivo: "AdrianoTeixeira-2026-11-06-SeniorBackendEngineer-Globex.pdf",
        pdf_base64: btoa("%PDF-candidatura"),
        nota: 74,
        requisitos_faltantes: [{ nome: "Kafka", categoria: "TECNOLOGIA", tipo: "EXPLICITO" }],
        carta: "Prezada equipe da Globex, ...",
        url_vaga: "https://weworkremotely.com/2",
      });
    }),
  );
  return corpos;
}

async function buscar(termo = "python backend") {
  await userEvent.type(await screen.findByLabelText("Termo de busca"), termo);
  await userEvent.click(screen.getByRole("button", { name: "Buscar vagas" }));
}

describe("DescobrirVagasPage", () => {
  it("busca com o currículo de referência e o período e ordena pela nota", async () => {
    const corpos = servirDescoberta();
    renderizarApp({ caminho: "/descobrir-vagas", perfil: "adriano" });
    await userEvent.selectOptions(await screen.findByLabelText("Publicadas nos últimos"), "7");

    await buscar();

    expect(await screen.findByRole("heading", { name: "2 vagas encontradas" })).toBeInTheDocument();
    const titulos = screen
      .getAllByRole("article")
      .map((artigo) => within(artigo).getByRole("heading").textContent);
    expect(titulos).toEqual(["Senior Backend Engineer", "Python Developer"]);
    const primeira = screen.getByRole("article", { name: "Senior Backend Engineer" });
    expect(
      within(primeira).getByText("Globex · We Work Remotely · Data de publicação desconhecida"),
    ).toBeInTheDocument();
    expect(within(primeira).getByText("88")).toBeInTheDocument();
    expect(
      within(primeira).getByText("Todos os requisitos explícitos foram encontrados."),
    ).toBeInTheDocument();
    const segunda = screen.getByRole("article", { name: "Python Developer" });
    expect(
      within(segunda).getByText("Acme · RemoteOK · Publicada em 03/11/2026"),
    ).toBeInTheDocument();
    expect(within(segunda).getByText("Django")).toBeInTheDocument();
    expect(
      within(segunda).getByRole("link", { name: "Ver vaga Python Developer na fonte" }),
    ).toHaveAttribute("href", "https://remoteok.com/1");
    expect(corpos[0]).toEqual({
      rota: "descobrir",
      corpo: { termo: "python backend", pdf_base64: btoa("%PDF-biblioteca"), dias_maximo: 7 },
    });
  });

  it("exige o termo de busca", async () => {
    const corpos = servirDescoberta();
    renderizarApp({ caminho: "/descobrir-vagas", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("button", { name: "Buscar vagas" }));

    expect(screen.getByLabelText("Termo de busca")).toHaveAccessibleDescription(
      "Informe um termo de busca.",
    );
    expect(corpos).toHaveLength(0);
  });

  it("sem currículos na biblioteca, explica que a nota precisa de um currículo de referência", async () => {
    servirDescoberta(VAGAS, { curriculos: [] });

    renderizarApp({ caminho: "/descobrir-vagas", perfil: "adriano" });

    expect(
      await screen.findByText(
        /A nota de compatibilidade compara cada vaga com um currículo em PDF/,
      ),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "envie um currículo" })).toHaveAttribute(
      "href",
      "/curriculos",
    );
    expect(screen.getByRole("button", { name: "Buscar vagas" })).toBeDisabled();
  });

  it("mostra quando nada foi encontrado", async () => {
    servirDescoberta([]);
    renderizarApp({ caminho: "/descobrir-vagas", perfil: "adriano" });

    await buscar();

    expect(await screen.findByText(/Nenhuma vaga encontrada/)).toBeInTheDocument();
  });

  it("candidata com o currículo mestre e entrega PDF, carta e link da vaga", async () => {
    const corpos = servirDescoberta();
    const downloads: string[] = [];
    Object.assign(URL, { createObjectURL: vi.fn(() => "blob:x"), revokeObjectURL: vi.fn() });
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (
      this: HTMLAnchorElement,
    ) {
      downloads.push(this.download);
    });
    renderizarApp({ caminho: "/descobrir-vagas", perfil: "adriano" });
    await userEvent.selectOptions(await screen.findByLabelText("Idioma da candidatura"), "en");
    await buscar();

    await userEvent.click(
      await screen.findByRole("button", { name: "Candidatar em Senior Backend Engineer" }),
    );

    const artigo = screen.getByRole("article", { name: "Senior Backend Engineer" });
    expect(
      await within(artigo).findByText("Nota ATS do currículo adaptado: 74/100"),
    ).toBeInTheDocument();
    expect(within(artigo).getByLabelText("Texto da carta")).toHaveValue(
      "Prezada equipe da Globex, ...",
    );
    const link = within(artigo).getByRole("link", { name: /Abrir vaga para se candidatar/ });
    expect(link).toHaveAttribute("href", "https://weworkremotely.com/2");
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", expect.stringContaining("noopener"));
    await userEvent.click(within(artigo).getByRole("button", { name: "Baixar PDF" }));
    expect(downloads).toEqual(["AdrianoTeixeira-2026-11-06-SeniorBackendEngineer-Globex.pdf"]);
    expect(corpos.find((c) => c.rota === "candidatar")?.corpo).toEqual({
      vaga: {
        titulo: "Senior Backend Engineer",
        empresa: "Globex",
        descricao: "Python, FastAPI e Kafka.",
        url: "https://weworkremotely.com/2",
        fonte: "WE_WORK_REMOTELY",
        data_publicacao: null,
      },
      idioma_alvo: "en",
      perfil_identificador: "adriano",
    });
    vi.restoreAllMocks();
  });

  it("sem currículo mestre, candidata com o PDF de referência", async () => {
    const corpos = servirDescoberta(VAGAS, { perfil: null });
    renderizarApp({ caminho: "/descobrir-vagas", perfil: "adriano" });
    await buscar();

    await userEvent.click(
      await screen.findByRole("button", { name: "Candidatar em Python Developer" }),
    );

    await within(screen.getByRole("article", { name: "Python Developer" })).findByText(/Nota ATS/);
    const corpo = corpos.find((c) => c.rota === "candidatar")!.corpo;
    expect(corpo.perfil_identificador).toBeUndefined();
    expect(atob(corpo.pdf_base64 as string)).toBe("%PDF-biblioteca");
  });

  it("mostra a falha da busca", async () => {
    servirDescoberta();
    servidorApi.use(
      http.post(`${API_TESTE}/v1/vagas/descobrir`, () =>
        HttpResponse.json(
          {
            type: "t",
            title: "Erro",
            status: 500,
            detail: "Ocorreu um erro inesperado.",
            instance: "i",
          },
          { status: 500 },
        ),
      ),
    );
    renderizarApp({ caminho: "/descobrir-vagas", perfil: "adriano" });

    await buscar();

    expect(
      await screen.findByText(/Não foi possível buscar vagas: Ocorreu um erro inesperado\./),
    ).toBeInTheDocument();
  });
});
