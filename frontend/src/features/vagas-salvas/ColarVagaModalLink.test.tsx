import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import type { Vaga } from "../../api/tipos";
import { servirDadosBase } from "../../test/fixtures";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

const URL_DIGITADA =
  "https://br.linkedin.com/jobs/view/engenheiro-at-barte-4484559483?trk=public_jobs_topcard-title";
const URL_NORMALIZADA = "https://www.linkedin.com/jobs/view/4484559483/";
const DADOS_LIDOS = {
  cargo: "Engenheiro de Software Sênior",
  empresa: "Barte",
  local: "Brasil",
  descricao: "Sobre a Barte\n\n- Python\n- FastAPI",
  url: URL_NORMALIZADA,
  tipo_contratacao: "Tempo integral",
  senioridade: null,
  setor: "Serviços financeiros",
};
const PROBLEMA_BLOQUEIO = {
  type: "https://jobsync.com/erros/leitura-vaga-indisponivel",
  title: "Leitura da vaga indisponível",
  status: 502,
  detail: "O site não permitiu a leitura desta vaga. Cole o texto da vaga para continuar.",
  instance: `${API_TESTE}/v1/vagas/extracoes`,
};

function servirCaptura(extracao: () => Response) {
  const vagas: Vaga[] = [];
  const extracoes: Record<string, unknown>[] = [];
  const capturas: Record<string, unknown>[] = [];
  servirDadosBase();
  servidorApi.use(
    http.get(`${API_TESTE}/v1/vagas`, () =>
      HttpResponse.json({ items: vagas, total: vagas.length, limite: 100, offset: 0 }),
    ),
    http.post(`${API_TESTE}/v1/vagas/extracoes`, async ({ request }) => {
      extracoes.push((await request.json()) as Record<string, unknown>);
      return extracao();
    }),
    http.post(`${API_TESTE}/v1/vagas`, async ({ request }) => {
      const corpo = (await request.json()) as Record<string, string>;
      capturas.push(corpo);
      const nova: Vaga = {
        id: "v-novo",
        perfil_identificador: corpo.perfil_identificador!,
        texto_descricao: corpo.texto_descricao!,
        url_origem: corpo.url_origem ?? null,
        data_captura: "2026-11-06T12:00:00",
      };
      vagas.unshift(nova);
      return HttpResponse.json(nova, { status: 201 });
    }),
  );
  return { extracoes, capturas };
}

async function abrirModal() {
  renderizarApp({ caminho: "/vagas-salvas", perfil: "adriano" });
  await userEvent.click(await screen.findByRole("button", { name: "Colar vaga" }));
  return screen.getByRole("dialog", { name: "Colar vaga" });
}

describe("Colar vaga — link da vaga", () => {
  it("lê o link, mostra o rascunho para confirmar e só então salva com a URL normalizada", async () => {
    const { extracoes, capturas } = servirCaptura(() => HttpResponse.json(DADOS_LIDOS));
    const dialogo = await abrirModal();

    await userEvent.type(within(dialogo).getByLabelText("Link da vaga (opcional)"), URL_DIGITADA);
    await userEvent.click(within(dialogo).getByRole("button", { name: "Ler vaga" }));

    expect(
      await within(dialogo).findByText(
        "Dados lidos do link: título, empresa, local e descrição. Confira antes de continuar.",
      ),
    ).toBeInTheDocument();
    expect(within(dialogo).getByLabelText("Título (opcional)")).toHaveValue(
      "Engenheiro de Software Sênior",
    );
    expect(within(dialogo).getByLabelText("Empresa (opcional)")).toHaveValue("Barte");
    expect(within(dialogo).getByLabelText("Local (opcional)")).toHaveValue("Brasil");
    expect(within(dialogo).getByLabelText("Descrição da vaga")).toHaveValue(
      "Sobre a Barte\n\n- Python\n- FastAPI",
    );
    expect(within(dialogo).getByLabelText("Link da vaga (opcional)")).toHaveValue(URL_NORMALIZADA);
    expect(extracoes).toEqual([{ url: URL_DIGITADA }]);
    expect(capturas).toEqual([]);

    await userEvent.click(within(dialogo).getByRole("button", { name: "Salvar vaga" }));

    expect(await screen.findByText("Vaga salva.")).toBeInTheDocument();
    expect(capturas).toEqual([
      {
        perfil_identificador: "adriano",
        texto_descricao: "Sobre a Barte\n\n- Python\n- FastAPI",
        url_origem: URL_NORMALIZADA,
        cargo: "Engenheiro de Software Sênior",
        empresa: "Barte",
        local: "Brasil",
      },
    ]);
  });

  it("os campos lidos podem ser corrigidos antes de salvar", async () => {
    const { capturas } = servirCaptura(() => HttpResponse.json(DADOS_LIDOS));
    const dialogo = await abrirModal();
    await userEvent.type(within(dialogo).getByLabelText("Link da vaga (opcional)"), URL_DIGITADA);
    await userEvent.click(within(dialogo).getByRole("button", { name: "Ler vaga" }));
    await within(dialogo).findByText(/Dados lidos do link/);

    await userEvent.clear(within(dialogo).getByLabelText("Empresa (opcional)"));
    await userEvent.type(within(dialogo).getByLabelText("Empresa (opcional)"), "Barte Pagamentos");
    await userEvent.click(within(dialogo).getByRole("button", { name: "Salvar vaga" }));

    await screen.findByText("Vaga salva.");
    expect(capturas[0]).toMatchObject({ empresa: "Barte Pagamentos", cargo: DADOS_LIDOS.cargo });
  });

  it("Enter no campo do link lê a vaga em vez de salvar", async () => {
    const { extracoes, capturas } = servirCaptura(() => HttpResponse.json(DADOS_LIDOS));
    const dialogo = await abrirModal();

    await userEvent.type(
      within(dialogo).getByLabelText("Link da vaga (opcional)"),
      `${URL_DIGITADA}{Enter}`,
    );

    await within(dialogo).findByText(/Dados lidos do link/);
    expect(extracoes).toHaveLength(1);
    expect(capturas).toEqual([]);
  });

  it("quando o site bloqueia, mostra o motivo e ainda permite salvar com o texto colado", async () => {
    const { capturas } = servirCaptura(() => HttpResponse.json(PROBLEMA_BLOQUEIO, { status: 502 }));
    const dialogo = await abrirModal();

    await userEvent.type(within(dialogo).getByLabelText("Link da vaga (opcional)"), URL_DIGITADA);
    await userEvent.click(within(dialogo).getByRole("button", { name: "Ler vaga" }));
    expect(await within(dialogo).findByText(PROBLEMA_BLOQUEIO.detail)).toBeInTheDocument();
    await userEvent.type(within(dialogo).getByLabelText("Descrição da vaga"), "Backend Python");
    await userEvent.click(within(dialogo).getByRole("button", { name: "Salvar vaga" }));

    await screen.findByText("Vaga salva.");
    expect(capturas).toEqual([
      {
        perfil_identificador: "adriano",
        texto_descricao: "Backend Python",
        url_origem: URL_DIGITADA,
      },
    ]);
  });

  it("identifica título e empresa a partir do texto colado", async () => {
    const { extracoes } = servirCaptura(() =>
      HttpResponse.json({ ...DADOS_LIDOS, descricao: "Backend Python" }),
    );
    const dialogo = await abrirModal();
    await userEvent.type(within(dialogo).getByLabelText("Descrição da vaga"), "Backend Python");

    await userEvent.click(
      within(dialogo).getByRole("button", { name: "Preencher os campos pelo texto" }),
    );

    expect(await within(dialogo).findByText(/Dados identificados no texto/)).toBeInTheDocument();
    expect(within(dialogo).getByLabelText("Título (opcional)")).toHaveValue(
      "Engenheiro de Software Sênior",
    );
    expect(extracoes).toEqual([{ texto: "Backend Python" }]);
  });

  it("fechar o modal descarta o rascunho lido", async () => {
    servirCaptura(() => HttpResponse.json(DADOS_LIDOS));
    const dialogo = await abrirModal();
    await userEvent.type(within(dialogo).getByLabelText("Link da vaga (opcional)"), URL_DIGITADA);
    await userEvent.click(within(dialogo).getByRole("button", { name: "Ler vaga" }));
    await within(dialogo).findByText(/Dados lidos do link/);

    await userEvent.click(within(dialogo).getByRole("button", { name: "Cancelar" }));
    await userEvent.click(await screen.findByRole("button", { name: "Colar vaga" }));
    const novo = screen.getByRole("dialog", { name: "Colar vaga" });

    expect(within(novo).getByLabelText("Título (opcional)")).toHaveValue("");
    expect(within(novo).getByLabelText("Link da vaga (opcional)")).toHaveValue("");
    expect(within(novo).queryByText(/Dados lidos do link/)).not.toBeInTheDocument();
  });
});
