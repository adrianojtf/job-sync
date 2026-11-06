import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { CANDIDATURA, servirDadosBase } from "../../test/fixtures";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

type Candidatura = typeof CANDIDATURA;
const STATUS = ["APLICADO", "ENTREVISTA", "OFERTA", "REJEITADO"];

function servirCandidaturas(iniciais: Candidatura[]) {
  const candidaturas = iniciais.map((candidatura) => ({ ...candidatura }));
  const movimentos: { id: string; novo_status: string }[] = [];
  servirDadosBase();
  servidorApi.use(
    http.get(`${API_TESTE}/v1/candidaturas`, () =>
      HttpResponse.json({
        por_status: Object.fromEntries(
          STATUS.map((status) => [status, candidaturas.filter((c) => c.status === status)]),
        ),
        total: candidaturas.length,
      }),
    ),
    http.post(`${API_TESTE}/v1/candidaturas/:id/submissao`, async ({ params, request }) => {
      const { novo_status } = (await request.json()) as { novo_status: string };
      movimentos.push({ id: String(params.id), novo_status });
      const candidatura = candidaturas.find((c) => c.id === params.id)!;
      candidatura.status = novo_status.toUpperCase();
      candidatura.historico_status = [{ status: candidatura.status, data: "2026-11-06T15:30:00" }];
      return HttpResponse.json(candidatura);
    }),
  );
  return movimentos;
}

const coluna = (nome: string) => screen.getByRole("region", { name: new RegExp(`^${nome}`) });

describe("CandidaturasPage", () => {
  it("mostra as quatro colunas com contagem e os cartões", async () => {
    servirCandidaturas([
      CANDIDATURA,
      {
        ...CANDIDATURA,
        id: "cand-2",
        cargo: "Platform Engineer",
        empresa: "Thoughtworks",
        status: "ENTREVISTA",
      },
    ]);

    renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });

    expect(await screen.findByText("Senior Java Backend Developer")).toBeInTheDocument();
    expect(coluna("Aplicado")).toHaveAccessibleName("Aplicado, 1 candidatura");
    expect(coluna("Entrevista")).toHaveAccessibleName("Entrevista, 1 candidatura");
    expect(coluna("Oferta")).toHaveAccessibleName("Oferta, 0 candidaturas");
    expect(within(coluna("Rejeitado")).getByText("Nenhuma candidatura")).toBeInTheDocument();
    expect(within(coluna("Entrevista")).getByText("Thoughtworks")).toBeInTheDocument();
    expect(within(coluna("Aplicado")).getByText("Aplicada em 02/11/2026")).toBeInTheDocument();
  });

  it("move a candidatura de coluna pelo menu Mover para", async () => {
    const movimentos = servirCandidaturas([CANDIDATURA]);
    renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });

    await userEvent.selectOptions(
      await screen.findByLabelText("Mover Senior Java Backend Developer para"),
      "ENTREVISTA",
    );

    expect(
      await within(coluna("Entrevista")).findByText("Senior Java Backend Developer"),
    ).toBeInTheDocument();
    expect(within(coluna("Aplicado")).getByText("Nenhuma candidatura")).toBeInTheDocument();
    expect(movimentos).toEqual([{ id: "cand-1", novo_status: "entrevista" }]);
    expect(screen.getByRole("status")).toHaveTextContent("Candidatura movida para Entrevista.");
  });

  it("mostra a falha ao mover e mantém o cartão na coluna", async () => {
    servirCandidaturas([CANDIDATURA]);
    servidorApi.use(
      http.post(`${API_TESTE}/v1/candidaturas/:id/submissao`, () =>
        HttpResponse.json(
          {
            type: "t",
            title: "Não encontrado",
            status: 404,
            detail: "Candidatura não encontrada.",
            instance: "i",
          },
          { status: 404 },
        ),
      ),
    );
    renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });

    await userEvent.selectOptions(
      await screen.findByLabelText("Mover Senior Java Backend Developer para"),
      "OFERTA",
    );

    expect(await screen.findByRole("alert")).toHaveTextContent("Candidatura não encontrada.");
    expect(
      within(coluna("Aplicado")).getByText("Senior Java Backend Developer"),
    ).toBeInTheDocument();
  });

  it("mostra o detalhe com histórico e currículo usado", async () => {
    servirCandidaturas([CANDIDATURA]);
    renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });

    await userEvent.click(
      await screen.findByRole("button", { name: "Detalhes de Senior Java Backend Developer" }),
    );
    const dialogo = screen.getByRole("dialog", { name: "Senior Java Backend Developer" });

    expect(within(dialogo).getByText("Neoway")).toBeInTheDocument();
    expect(await within(dialogo).findByText("CV LinkedIn")).toBeInTheDocument();
    const historico = within(dialogo).getByRole("list", { name: "Histórico de status" });
    expect(within(historico).getByText(/Aplicado · 02\/11\/2026/)).toBeInTheDocument();
  });

  it("sem candidaturas, aponta para as vagas salvas", async () => {
    servirCandidaturas([]);

    renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });

    expect(await screen.findByText("Nenhuma candidatura ainda")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Ir para Vagas salvas" })).toHaveAttribute(
      "href",
      "/vagas-salvas",
    );
  });
});
