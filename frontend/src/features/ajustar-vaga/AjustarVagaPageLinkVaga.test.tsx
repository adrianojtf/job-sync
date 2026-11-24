import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { AVALIACAO_VAGA, servirDadosBase } from "../../test/fixtures";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

const URL_VAGA = "https://www.linkedin.com/jobs/view/4484559483/";
const DADOS_LIDOS = {
  cargo: "Engenheiro de Software Sênior",
  empresa: "Barte",
  local: "Brasil",
  descricao: "Sobre a Barte\n\n- Python\n- FastAPI",
  url: URL_VAGA,
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

function servirExtracao(resposta: () => Response | Promise<Response>) {
  const corpos: Record<string, unknown>[] = [];
  servirDadosBase();
  servidorApi.use(
    http.post(`${API_TESTE}/v1/vagas/extracoes`, async ({ request }) => {
      corpos.push((await request.json()) as Record<string, unknown>);
      return resposta();
    }),
  );
  return corpos;
}

async function abrirPagina() {
  renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
  return screen.findByLabelText("Link da vaga");
}

describe("Ajustar para uma vaga — link da vaga", () => {
  it("preenche título, empresa e descrição a partir do link e avisa o que foi lido", async () => {
    const corpos = servirExtracao(() => HttpResponse.json(DADOS_LIDOS));
    const campoLink = await abrirPagina();

    await userEvent.type(campoLink, URL_VAGA);
    await userEvent.click(screen.getByRole("button", { name: "Ler vaga" }));

    expect(
      await screen.findByText(
        "Dados lidos do link: título, empresa e descrição. Confira antes de continuar.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Título da vaga")).toHaveValue("Engenheiro de Software Sênior");
    expect(screen.getByLabelText("Empresa")).toHaveValue("Barte");
    expect(screen.getByLabelText("Descrição da vaga")).toHaveValue(
      "Sobre a Barte\n\n- Python\n- FastAPI",
    );
    expect(corpos).toEqual([{ url: URL_VAGA }]);
  });

  it("mantém o que já foi digitado quando a leitura não encontra título e empresa", async () => {
    servirExtracao(() => HttpResponse.json({ descricao: "Texto lido da página." }));
    const campoLink = await abrirPagina();
    await userEvent.type(screen.getByLabelText("Título da vaga"), "Meu título");
    await userEvent.type(screen.getByLabelText("Empresa"), "Minha empresa");

    await userEvent.type(campoLink, URL_VAGA);
    await userEvent.click(screen.getByRole("button", { name: "Ler vaga" }));

    expect(
      await screen.findByText(
        "Dados lidos do link: descrição. Não encontramos: título e empresa. Confira antes de continuar.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Título da vaga")).toHaveValue("Meu título");
    expect(screen.getByLabelText("Empresa")).toHaveValue("Minha empresa");
    expect(screen.getByLabelText("Descrição da vaga")).toHaveValue("Texto lido da página.");
  });

  it("os campos preenchidos continuam editáveis", async () => {
    servirExtracao(() => HttpResponse.json(DADOS_LIDOS));
    const campoLink = await abrirPagina();
    await userEvent.type(campoLink, URL_VAGA);
    await userEvent.click(screen.getByRole("button", { name: "Ler vaga" }));
    await screen.findByText(/Dados lidos do link/);

    await userEvent.clear(screen.getByLabelText("Empresa"));
    await userEvent.type(screen.getByLabelText("Empresa"), "Outra empresa");

    expect(screen.getByLabelText("Empresa")).toHaveValue("Outra empresa");
  });

  it("quando o site bloqueia, mostra o motivo e permite continuar colando o texto", async () => {
    const corpos: Record<string, unknown>[] = [];
    let chamada = 0;
    servirDadosBase();
    servidorApi.use(
      http.post(`${API_TESTE}/v1/vagas/extracoes`, async ({ request }) => {
        corpos.push((await request.json()) as Record<string, unknown>);
        chamada += 1;
        return chamada === 1
          ? HttpResponse.json(PROBLEMA_BLOQUEIO, { status: 502 })
          : HttpResponse.json({ ...DADOS_LIDOS, descricao: "Python e FastAPI." });
      }),
    );
    const campoLink = await abrirPagina();

    await userEvent.type(campoLink, URL_VAGA);
    await userEvent.click(screen.getByRole("button", { name: "Ler vaga" }));
    expect(await screen.findByText(PROBLEMA_BLOQUEIO.detail)).toBeInTheDocument();
    expect(screen.getByLabelText("Título da vaga")).toHaveValue("");

    await userEvent.type(screen.getByLabelText("Descrição da vaga"), "Python e FastAPI.");
    await userEvent.click(screen.getByRole("button", { name: "Preencher os campos pelo texto" }));

    expect(
      await screen.findByText(
        "Dados identificados no texto: título, empresa e descrição. Confira antes de continuar.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Título da vaga")).toHaveValue("Engenheiro de Software Sênior");
    expect(screen.getByLabelText("Empresa")).toHaveValue("Barte");
    expect(corpos).toEqual([{ url: URL_VAGA }, { texto: "Python e FastAPI." }]);
  });

  it("o botão de preencher pelo texto só vale com a descrição preenchida", async () => {
    servirExtracao(() => HttpResponse.json(DADOS_LIDOS));
    await abrirPagina();

    const botao = screen.getByRole("button", { name: "Preencher os campos pelo texto" });
    expect(botao).toBeDisabled();
    await userEvent.type(screen.getByLabelText("Descrição da vaga"), "Vaga de backend.");

    await waitFor(() => expect(botao).toBeEnabled());
  });

  it("Enter no campo do link lê a vaga sem tentar gerar o currículo", async () => {
    const corpos = servirExtracao(() => HttpResponse.json(DADOS_LIDOS));
    const campoLink = await abrirPagina();

    await userEvent.type(campoLink, `${URL_VAGA}{Enter}`);

    await screen.findByText(/Dados lidos do link/);
    expect(corpos).toEqual([{ url: URL_VAGA }]);
    expect(screen.queryByText("Informe o título da vaga.")).not.toBeInTheDocument();
  });
});

describe("Ajustar currículo para uma vaga — modal do menu com link da vaga", () => {
  async function abrirModal() {
    renderizarApp({ caminho: "/", perfil: "adriano" });
    await userEvent.click(await screen.findByRole("button", { name: "Ajustar para uma vaga" }));
    return screen.getByRole("dialog", { name: "Ajustar currículo para uma vaga" });
  }

  function servirModal(resposta: () => Response) {
    const corpos: Record<string, unknown>[] = [];
    servirDadosBase();
    servidorApi.use(
      http.post(`${API_TESTE}/v1/vagas/extracoes`, async ({ request }) => {
        corpos.push((await request.json()) as Record<string, unknown>);
        return resposta();
      }),
      http.post(`${API_TESTE}/v1/vagas/avaliacoes`, () => HttpResponse.json(AVALIACAO_VAGA)),
    );
    return corpos;
  }

  it("tem o campo Link da vaga, lê o link e leva os dados para a análise", async () => {
    const corpos = servirModal(() => HttpResponse.json(DADOS_LIDOS));
    const modal = await abrirModal();

    await userEvent.type(within(modal).getByLabelText("Link da vaga"), URL_VAGA);
    await userEvent.click(within(modal).getByRole("button", { name: "Ler vaga" }));

    expect(
      await within(modal).findByText(
        "Dados lidos do link: título, empresa e descrição. Confira antes de continuar.",
      ),
    ).toBeInTheDocument();
    expect(within(modal).getByLabelText("Título da vaga")).toHaveValue(
      "Engenheiro de Software Sênior",
    );
    expect(within(modal).getByLabelText("Empresa")).toHaveValue("Barte");
    expect(within(modal).getByLabelText("Descrição da vaga")).toHaveValue(
      "Sobre a Barte\n\n- Python\n- FastAPI",
    );
    expect(corpos).toEqual([{ url: URL_VAGA }]);

    await userEvent.click(within(modal).getByRole("button", { name: "Analisar vaga" }));

    expect(
      await screen.findByRole("heading", { level: 1, name: "Ajustar para uma vaga" }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Título da vaga")).toHaveValue("Engenheiro de Software Sênior");
    expect(screen.getByLabelText("Empresa", { exact: true })).toHaveValue("Barte");
    expect(await screen.findByRole("meter", { name: "Relevância" })).toBeInTheDocument();
  });

  it("quando o site bloqueia, mostra o motivo e continua pelo texto colado", async () => {
    let chamada = 0;
    servirDadosBase();
    servidorApi.use(
      http.post(`${API_TESTE}/v1/vagas/extracoes`, () => {
        chamada += 1;
        return chamada === 1
          ? HttpResponse.json(PROBLEMA_BLOQUEIO, { status: 502 })
          : HttpResponse.json({ ...DADOS_LIDOS, descricao: "Python e FastAPI." });
      }),
    );
    const modal = await abrirModal();

    await userEvent.type(within(modal).getByLabelText("Link da vaga"), URL_VAGA);
    await userEvent.click(within(modal).getByRole("button", { name: "Ler vaga" }));
    expect(await within(modal).findByText(PROBLEMA_BLOQUEIO.detail)).toBeInTheDocument();
    expect(
      within(modal).getByRole("button", { name: "Preencher os campos pelo texto" }),
    ).toBeDisabled();

    await userEvent.type(within(modal).getByLabelText("Descrição da vaga"), "Python e FastAPI.");
    await userEvent.click(
      within(modal).getByRole("button", { name: "Preencher os campos pelo texto" }),
    );

    expect(await within(modal).findByText(/Dados identificados no texto/)).toBeInTheDocument();
    expect(within(modal).getByLabelText("Título da vaga")).toHaveValue(
      "Engenheiro de Software Sênior",
    );
    expect(within(modal).getByLabelText("Empresa")).toHaveValue("Barte");
  });

  it("Enter no campo do link lê a vaga em vez de enviar o formulário", async () => {
    const corpos = servirModal(() => HttpResponse.json(DADOS_LIDOS));
    const modal = await abrirModal();

    await userEvent.type(within(modal).getByLabelText("Link da vaga"), `${URL_VAGA}{Enter}`);

    await within(modal).findByText(/Dados lidos do link/);
    expect(corpos).toHaveLength(1);
    expect(
      screen.getByRole("dialog", { name: "Ajustar currículo para uma vaga" }),
    ).toBeInTheDocument();
  });
});
