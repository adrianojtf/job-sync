import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import type { CurriculoSalvo } from "../../api/tipos";
import { CURRICULO_ADAPTADO_RESUMO } from "../../test/fixtures";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

function curriculo(indice: number): CurriculoSalvo {
  return {
    id: `c${indice}`,
    perfil_identificador: "adriano",
    nome_referencia: `Currículo ${indice}`,
    data_upload: "2026-11-06T10:00:00",
  };
}

function servirBiblioteca(inicial: CurriculoSalvo[]) {
  const biblioteca = [...inicial];
  const recebidos: unknown[] = [];
  servidorApi.use(
    http.get(`${API_TESTE}/v1/curriculos`, () =>
      HttpResponse.json({ items: biblioteca, total: biblioteca.length }),
    ),
    http.post(`${API_TESTE}/v1/curriculos`, async ({ request }) => {
      const corpo = (await request.json()) as { nome_referencia: string };
      recebidos.push(corpo);
      const novo = { ...curriculo(biblioteca.length + 1), nome_referencia: corpo.nome_referencia };
      biblioteca.push(novo);
      return HttpResponse.json(novo, { status: 201 });
    }),
    http.delete(`${API_TESTE}/v1/curriculos/:id`, ({ params }) => {
      biblioteca.splice(
        biblioteca.findIndex((item) => item.id === params.id),
        1,
      );
      return new HttpResponse(null, { status: 204 });
    }),
  );
  return { recebidos };
}

const pdf = (tamanho = 20, nome = "cv.pdf", tipo = "application/pdf") =>
  new File([new Uint8Array(tamanho)], nome, { type: tipo });

async function abrirEnvio() {
  await userEvent.click(await screen.findByRole("button", { name: "Enviar currículo" }));
  return screen.getByRole("dialog", { name: "Enviar currículo" });
}

describe("CurriculosPage", () => {
  it("lista os currículos com nome, data e contagem do limite", async () => {
    servirBiblioteca([curriculo(1), curriculo(2)]);

    renderizarApp({ caminho: "/curriculos", perfil: "adriano" });

    expect(await screen.findByText("Currículo 1")).toBeInTheDocument();
    expect(screen.getByText("Currículo 2")).toBeInTheDocument();
    expect(screen.getAllByText("Enviado em 06/11/2026")).toHaveLength(2);
    expect(screen.getByText("2 de 10 currículos")).toBeInTheDocument();
  });

  it("mostra estado vazio sem currículos", async () => {
    servirBiblioteca([]);

    renderizarApp({ caminho: "/curriculos", perfil: "adriano" });

    expect(await screen.findByText("Nenhum currículo salvo")).toBeInTheDocument();
  });

  it("envia um PDF com nome de referência e atualiza a lista", async () => {
    const { recebidos } = servirBiblioteca([]);
    renderizarApp({ caminho: "/curriculos", perfil: "adriano" });
    const dialogo = await abrirEnvio();

    await userEvent.type(within(dialogo).getByLabelText("Nome de referência"), "Backend Java");
    await userEvent.upload(within(dialogo).getByLabelText("Arquivo PDF"), pdf());
    await userEvent.click(within(dialogo).getByRole("button", { name: "Enviar" }));

    expect(await screen.findByText("Backend Java")).toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(recebidos[0]).toMatchObject({
      perfil_identificador: "adriano",
      nome_referencia: "Backend Java",
    });
    expect((recebidos[0] as { pdf_base64: string }).pdf_base64).not.toBe("");
  });

  it("valida nome, tipo e tamanho do arquivo antes de enviar", async () => {
    const { recebidos } = servirBiblioteca([]);
    renderizarApp({ caminho: "/curriculos", perfil: "adriano" });
    const dialogo = await abrirEnvio();

    await userEvent.click(within(dialogo).getByRole("button", { name: "Enviar" }));

    expect(within(dialogo).getByLabelText("Nome de referência")).toHaveAccessibleDescription(
      "Informe um nome de referência.",
    );
    expect(within(dialogo).getByLabelText("Arquivo PDF")).toHaveAccessibleDescription(
      /Escolha um arquivo PDF\./,
    );

    await userEvent.upload(within(dialogo).getByLabelText("Arquivo PDF"), pdf(5 * 1024 * 1024 + 1));
    await userEvent.click(within(dialogo).getByRole("button", { name: "Enviar" }));

    expect(within(dialogo).getByLabelText("Arquivo PDF")).toHaveAccessibleDescription(
      /mais de 5 MB/,
    );
    expect(recebidos).toHaveLength(0);
  });

  it("com 10 currículos desabilita o envio e explica o limite", async () => {
    servirBiblioteca(Array.from({ length: 10 }, (_, indice) => curriculo(indice + 1)));

    renderizarApp({ caminho: "/curriculos", perfil: "adriano" });

    expect(await screen.findByText(/Você atingiu o limite de 10 currículos/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Enviar currículo" })).toBeDisabled();
  });

  it("mostra a mensagem do backend quando o envio é recusado", async () => {
    servirBiblioteca([]);
    servidorApi.use(
      http.post(`${API_TESTE}/v1/curriculos`, () =>
        HttpResponse.json(
          {
            type: "t",
            title: "Erro",
            status: 422,
            detail: "Limite de 10 currículos salvos atingido.",
            instance: "i",
          },
          { status: 422 },
        ),
      ),
    );
    renderizarApp({ caminho: "/curriculos", perfil: "adriano" });
    const dialogo = await abrirEnvio();

    await userEvent.type(within(dialogo).getByLabelText("Nome de referência"), "Outro");
    await userEvent.upload(within(dialogo).getByLabelText("Arquivo PDF"), pdf());
    await userEvent.click(within(dialogo).getByRole("button", { name: "Enviar" }));

    expect(
      await within(dialogo).findByText("Limite de 10 currículos salvos atingido."),
    ).toBeInTheDocument();
  });

  it("remove depois de confirmar e atualiza a lista", async () => {
    servirBiblioteca([curriculo(1)]);
    renderizarApp({ caminho: "/curriculos", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("button", { name: "Remover Currículo 1" }));
    const confirmacao = screen.getByRole("dialog", { name: "Remover currículo?" });
    await userEvent.click(within(confirmacao).getByRole("button", { name: "Remover" }));

    expect(await screen.findByText("Nenhum currículo salvo")).toBeInTheDocument();
  });

  it("cancelar a remoção mantém o currículo", async () => {
    servirBiblioteca([curriculo(1)]);
    renderizarApp({ caminho: "/curriculos", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("button", { name: "Remover Currículo 1" }));
    await userEvent.click(screen.getByRole("button", { name: "Cancelar" }));

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.getByText("Currículo 1")).toBeInTheDocument();
  });

  it("baixa o PDF com o nome de referência", async () => {
    servirBiblioteca([curriculo(1)]);
    servidorApi.use(
      http.get(`${API_TESTE}/v1/curriculos/:id/conteudo`, () =>
        HttpResponse.json({
          id: "c1",
          nome_referencia: "Currículo 1",
          pdf_base64: btoa("%PDF-1.4"),
        }),
      ),
    );
    Object.assign(URL, { createObjectURL: vi.fn(() => "blob:x"), revokeObjectURL: vi.fn() });
    const nomes: string[] = [];
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (
      this: HTMLAnchorElement,
    ) {
      nomes.push(this.download);
    });
    renderizarApp({ caminho: "/curriculos", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("button", { name: "Baixar Currículo 1" }));

    await waitFor(() => expect(nomes).toEqual(["Currículo 1.pdf"]));
    vi.restoreAllMocks();
  });
});

describe("CurriculosPage — currículos adaptados", () => {
  it("lista os currículos adaptados com a vaga e um link para editar", async () => {
    servidorApi.use(
      http.get(`${API_TESTE}/v1/curriculos-adaptados`, () =>
        HttpResponse.json({ items: [CURRICULO_ADAPTADO_RESUMO], total: 1 }),
      ),
    );
    renderizarApp({ caminho: "/curriculos", perfil: "adriano" });

    const painel = await screen.findByRole("region", { name: "Currículos adaptados" });

    expect(await within(painel).findByText("Senior Java · Olist")).toBeInTheDocument();
    expect(
      within(painel).getByRole("link", {
        name: `Editar ${CURRICULO_ADAPTADO_RESUMO.nome_referencia}`,
      }),
    ).toHaveAttribute("href", "/curriculos-adaptados/ad1");
  });

  it("o link de editar abre a edição do currículo", async () => {
    servidorApi.use(
      http.get(`${API_TESTE}/v1/curriculos-adaptados`, () =>
        HttpResponse.json({ items: [CURRICULO_ADAPTADO_RESUMO], total: 1 }),
      ),
      http.get(`${API_TESTE}/v1/curriculos-adaptados/:id`, () =>
        HttpResponse.json({
          ...CURRICULO_ADAPTADO_RESUMO,
          descricao_vaga: "Vaga.",
          analise_vaga: { requisitos: [], ambiguidade: [], texto_original: "Vaga." },
          rascunho: {
            nome_completo: "Adriano Teixeira",
            secoes: [{ tipo: "PERFIL", titulo: "Perfil", conteudo: "Resumo." }],
            experiencias: null,
            competencias: [],
          },
        }),
      ),
    );
    renderizarApp({ caminho: "/curriculos", perfil: "adriano" });

    await userEvent.click(
      await screen.findByRole("link", {
        name: `Editar ${CURRICULO_ADAPTADO_RESUMO.nome_referencia}`,
      }),
    );

    expect(
      await screen.findByRole("heading", { name: "Edite o currículo adaptado" }),
    ).toBeInTheDocument();
  });

  it("sem currículos adaptados explica como criar o primeiro", async () => {
    renderizarApp({ caminho: "/curriculos", perfil: "adriano" });

    const painel = await screen.findByRole("region", { name: "Currículos adaptados" });

    expect(await within(painel).findByText("Nenhum currículo adaptado ainda")).toBeInTheDocument();
  });

  it("falha ao carregar a lista mostra o erro sem esconder a biblioteca de PDFs", async () => {
    servidorApi.use(
      http.get(`${API_TESTE}/v1/curriculos-adaptados`, () =>
        HttpResponse.json(
          { type: "t", title: "Erro", status: 500, detail: "Falha no servidor.", instance: "i" },
          { status: 500 },
        ),
      ),
    );
    renderizarApp({ caminho: "/curriculos", perfil: "adriano" });

    expect(await screen.findByText(/Falha no servidor\./)).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Biblioteca" })).toBeInTheDocument();
  });
});
