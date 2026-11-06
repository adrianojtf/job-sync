import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import type { Vaga } from "../../api/tipos";
import { AVALIACAO_VAGA, servirDadosBase, VAGA_SALVA } from "../../test/fixtures";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

function servirVagas(
  iniciais: Vaga[],
  curriculos = undefined as Parameters<typeof servirDadosBase>[0],
) {
  const vagas = [...iniciais];
  const recebidos: { rota: string; corpo: Record<string, unknown> }[] = [];
  servirDadosBase(curriculos);
  servidorApi.use(
    http.get(`${API_TESTE}/v1/vagas`, () =>
      HttpResponse.json({ items: vagas, total: vagas.length, limite: 100, offset: 0 }),
    ),
    http.post(`${API_TESTE}/v1/vagas`, async ({ request }) => {
      const corpo = (await request.json()) as Record<string, string>;
      recebidos.push({ rota: "capturar", corpo });
      const nova: Vaga = {
        id: `v${vagas.length + 10}`,
        perfil_identificador: corpo.perfil_identificador!,
        texto_descricao: corpo.texto_descricao!,
        url_origem: corpo.url_origem ?? null,
        data_captura: "2026-11-06T12:00:00",
      };
      vagas.unshift(nova);
      return HttpResponse.json(nova, { status: 201 });
    }),
    http.post(`${API_TESTE}/v1/candidaturas`, async ({ request }) => {
      const corpo = (await request.json()) as Record<string, string>;
      recebidos.push({ rota: "candidatura", corpo });
      vagas.splice(
        vagas.findIndex((vaga) => vaga.id === corpo.vaga_id),
        1,
      );
      return HttpResponse.json(
        {
          id: "cand-9",
          ...corpo,
          status: "APLICADO",
          data_aplicacao: "2026-11-06T12:00:00",
          historico_status: [],
        },
        { status: 201 },
      );
    }),
    http.post(`${API_TESTE}/v1/vagas/avaliacoes`, () => HttpResponse.json(AVALIACAO_VAGA)),
  );
  return recebidos;
}

const TITULO = "Senior Java Backend Developer";

describe("VagasSalvasPage", () => {
  it("lista as vagas com título, origem e data", async () => {
    servirVagas([VAGA_SALVA]);

    renderizarApp({ caminho: "/vagas-salvas", perfil: "adriano" });

    expect(await screen.findByText(TITULO)).toBeInTheDocument();
    expect(screen.getByText("example.com · Salva em 05/11/2026")).toBeInTheDocument();
    expect(screen.getByText("1 vaga")).toBeInTheDocument();
  });

  it("sem vagas, explica como capturar", async () => {
    servirVagas([]);

    renderizarApp({ caminho: "/vagas-salvas", perfil: "adriano" });

    expect(await screen.findByText("Nenhuma vaga salva")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "gere o token da extensão" })).toHaveAttribute(
      "href",
      "/configuracoes",
    );
  });

  it("registra uma vaga colada e mostra na lista", async () => {
    const recebidos = servirVagas([]);
    renderizarApp({ caminho: "/vagas-salvas", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("button", { name: "Colar vaga" }));
    const dialogo = screen.getByRole("dialog", { name: "Colar vaga" });
    await userEvent.click(within(dialogo).getByRole("button", { name: "Salvar vaga" }));
    expect(within(dialogo).getByLabelText("Descrição da vaga")).toHaveAccessibleDescription(
      "Cole a descrição da vaga.",
    );

    await userEvent.type(
      within(dialogo).getByLabelText("Descrição da vaga"),
      "Backend Python{Enter}FastAPI",
    );
    await userEvent.type(
      within(dialogo).getByLabelText("Link da vaga (opcional)"),
      "https://jobs.example.org/1",
    );
    await userEvent.click(within(dialogo).getByRole("button", { name: "Salvar vaga" }));

    expect(await screen.findByText("Backend Python")).toBeInTheDocument();
    expect(recebidos[0]).toEqual({
      rota: "capturar",
      corpo: {
        perfil_identificador: "adriano",
        texto_descricao: "Backend Python\nFastAPI",
        url_origem: "https://jobs.example.org/1",
      },
    });
  });

  it("mostra o detalhe com a descrição completa, o link original e a avaliação", async () => {
    servirVagas([VAGA_SALVA]);
    renderizarApp({ caminho: "/vagas-salvas", perfil: "adriano" });

    await userEvent.click(
      await screen.findByRole("button", { name: `Detalhes da vaga ${TITULO}` }),
    );
    const dialogo = screen.getByRole("dialog", { name: TITULO });

    expect(within(dialogo).getByText(/Requisitos: Java, Kafka, AWS\./)).toBeInTheDocument();
    const link = within(dialogo).getByRole("link", { name: /Abrir vaga original/ });
    expect(link).toHaveAttribute("href", VAGA_SALVA.url_origem);
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", expect.stringContaining("noopener"));

    await userEvent.click(within(dialogo).getByRole("button", { name: "Avaliar descrição" }));

    expect(await within(dialogo).findByRole("meter", { name: "Clareza" })).toHaveAttribute(
      "aria-valuenow",
      "80",
    );
  });

  it("abre Ajustar para uma vaga com a vaga preenchida", async () => {
    servirVagas([VAGA_SALVA]);
    renderizarApp({ caminho: "/vagas-salvas", perfil: "adriano" });

    await userEvent.click(
      await screen.findByRole("button", { name: `Detalhes da vaga ${TITULO}` }),
    );
    await userEvent.click(screen.getByRole("button", { name: "Ajustar currículo" }));

    expect(
      await screen.findByRole("heading", { level: 1, name: "Ajustar para uma vaga" }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Título da vaga")).toHaveValue(TITULO);
    expect(screen.getByLabelText("Descrição da vaga")).toHaveValue(VAGA_SALVA.texto_descricao);
  });

  it("abre Analisar ATS com a descrição da vaga", async () => {
    servirVagas([VAGA_SALVA]);
    renderizarApp({ caminho: "/vagas-salvas", perfil: "adriano" });

    await userEvent.click(
      await screen.findByRole("button", { name: `Detalhes da vaga ${TITULO}` }),
    );
    await userEvent.click(screen.getByRole("button", { name: "Analisar ATS" }));

    expect(
      await screen.findByRole("heading", { level: 1, name: "Analisar ATS" }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Descrição da vaga")).toHaveValue(VAGA_SALVA.texto_descricao);
  });

  it("cria a candidatura e a vaga sai da lista", async () => {
    const recebidos = servirVagas([VAGA_SALVA]);
    renderizarApp({ caminho: "/vagas-salvas", perfil: "adriano" });

    await userEvent.click(
      await screen.findByRole("button", { name: `Criar candidatura para ${TITULO}` }),
    );
    const dialogo = screen.getByRole("dialog", { name: "Criar candidatura" });
    expect(within(dialogo).getByLabelText("Cargo")).toHaveValue(TITULO);
    await userEvent.click(within(dialogo).getByRole("button", { name: "Criar candidatura" }));
    expect(within(dialogo).getByLabelText("Empresa")).toHaveAccessibleDescription(
      "Informe a empresa.",
    );

    await userEvent.type(within(dialogo).getByLabelText("Empresa"), "Olist");
    await userEvent.click(within(dialogo).getByRole("button", { name: "Criar candidatura" }));

    expect(await screen.findByText("Nenhuma vaga salva")).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("Candidatura criada em Aplicado.");
    expect(recebidos.find((r) => r.rota === "candidatura")?.corpo).toEqual({
      perfil_identificador: "adriano",
      vaga_id: VAGA_SALVA.id,
      curriculo_salvo_id: "c1",
      empresa: "Olist",
      cargo: TITULO,
    });
  });

  it("sem currículos na biblioteca, explica que a candidatura precisa de um PDF", async () => {
    servirVagas([VAGA_SALVA], { curriculos: [] });
    renderizarApp({ caminho: "/vagas-salvas", perfil: "adriano" });

    await userEvent.click(
      await screen.findByRole("button", { name: `Criar candidatura para ${TITULO}` }),
    );
    const dialogo = screen.getByRole("dialog", { name: "Criar candidatura" });

    await waitFor(() =>
      expect(
        within(dialogo).getByText(/A candidatura registra qual PDF você enviou/),
      ).toBeInTheDocument(),
    );
    expect(within(dialogo).getByRole("link", { name: "Meus currículos" })).toHaveAttribute(
      "href",
      "/curriculos",
    );
    expect(within(dialogo).getByRole("button", { name: "Criar candidatura" })).toBeDisabled();
  });
});
