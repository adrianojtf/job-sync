import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import {
  CANDIDATURA,
  CURRICULO_SALVO,
  PERFIL_ESTRUTURADO,
  servirDadosBase,
  VAGA_SALVA,
} from "../../test/fixtures";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

function servirCandidaturas(...lista: (typeof CANDIDATURA)[]) {
  servidorApi.use(
    http.get(`${API_TESTE}/v1/candidaturas`, () =>
      HttpResponse.json({
        por_status: Object.fromEntries(
          ["APLICADO", "ENTREVISTA", "OFERTA", "REJEITADO"].map((status) => [
            status,
            lista.filter((c) => c.status === status),
          ]),
        ),
        total: lista.length,
      }),
    ),
  );
}

const indicador = (rotulo: string) => screen.getByRole("group", { name: rotulo });

describe("VisaoGeralPage", () => {
  it("cumprimenta pelo primeiro nome e mostra indicadores, vagas recentes, currículo e atividades", async () => {
    servirDadosBase();
    servirCandidaturas(
      {
        ...CANDIDATURA,
        status: "ENTREVISTA",
        historico_status: [{ status: "ENTREVISTA", data: "2026-11-05T15:00:00" }],
      },
      { ...CANDIDATURA, id: "cand-2", cargo: "Platform Engineer", empresa: "Thoughtworks" },
    );

    renderizarApp({ caminho: "/", perfil: "adriano" });

    expect(
      await screen.findByRole("heading", {
        level: 1,
        name: /^(Bom dia|Boa tarde|Boa noite), Adriano$/,
      }),
    ).toBeInTheDocument();
    expect(await within(indicador("Currículos salvos")).findByText("1")).toBeInTheDocument();
    expect(within(indicador("Vagas salvas")).getByText("1")).toBeInTheDocument();
    expect(await within(indicador("Candidaturas ativas")).findByText("2")).toBeInTheDocument();
    expect(
      within(indicador("Candidaturas ativas")).getByText("1 aguardando retorno"),
    ).toBeInTheDocument();
    expect(within(indicador("Em entrevista ou oferta")).getByText("1")).toBeInTheDocument();

    const recentes = screen.getByRole("region", { name: "Suas vagas recentes" });
    const primeiroItem = within(recentes).getAllByRole("listitem")[0]!;
    expect(
      within(primeiroItem).getByRole("link", { name: "Senior Java Backend Developer" }),
    ).toHaveAttribute("href", "/candidaturas");
    expect(within(recentes).getByText("Entrevista")).toBeInTheDocument();
    expect(within(recentes).getByText("Sem candidatura")).toBeInTheDocument();

    const curriculo = screen.getByRole("region", { name: "Currículo principal" });
    expect(within(curriculo).getByText("Adriano Teixeira")).toBeInTheDocument();
    expect(within(curriculo).getByText("Dev Java")).toBeInTheDocument();
    expect(
      within(curriculo).getByRole("progressbar", { name: "Completude do currículo mestre" }),
    ).toHaveAttribute("aria-valuenow", "57");
    expect(within(curriculo).getByRole("link", { name: "Editar currículo" })).toHaveAttribute(
      "href",
      "/perfil",
    );

    const atividade = screen.getByRole("region", { name: "Atividade recente" });
    const eventos = within(atividade).getAllByRole("listitem");
    expect(eventos[0]).toHaveTextContent("Senior Java Backend Developer movida para Entrevista");
    expect(
      within(atividade).getByText(/Vaga salva: Senior Java Backend Developer/),
    ).toBeInTheDocument();
    expect(
      within(atividade).getByText(`Currículo enviado: ${CURRICULO_SALVO.nome_referencia}`),
    ).toBeInTheDocument();
  });

  it("no primeiro acesso, chama para completar o currículo mestre", async () => {
    renderizarApp({ caminho: "/", perfil: "adriano" });

    expect(
      await screen.findByRole("heading", { level: 1, name: /, adriano$/ }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("heading", { name: "Complete seu currículo mestre" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Preencher meu perfil" })).toHaveAttribute(
      "href",
      "/perfil",
    );
    expect(await within(indicador("Vagas salvas")).findByText("0")).toBeInTheDocument();
    expect(
      within(screen.getByRole("region", { name: "Suas vagas recentes" })).getByText(
        /Nenhuma vaga ainda/,
      ),
    ).toBeInTheDocument();
    expect(
      within(screen.getByRole("region", { name: "Atividade recente" })).getByText(
        "Nenhuma atividade ainda.",
      ),
    ).toBeInTheDocument();
  });

  it("o botão principal abre o modal de Ajustar para uma vaga", async () => {
    servirDadosBase({ perfil: PERFIL_ESTRUTURADO, vagas: [VAGA_SALVA] });
    renderizarApp({ caminho: "/", perfil: "adriano" });
    await screen.findByRole("heading", { level: 1 });

    const botoes = screen.getAllByRole("button", { name: "Ajustar para uma vaga" });
    expect(botoes).toHaveLength(1);
    await userEvent.click(botoes[0]!);

    expect(
      screen.getByRole("dialog", { name: "Ajustar currículo para uma vaga" }),
    ).toBeInTheDocument();
  });

  it("avisa quando parte dos dados não carregou e permite tentar de novo", async () => {
    let falhar = true;
    servidorApi.use(
      http.get(`${API_TESTE}/v1/vagas`, () =>
        falhar
          ? HttpResponse.json(
              { type: "t", title: "Erro", status: 500, detail: "Falhou.", instance: "i" },
              { status: 500 },
            )
          : HttpResponse.json({ items: [VAGA_SALVA], total: 1, limite: 100, offset: 0 }),
      ),
    );
    renderizarApp({ caminho: "/", perfil: "adriano" });

    expect(await screen.findByText(/Alguns dados não carregaram/)).toBeInTheDocument();
    falhar = false;
    await userEvent.click(screen.getByRole("button", { name: "Tentar novamente" }));

    expect(await within(indicador("Vagas salvas")).findByText("1")).toBeInTheDocument();
    expect(screen.queryByText(/Alguns dados não carregaram/)).not.toBeInTheDocument();
  });
});
