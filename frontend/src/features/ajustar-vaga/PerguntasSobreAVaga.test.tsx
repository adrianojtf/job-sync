import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { delay, http, HttpResponse } from "msw";
import { AVALIACAO_VAGA, CURRICULO_SALVO, servirDadosBase } from "../../test/fixtures";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

const RASCUNHO = {
  nome_completo: "Adriano Teixeira",
  email: "adriano@email.com",
  linkedin: "",
  secoes: [{ tipo: "PERFIL", titulo: "Perfil", conteudo: "Resumo adaptado pela IA." }],
  experiencias: [
    {
      cargo: "Dev Java",
      empresa: "Neoway",
      periodo: "2020-2024",
      conquistas: ["APIs em Java."],
      contexto: "Empresa de dados.",
    },
  ],
  titulo_experiencias: "Experiências",
};

const ADAPTADO = {
  rascunho: RASCUNHO,
  analise_vaga: { requisitos: [], ambiguidade: [], texto_original: "Java." },
  avaliacao_vaga: AVALIACAO_VAGA,
  status_avaliacao_vaga: "avaliada",
  avaliacoes_experiencias: [],
};

const LACUNAS = [
  { tema: "Atuação junto ao cliente", pergunta: "Você já atuou junto ao cliente na entrega?" },
  { tema: "Construção de MVPs", pergunta: "Você já construiu um MVP do zero?" },
];

interface Opcoes {
  lacunas?: { tema: string; pergunta: string }[];
  falhaLacunas?: boolean;
  atrasoLacunas?: number;
  parecidas?: string[];
  falhaRedacao?: boolean;
}

function servirFluxo({
  lacunas = LACUNAS,
  falhaLacunas = false,
  atrasoLacunas = 0,
  parecidas = [],
  falhaRedacao = false,
}: Opcoes = {}) {
  const chamadas: { rota: string; corpo: Record<string, unknown> }[] = [];
  const registrar = async (rota: string, request: Request) => {
    chamadas.push({ rota, corpo: (await request.json()) as Record<string, unknown> });
  };
  servidorApi.use(
    http.post(`${API_TESTE}/v1/curriculos/lacunas`, async ({ request }) => {
      await registrar("lacunas", request);
      if (atrasoLacunas) await delay(atrasoLacunas);
      if (falhaLacunas) {
        return HttpResponse.json(
          { type: "t", title: "Erro", status: 500, detail: "Falha interna", instance: "i" },
          { status: 500 },
        );
      }
      return HttpResponse.json({ lacunas });
    }),
    http.post(`${API_TESTE}/v1/curriculos/lacunas/conquista-rascunho`, async ({ request }) => {
      await registrar("rascunho-conquista", request);
      if (falhaRedacao) {
        return HttpResponse.json(
          { type: "t", title: "IA", status: 502, detail: "IA indisponível", instance: "i" },
          { status: 502 },
        );
      }
      return HttpResponse.json({ texto: "Atuei junto ao cliente na entrega de um MVP." });
    }),
    http.post(`${API_TESTE}/v1/perfil-estruturado/conquistas/parecidas`, async ({ request }) => {
      await registrar("parecidas", request);
      return HttpResponse.json({ parecidas });
    }),
    http.post(
      `${API_TESTE}/v1/perfil-estruturado/:perfil/experiencias/:indice/conquistas`,
      async ({ request, params }) => {
        await registrar(`adicionar:${String(params.perfil)}:${String(params.indice)}`, request);
        return HttpResponse.json({ perfil_identificador: "adriano" });
      },
    ),
    http.post(`${API_TESTE}/v1/curriculos/:id/rascunhos-adaptados`, async ({ request, params }) => {
      await registrar(`rascunhos:${String(params.id)}`, request);
      return HttpResponse.json(ADAPTADO);
    }),
  );
  return chamadas;
}

const rotas = (chamadas: { rota: string }[]) => chamadas.map((chamada) => chamada.rota);

async function pedirCurriculo() {
  await userEvent.type(await screen.findByLabelText("Título da vaga"), "Forward Deployed Engineer");
  await userEvent.type(screen.getByLabelText("Empresa"), "Barte");
  await userEvent.type(screen.getByLabelText("Descrição da vaga"), "Atuar junto ao cliente.");
  await waitFor(() => expect(screen.getByLabelText("Currículo base")).toHaveValue("perfil"));
  await userEvent.click(screen.getByRole("button", { name: "Gerar currículo adaptado" }));
}

const tituloPerguntas = () => screen.findByRole("heading", { name: "Perguntas sobre a vaga" });
const botao = (nome: string) => screen.getByRole("button", { name: nome });

async function responderSimComCaso() {
  await userEvent.click(botao("Sim"));
  await userEvent.selectOptions(screen.getByLabelText("Em qual experiência?"), "0");
  await userEvent.type(screen.getByLabelText("O que você fez?"), "Fiquei no cliente por 2 meses.");
  await userEvent.click(botao("Escrever conquista"));
  await screen.findByLabelText("Conquista");
}

describe("Perguntas sobre a vaga — antes de gerar", () => {
  it("sem lacunas, segue direto para a revisão sem mostrar as perguntas", async () => {
    servirDadosBase();
    const chamadas = servirFluxo({ lacunas: [] });
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });

    await pedirCurriculo();

    expect(
      await screen.findByRole("heading", { name: "Revise o currículo adaptado" }),
    ).toBeInTheDocument();
    expect(rotas(chamadas)).toEqual(["lacunas", "rascunhos:perfil-estruturado"]);
    expect(
      screen.queryByRole("heading", { name: "Perguntas sobre a vaga" }),
    ).not.toBeInTheDocument();
  });

  it("envia a vaga, o cargo, o idioma e o perfil ao buscar as lacunas", async () => {
    servirDadosBase();
    const chamadas = servirFluxo({ lacunas: [] });
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });

    await pedirCurriculo();

    await screen.findByRole("heading", { name: "Revise o currículo adaptado" });
    expect(chamadas[0]).toEqual({
      rota: "lacunas",
      corpo: {
        perfil_identificador: "adriano",
        descricao_vaga: "Atuar junto ao cliente.",
        cargo_alvo: "Forward Deployed Engineer",
        idioma_alvo: "pt",
      },
    });
  });

  it("se buscar as lacunas falhar, gera o currículo mesmo assim", async () => {
    servirDadosBase();
    const chamadas = servirFluxo({ falhaLacunas: true });
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });

    await pedirCurriculo();

    expect(
      await screen.findByRole("heading", { name: "Revise o currículo adaptado" }),
    ).toBeInTheDocument();
    expect(rotas(chamadas)).toContain("rascunhos:perfil-estruturado");
  });

  it("com lacunas, informa o número de perguntas e ainda não gera o currículo", async () => {
    servirDadosBase();
    const chamadas = servirFluxo();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });

    await pedirCurriculo();

    expect(await tituloPerguntas()).toBeInTheDocument();
    expect(screen.getByText("2 perguntas sobre a vaga")).toBeInTheDocument();
    expect(screen.getByText("Você já atuou junto ao cliente na entrega?")).toBeInTheDocument();
    expect(rotas(chamadas)).toEqual(["lacunas"]);
  });

  it("'Pular perguntas e gerar' gera o currículo sem salvar nada", async () => {
    servirDadosBase();
    const chamadas = servirFluxo();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await pedirCurriculo();
    await tituloPerguntas();

    await userEvent.click(botao("Pular perguntas e gerar"));

    expect(
      await screen.findByRole("heading", { name: "Revise o currículo adaptado" }),
    ).toBeInTheDocument();
    expect(rotas(chamadas)).toEqual(["lacunas", "rascunhos:perfil-estruturado"]);
  });

  it("o botão de pular fica visível enquanto as lacunas carregam e descarta as perguntas", async () => {
    servirDadosBase();
    const chamadas = servirFluxo({ atrasoLacunas: 300 });
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await pedirCurriculo();

    await userEvent.click(await screen.findByRole("button", { name: "Pular perguntas e gerar" }));

    expect(
      await screen.findByRole("heading", { name: "Revise o currículo adaptado" }),
    ).toBeInTheDocument();
    await delay(400);
    expect(
      screen.queryByRole("heading", { name: "Perguntas sobre a vaga" }),
    ).not.toBeInTheDocument();
    expect(rotas(chamadas).filter((rota) => rota.startsWith("rascunhos"))).toHaveLength(1);
  });

  it("não busca lacunas quando a fonte é um PDF da biblioteca", async () => {
    servirDadosBase();
    const chamadas = servirFluxo();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await userEvent.type(await screen.findByLabelText("Título da vaga"), "FDE");
    await userEvent.type(screen.getByLabelText("Empresa"), "Barte");
    await userEvent.type(screen.getByLabelText("Descrição da vaga"), "Atuar junto ao cliente.");
    await userEvent.selectOptions(
      await screen.findByLabelText("Currículo base"),
      CURRICULO_SALVO.id,
    );

    await userEvent.click(botao("Gerar currículo adaptado"));

    await screen.findByRole("heading", { name: "Revise o currículo adaptado" });
    expect(rotas(chamadas)).not.toContain("lacunas");
  });
});

describe("Perguntas sobre a vaga — respostas", () => {
  it("'Não' e 'Prefiro não responder' avançam sem chamar a IA nem salvar, e ao fim gera o currículo", async () => {
    servirDadosBase();
    const chamadas = servirFluxo();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await pedirCurriculo();
    await tituloPerguntas();

    await userEvent.click(botao("Não"));
    expect(await screen.findByText("Você já construiu um MVP do zero?")).toBeInTheDocument();
    await userEvent.click(botao("Prefiro não responder"));

    expect(
      await screen.findByRole("heading", { name: "Revise o currículo adaptado" }),
    ).toBeInTheDocument();
    expect(rotas(chamadas)).toEqual(["lacunas", "rascunhos:perfil-estruturado"]);
  });

  it("'Sim' pede a experiência e o caso antes de escrever a conquista", async () => {
    servirDadosBase();
    servirFluxo();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await pedirCurriculo();
    await tituloPerguntas();

    await userEvent.click(botao("Sim"));

    expect(botao("Escrever conquista")).toBeDisabled();
    await userEvent.selectOptions(screen.getByLabelText("Em qual experiência?"), "0");
    expect(botao("Escrever conquista")).toBeDisabled();
    await userEvent.type(screen.getByLabelText("O que você fez?"), "Fiquei no cliente.");
    expect(botao("Escrever conquista")).toBeEnabled();
  });

  it("escreve a conquista a partir do caso e mostra o texto para revisão", async () => {
    servirDadosBase();
    const chamadas = servirFluxo();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await pedirCurriculo();
    await tituloPerguntas();

    await responderSimComCaso();

    expect(screen.getByLabelText("Conquista")).toHaveValue(
      "Atuei junto ao cliente na entrega de um MVP.",
    );
    expect(chamadas.find((c) => c.rota === "rascunho-conquista")?.corpo).toEqual({
      perfil_identificador: "adriano",
      tema: "Atuação junto ao cliente",
      pergunta: "Você já atuou junto ao cliente na entrega?",
      caso: "Fiquei no cliente por 2 meses.",
      experiencia_indice: 0,
      idioma_alvo: "pt",
    });
  });

  it("aprova a conquista editada, salva na experiência e passa para a próxima pergunta", async () => {
    servirDadosBase();
    const chamadas = servirFluxo();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await pedirCurriculo();
    await tituloPerguntas();
    await responderSimComCaso();
    const campo = screen.getByLabelText("Conquista");
    await userEvent.clear(campo);
    await userEvent.type(campo, "Entreguei um MVP junto ao cliente.");

    await userEvent.click(botao("Aprovar e salvar"));

    expect(await screen.findByText("Você já construiu um MVP do zero?")).toBeInTheDocument();
    expect(chamadas.find((c) => c.rota === "parecidas")?.corpo).toEqual({
      texto: "Entreguei um MVP junto ao cliente.",
      conquistas: [],
    });
    expect(chamadas.find((c) => c.rota.startsWith("adicionar"))).toEqual({
      rota: "adicionar:adriano:0",
      corpo: { texto: "Entreguei um MVP junto ao cliente." },
    });
  });

  it("avisa quando a conquista se parece com outra e só salva depois de 'Aprovar mesmo assim'", async () => {
    servirDadosBase();
    const chamadas = servirFluxo({ parecidas: ["Atuei com o cliente em um MVP."] });
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await pedirCurriculo();
    await tituloPerguntas();
    await responderSimComCaso();

    await userEvent.click(botao("Aprovar e salvar"));

    expect(await screen.findByText(/se parece com outra já cadastrada/)).toBeInTheDocument();
    expect(
      screen.getByText("Atuei com o cliente em um MVP.", { selector: "li" }),
    ).toBeInTheDocument();
    expect(rotas(chamadas).some((rota) => rota.startsWith("adicionar"))).toBe(false);

    await userEvent.click(botao("Aprovar mesmo assim"));

    expect(await screen.findByText("Você já construiu um MVP do zero?")).toBeInTheDocument();
    expect(rotas(chamadas).some((rota) => rota.startsWith("adicionar"))).toBe(true);
  });

  it("mostra o erro quando a IA não consegue escrever a conquista e permite tentar de novo", async () => {
    servirDadosBase();
    servirFluxo({ falhaRedacao: true });
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await pedirCurriculo();
    await tituloPerguntas();

    await userEvent.click(botao("Sim"));
    await userEvent.selectOptions(screen.getByLabelText("Em qual experiência?"), "0");
    await userEvent.type(screen.getByLabelText("O que você fez?"), "Fiquei no cliente.");
    await userEvent.click(botao("Escrever conquista"));

    const pergunta = screen.getByRole("group", { name: "Pergunta 1 de 2" });
    expect(await within(pergunta).findByRole("alert")).toHaveTextContent("IA indisponível");
    await waitFor(() => expect(botao("Escrever conquista")).toBeEnabled());
  });

  it("as perguntas ficam acessíveis em um grupo com o número da pergunta", async () => {
    servirDadosBase();
    servirFluxo();
    renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
    await pedirCurriculo();
    await tituloPerguntas();

    const pergunta = screen.getByRole("group", { name: "Pergunta 1 de 2" });

    expect(
      within(pergunta).getByText("Você já atuou junto ao cliente na entrega?"),
    ).toBeInTheDocument();
  });
});
