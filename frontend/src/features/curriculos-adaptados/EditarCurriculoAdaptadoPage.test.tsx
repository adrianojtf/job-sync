import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { CURRICULO_ADAPTADO, servirDadosBase } from "../../test/fixtures";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

const PDF_EDITADO = {
  id: "ad1",
  nome_arquivo: "AdrianoTeixeira-2026-11-08-SeniorJava-Olist.pdf",
  pdf_base64: btoa("%PDF-editado"),
  atualizado_em: "2026-11-08T10:00:00Z",
};

const problema = (status: number, detail: string) =>
  HttpResponse.json({ type: "t", title: "Erro", status, detail, instance: "i" }, { status });

function servirCurriculoAdaptado() {
  const consultas: string[] = [];
  const atualizacoes: Record<string, unknown>[] = [];
  servidorApi.use(
    http.get(`${API_TESTE}/v1/curriculos-adaptados/:id`, ({ params, request }) => {
      consultas.push(
        `${params.id}?${new URL(request.url).searchParams.get("perfil_identificador")}`,
      );
      return HttpResponse.json(CURRICULO_ADAPTADO);
    }),
    http.put(`${API_TESTE}/v1/curriculos-adaptados/:id`, async ({ request }) => {
      atualizacoes.push((await request.json()) as Record<string, unknown>);
      return HttpResponse.json(PDF_EDITADO);
    }),
  );
  return { consultas, atualizacoes };
}

function capturarConteudoBaixado() {
  const conteudos: Promise<string>[] = [];
  Object.assign(URL, {
    createObjectURL: vi.fn((blob: Blob) => {
      conteudos.push(
        new Promise<string>((resolve) => {
          const leitor = new FileReader();
          leitor.onload = () => resolve(String(leitor.result));
          leitor.readAsText(blob);
        }),
      );
      return "blob:x";
    }),
    revokeObjectURL: vi.fn(),
  });
  vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
  return conteudos;
}

afterEach(() => vi.restoreAllMocks());

describe("EditarCurriculoAdaptadoPage", () => {
  it("reabre o currículo salvo para o perfil da sessão, com o conteúdo e as tags", async () => {
    servirDadosBase();
    const { consultas } = servirCurriculoAdaptado();

    renderizarApp({ caminho: "/curriculos-adaptados/ad1", perfil: "adriano" });

    await screen.findByRole("heading", { name: "Edite o currículo adaptado" });
    expect(consultas).toEqual(["ad1?adriano"]);
    expect(screen.getByLabelText("Resumo profissional")).toHaveValue("Resumo salvo.");
    expect(
      within(screen.getByRole("group", { name: "Linguagens" })).getByText("Python"),
    ).toBeInTheDocument();
    expect(
      within(screen.getByRole("group", { name: "Bancos de Dados" })).getByText("SQL"),
    ).toBeInTheDocument();
  });

  it("mostra o carregamento enquanto busca o currículo", async () => {
    servirDadosBase();
    servirCurriculoAdaptado();

    renderizarApp({ caminho: "/curriculos-adaptados/ad1", perfil: "adriano" });

    expect(await screen.findByText("Carregando currículo…")).toBeInTheDocument();
    await screen.findByRole("heading", { name: "Edite o currículo adaptado" });
  });

  it("currículo inexistente mostra o erro e o caminho de volta", async () => {
    servirDadosBase();
    servidorApi.use(
      http.get(`${API_TESTE}/v1/curriculos-adaptados/:id`, () =>
        problema(404, "Currículo adaptado não encontrado."),
      ),
    );

    renderizarApp({ caminho: "/curriculos-adaptados/nao-existe", perfil: "adriano" });

    expect(await screen.findByText(/Currículo adaptado não encontrado\./)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Voltar para Meus currículos" })).toHaveAttribute(
      "href",
      "/curriculos",
    );
  });

  it("salvar envia a edição, mostra o PDF novo e permite baixá-lo", async () => {
    servirDadosBase();
    const { atualizacoes } = servirCurriculoAdaptado();
    const conteudos = capturarConteudoBaixado();
    renderizarApp({ caminho: "/curriculos-adaptados/ad1", perfil: "adriano" });
    await screen.findByRole("heading", { name: "Edite o currículo adaptado" });
    await userEvent.click(
      within(screen.getByRole("group", { name: "Linguagens" })).getByRole("button", {
        name: "Remover Python",
      }),
    );

    await userEvent.click(screen.getByRole("button", { name: "Salvar alterações" }));

    expect(await screen.findByText(PDF_EDITADO.nome_arquivo)).toBeInTheDocument();
    expect(atualizacoes[0]).toMatchObject({
      perfil_identificador: "adriano",
      rascunho: {
        competencias: [
          { nome: "Linguagens", tags: ["Java"] },
          { nome: "Bancos de Dados", tags: ["SQL"] },
        ],
      },
    });
    await userEvent.click(screen.getByRole("button", { name: "Baixar PDF" }));
    expect(await Promise.all(conteudos)).toEqual(["%PDF-editado"]);
  });

  it("depois de salvar, Editar de novo parte do que foi salvo por último", async () => {
    servirDadosBase();
    servirCurriculoAdaptado();
    renderizarApp({ caminho: "/curriculos-adaptados/ad1", perfil: "adriano" });
    await screen.findByRole("heading", { name: "Edite o currículo adaptado" });
    await userEvent.clear(screen.getByLabelText("Resumo profissional"));
    await userEvent.type(screen.getByLabelText("Resumo profissional"), "Resumo novo.");
    await userEvent.click(screen.getByRole("button", { name: "Salvar alterações" }));
    await screen.findByText(PDF_EDITADO.nome_arquivo);

    await userEvent.click(screen.getByRole("button", { name: "Editar de novo" }));

    expect(await screen.findByLabelText("Resumo profissional")).toHaveValue("Resumo novo.");
  });

  it("falha ao salvar mantém a edição com o que foi digitado", async () => {
    servirDadosBase();
    servirCurriculoAdaptado();
    servidorApi.use(
      http.put(`${API_TESTE}/v1/curriculos-adaptados/:id`, () =>
        problema(422, "Rascunho inválido."),
      ),
    );
    renderizarApp({ caminho: "/curriculos-adaptados/ad1", perfil: "adriano" });
    await screen.findByRole("heading", { name: "Edite o currículo adaptado" });
    await userEvent.type(screen.getByLabelText("Resumo profissional"), " Mais.");

    await userEvent.click(screen.getByRole("button", { name: "Salvar alterações" }));

    expect(await screen.findByText(/Rascunho inválido\./)).toBeInTheDocument();
    expect(screen.getByLabelText("Resumo profissional")).toHaveValue("Resumo salvo. Mais.");
  });

  it("Voltar leva para Meus currículos", async () => {
    servirDadosBase();
    servirCurriculoAdaptado();
    renderizarApp({ caminho: "/curriculos-adaptados/ad1", perfil: "adriano" });
    await screen.findByRole("heading", { name: "Edite o currículo adaptado" });

    await userEvent.click(screen.getByRole("button", { name: "Voltar" }));

    expect(
      await screen.findByRole("heading", { level: 1, name: "Meus currículos" }),
    ).toBeInTheDocument();
  });

  it("as sugestões de IA da edição usam a vaga original do currículo", async () => {
    servirDadosBase();
    servirCurriculoAdaptado();
    const pedidos: Record<string, unknown>[] = [];
    servidorApi.use(
      http.post(`${API_TESTE}/v1/secoes-curriculo/sugestoes`, async ({ request }) => {
        pedidos.push((await request.json()) as Record<string, unknown>);
        return HttpResponse.json({ conteudo_sugerido: "Resumo sugerido.", foco: "aderencia_vaga" });
      }),
    );
    renderizarApp({ caminho: "/curriculos-adaptados/ad1", perfil: "adriano" });
    await screen.findByRole("heading", { name: "Edite o currículo adaptado" });

    await userEvent.click(screen.getByRole("button", { name: "Sugestões de IA para resumo" }));
    await screen.findByText("Resumo sugerido.");

    expect(pedidos[0]).toMatchObject({
      contexto_vaga: {
        descricao_vaga: "Java, Kafka e AWS.",
        idioma_alvo: "pt",
        cargo_alvo: "Senior Java",
        analise_vaga: { texto_original: "Java, Kafka e AWS." },
      },
    });
  });
});
