import type { DndContextProps, DragCancelEvent, DragEndEvent } from "@dnd-kit/core";
import { act, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import {
  CANDIDATURA,
  CURRICULO_ADAPTADO_RESUMO,
  CURRICULO_SALVO,
  servirDadosBase,
} from "../../test/fixtures";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

import type { CurriculoAdaptadoResumo } from "../../api/tipos";

type Candidatura = typeof CANDIDATURA;
const STATUS = ["APLICADO", "ENTREVISTA", "OFERTA", "REJEITADO"];

const dnd = vi.hoisted(() => ({ props: null as DndContextProps | null }));
vi.mock("@dnd-kit/core", async (importOriginal) => {
  const real = await importOriginal<typeof import("@dnd-kit/core")>();
  return {
    ...real,
    DndContext: (props: DndContextProps) => {
      dnd.props = props;
      return <real.DndContext {...props} />;
    },
  };
});

const esperarUmPouco = () => act(() => new Promise<void>((resolver) => setTimeout(resolver, 30)));

async function soltar(ativo: string, sobre: string | null) {
  await act(async () => {
    dnd.props!.onDragEnd!({
      active: { id: ativo },
      over: sobre ? { id: sobre } : null,
    } as DragEndEvent);
  });
  await esperarUmPouco();
}

async function cancelar(ativo: string) {
  await act(async () => {
    dnd.props!.onDragCancel!({ active: { id: ativo }, over: null } as DragCancelEvent);
  });
  await esperarUmPouco();
}

function servirCandidaturas(iniciais: Candidatura[]) {
  const candidaturas = iniciais.map((candidatura) => ({ ...candidatura }));
  const movimentos: { id: string; novo_status: string; posicao?: number }[] = [];
  servirDadosBase();
  servidorApi.use(
    http.get(`${API_TESTE}/v1/candidaturas`, () =>
      HttpResponse.json({
        por_status: Object.fromEntries(
          STATUS.map((status) => [
            status,
            candidaturas.filter((c) => c.status === status).sort((a, b) => a.posicao - b.posicao),
          ]),
        ),
        total: candidaturas.length,
      }),
    ),
    http.post(`${API_TESTE}/v1/candidaturas/:id/submissao`, async ({ params, request }) => {
      const { novo_status, posicao } = (await request.json()) as {
        novo_status: string;
        posicao?: number;
      };
      movimentos.push({
        id: String(params.id),
        novo_status,
        ...(posicao === undefined ? {} : { posicao }),
      });
      const candidatura = candidaturas.find((c) => c.id === params.id)!;
      const novoStatus = novo_status.toUpperCase();
      const destino = candidaturas
        .filter((c) => c.status === novoStatus && c.id !== candidatura.id)
        .sort((a, b) => a.posicao - b.posicao);
      destino.splice(Math.min(posicao ?? 0, destino.length), 0, candidatura);
      destino.forEach((c, indice) => (c.posicao = indice));
      candidatura.status = novoStatus;
      candidatura.historico_status = [{ status: novoStatus, data: "2026-11-06T15:30:00" }];
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
    const quando = within(coluna("Aplicado")).getByTitle("Aplicada em 02/11/2026");
    expect(quando.tagName).toBe("TIME");
    expect(quando).toHaveAttribute("datetime", "2026-11-02T09:00:00");
    expect(quando).toHaveTextContent(
      /^(hoje|há \d+ (dia|dias|semana|semanas|mês|meses|ano|anos))$/,
    );
    expect(within(coluna("Aplicado")).getByText("N")).toHaveAttribute("aria-hidden", "true");
    expect(within(coluna("Rejeitado")).getByText("Arraste um cartão até aqui")).toBeInTheDocument();
  });

  it("não tem mais caixa de seleção nem botão Detalhes nos cartões", async () => {
    servirCandidaturas([CANDIDATURA]);

    renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });

    await screen.findByText("Senior Java Backend Developer");
    expect(screen.queryByRole("combobox")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^Detalhes/ })).not.toBeInTheDocument();
  });

  it("o cartão é um item de lista com o título como único botão", async () => {
    servirCandidaturas([CANDIDATURA]);

    renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });

    await screen.findByText("Senior Java Backend Developer");
    const cartao = within(coluna("Aplicado")).getAllByRole("listitem")[0]!;
    expect(cartao).toHaveAttribute("tabindex", "0");
    expect(cartao).toHaveAttribute("aria-roledescription", "cartão arrastável");
    expect(within(cartao).getAllByRole("button")).toHaveLength(1);
  });

  describe("arrastar e soltar", () => {
    async function abrirBoard(candidaturas: Candidatura[] = [CANDIDATURA]) {
      const movimentos = servirCandidaturas(candidaturas);
      renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });
      await screen.findByText(candidaturas[0]!.cargo);
      return movimentos;
    }

    const duasAplicadas = () => [
      { ...CANDIDATURA, id: "cand-1", cargo: "Vaga Um", posicao: 0 },
      { ...CANDIDATURA, id: "cand-2", cargo: "Vaga Dois", posicao: 1 },
      { ...CANDIDATURA, id: "cand-3", cargo: "Vaga Três", posicao: 2 },
    ];

    it("soltar sobre outra coluna move a candidatura para o fim dela", async () => {
      const movimentos = await abrirBoard();

      await soltar("cand-1", "coluna:ENTREVISTA");

      expect(
        await within(coluna("Entrevista")).findByText("Senior Java Backend Developer"),
      ).toBeInTheDocument();
      expect(within(coluna("Aplicado")).getByText("Nenhuma candidatura")).toBeInTheDocument();
      expect(movimentos).toEqual([{ id: "cand-1", novo_status: "entrevista", posicao: 0 }]);
      expect(await screen.findByText("Candidatura movida para Entrevista.")).toBeInTheDocument();
    });

    it("soltar sobre um cartão de outra coluna usa a posição dele", async () => {
      const movimentos = await abrirBoard([
        ...duasAplicadas(),
        { ...CANDIDATURA, id: "cand-9", cargo: "Vaga Nove", status: "ENTREVISTA", posicao: 0 },
      ]);

      await soltar("cand-2", "cand-9");

      await waitFor(() =>
        expect(movimentos).toEqual([{ id: "cand-2", novo_status: "entrevista", posicao: 0 }]),
      );
    });

    it("reordena dentro da coluna enviando a nova posição", async () => {
      const movimentos = await abrirBoard(duasAplicadas());

      await soltar("cand-1", "cand-3");

      await waitFor(() =>
        expect(movimentos).toEqual([{ id: "cand-1", novo_status: "aplicado", posicao: 2 }]),
      );
      await waitFor(() =>
        expect(
          within(coluna("Aplicado"))
            .getAllByRole("listitem")
            .map((item) => item.textContent),
        ).toEqual([
          expect.stringContaining("Vaga Dois"),
          expect.stringContaining("Vaga Três"),
          expect.stringContaining("Vaga Um"),
        ]),
      );
    });

    it("soltar no mesmo lugar não chama a API", async () => {
      const movimentos = await abrirBoard(duasAplicadas());

      await soltar("cand-2", "cand-2");
      await soltar("cand-3", "coluna:APLICADO");

      expect(movimentos).toEqual([]);
    });

    it("soltar fora de qualquer coluna não chama a API", async () => {
      const movimentos = await abrirBoard();

      await soltar("cand-1", null);

      expect(movimentos).toEqual([]);
    });

    it("cancelar o arrasto não chama a API", async () => {
      const movimentos = await abrirBoard();

      await cancelar("cand-1");

      expect(movimentos).toEqual([]);
    });

    it("mostra a falha ao soltar e devolve o cartão à coluna de origem", async () => {
      await abrirBoard();
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

      await soltar("cand-1", "coluna:OFERTA");

      expect(await screen.findByRole("alert")).toHaveTextContent("Candidatura não encontrada.");
      expect(
        within(coluna("Aplicado")).getByText("Senior Java Backend Developer"),
      ).toBeInTheDocument();
    });

    it("anuncia o movimento por teclado em português", async () => {
      await abrirBoard();
      const cartao = within(coluna("Aplicado")).getAllByRole("listitem")[0]!;

      cartao.focus();
      await userEvent.keyboard(" ");

      expect(
        await screen.findByText("Candidatura Senior Java Backend Developer na posição original."),
      ).toBeInTheDocument();
      await userEvent.keyboard("{Escape}");
      expect(
        await screen.findByText(
          "Movimento cancelado. Candidatura Senior Java Backend Developer voltou à posição original.",
        ),
      ).toBeInTheDocument();
    });
  });

  describe("detalhe da candidatura", () => {
    it("o título do cartão abre o detalhe", async () => {
      servirCandidaturas([CANDIDATURA]);
      renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });

      await userEvent.click(
        await screen.findByRole("button", { name: "Senior Java Backend Developer" }),
      );

      expect(
        screen.getByRole("dialog", { name: "Senior Java Backend Developer" }),
      ).toBeInTheDocument();
    });

    it("move pelo campo Mover para: topo da coluna, status atualizado e aviso", async () => {
      const movimentos = servirCandidaturas([CANDIDATURA]);
      renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });
      await userEvent.click(
        await screen.findByRole("button", { name: "Senior Java Backend Developer" }),
      );
      const dialogo = screen.getByRole("dialog", { name: "Senior Java Backend Developer" });

      await userEvent.selectOptions(within(dialogo).getByLabelText("Mover para"), "ENTREVISTA");

      expect(movimentos).toEqual([{ id: "cand-1", novo_status: "entrevista", posicao: 0 }]);
      expect(await screen.findByText("Candidatura movida para Entrevista.")).toBeInTheDocument();
      await waitFor(() =>
        expect(within(dialogo).getByLabelText("Mover para")).toHaveValue("ENTREVISTA"),
      );
      expect(
        within(coluna("Entrevista")).getByText("Senior Java Backend Developer"),
      ).toBeInTheDocument();
    });

    it("se o Mover para falhar, o campo volta ao status anterior", async () => {
      servirCandidaturas([CANDIDATURA]);
      servidorApi.use(
        http.post(`${API_TESTE}/v1/candidaturas/:id/submissao`, () =>
          HttpResponse.json(
            {
              type: "t",
              title: "Erro",
              status: 404,
              detail: "Candidatura não encontrada.",
              instance: "i",
            },
            { status: 404 },
          ),
        ),
      );
      renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });
      await userEvent.click(
        await screen.findByRole("button", { name: "Senior Java Backend Developer" }),
      );
      const dialogo = screen.getByRole("dialog", { name: "Senior Java Backend Developer" });

      await userEvent.selectOptions(within(dialogo).getByLabelText("Mover para"), "OFERTA");

      expect(await screen.findByRole("alert")).toHaveTextContent("Candidatura não encontrada.");
      await waitFor(() =>
        expect(within(dialogo).getByLabelText("Mover para")).toHaveValue("APLICADO"),
      );
    });
  });

  it("mostra o detalhe com histórico e currículo usado", async () => {
    servirCandidaturas([CANDIDATURA]);
    renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });

    await userEvent.click(
      await screen.findByRole("button", { name: "Senior Java Backend Developer" }),
    );
    const dialogo = screen.getByRole("dialog", { name: "Senior Java Backend Developer" });

    expect(within(dialogo).getByText("Neoway")).toBeInTheDocument();
    expect(await within(dialogo).findByText("CV LinkedIn")).toBeInTheDocument();
    const historico = within(dialogo).getByRole("list", { name: "Histórico de status" });
    expect(within(historico).getByText(/Aplicado · 02\/11\/2026/)).toBeInTheDocument();
  });

  describe("download do PDF usado na candidatura", () => {
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

    async function abrirDetalhe(
      candidatura: Candidatura,
      adaptados: CurriculoAdaptadoResumo[] = [],
    ) {
      servirCandidaturas([candidatura]);
      servidorApi.use(
        http.get(`${API_TESTE}/v1/curriculos-adaptados`, () =>
          HttpResponse.json({ items: adaptados, total: adaptados.length }),
        ),
      );
      renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });
      await userEvent.click(await screen.findByRole("button", { name: candidatura.cargo }));
      return screen.getByRole("dialog", { name: candidatura.cargo });
    }

    afterEach(() => vi.restoreAllMocks());

    it("o detalhe baixa o PDF do currículo ligado à candidatura", async () => {
      const downloads = capturarDownloads();
      const idsBaixados: string[] = [];
      const candidatura = { ...CANDIDATURA, curriculo_salvo_id: "pdf-gerado-9" };
      servirCandidaturas([candidatura]);
      servidorApi.use(
        http.get(`${API_TESTE}/v1/curriculos/:id/conteudo`, ({ params }) => {
          idsBaixados.push(String(params.id));
          return HttpResponse.json({
            id: params.id,
            nome_referencia: "PDF gerado",
            pdf_base64: btoa("%PDF-gerado"),
          });
        }),
        http.get(`${API_TESTE}/v1/curriculos`, () =>
          HttpResponse.json({
            items: [{ ...CURRICULO_SALVO, id: "pdf-gerado-9", nome_referencia: "PDF gerado" }],
            total: 1,
          }),
        ),
      );
      renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });
      await userEvent.click(await screen.findByRole("button", { name: candidatura.cargo }));
      const dialogo = screen.getByRole("dialog", { name: candidatura.cargo });

      await userEvent.click(
        await within(dialogo).findByRole("button", { name: "Baixar PDF do currículo usado" }),
      );

      await waitFor(() => expect(downloads).toEqual(["PDF gerado.pdf"]));
      expect(idsBaixados).toEqual(["pdf-gerado-9"]);
    });

    it("oferece Editar currículo quando o PDF veio de um currículo adaptado", async () => {
      const dialogo = await abrirDetalhe({ ...CANDIDATURA, curriculo_salvo_id: "c1" }, [
        { ...CURRICULO_ADAPTADO_RESUMO, curriculo_salvo_id: "c1" },
      ]);

      expect(
        await within(dialogo).findByRole("link", { name: "Editar currículo" }),
      ).toHaveAttribute("href", "/curriculos-adaptados/ad1");
    });

    it("não oferece Editar currículo quando nenhum currículo adaptado gerou o PDF", async () => {
      const dialogo = await abrirDetalhe({ ...CANDIDATURA, curriculo_salvo_id: "c1" }, [
        { ...CURRICULO_ADAPTADO_RESUMO, curriculo_salvo_id: "outro" },
      ]);
      await within(dialogo).findByText("CV LinkedIn");

      expect(
        within(dialogo).queryByRole("link", { name: "Editar currículo" }),
      ).not.toBeInTheDocument();
    });

    it("sem o currículo na biblioteca avisa que foi removido e não oferece o download", async () => {
      const dialogo = await abrirDetalhe({ ...CANDIDATURA, curriculo_salvo_id: "removido" });

      expect(await within(dialogo).findByText("Removido da biblioteca")).toBeInTheDocument();
      expect(
        within(dialogo).queryByRole("button", { name: "Baixar PDF do currículo usado" }),
      ).not.toBeInTheDocument();
    });

    it("mostra o erro quando o download falha", async () => {
      capturarDownloads();
      const dialogo = await abrirDetalhe(CANDIDATURA);
      servidorApi.use(
        http.get(`${API_TESTE}/v1/curriculos/:id/conteudo`, () =>
          HttpResponse.json(
            {
              type: "t",
              title: "Erro",
              status: 404,
              detail: "Currículo não encontrado.",
              instance: "i",
            },
            { status: 404 },
          ),
        ),
      );

      await userEvent.click(
        await within(dialogo).findByRole("button", { name: "Baixar PDF do currículo usado" }),
      );

      expect(await screen.findByText("Currículo não encontrado.")).toBeInTheDocument();
    });
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
