import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { HttpApiClient } from "../../api/http-api-client";
import type { ContextoVaga, RascunhoCurriculoAdaptado } from "../../api/tipos";
import { AppProviders } from "../../app/AppProviders";
import { API_TESTE, servidorApi } from "../../test/servidor-api";
import { RevisaoCurriculoAdaptado } from "./RevisaoCurriculoAdaptado";

const rascunhoDoPerfil: RascunhoCurriculoAdaptado = {
  nome_completo: "Ana Souza",
  email: "ana@ex.com",
  linkedin: "",
  secoes: [
    { tipo: "PERFIL", titulo: "Perfil", conteudo: "Resumo da IA." },
    { tipo: "TECNOLOGIAS", titulo: "Tecnologias", conteudo: "Linguagens: Java" },
    { tipo: "FORMACAO", titulo: "Formação acadêmica", conteudo: "ADS — Estácio" },
  ],
  experiencias: [
    {
      cargo: "Dev",
      empresa: "TechCorp",
      periodo: "2024",
      conquistas: ["Conquista da IA."],
      contexto: "Contexto da IA.",
    },
  ],
  titulo_experiencias: "Experiências",
};

const rascunhoDePdf: RascunhoCurriculoAdaptado = {
  nome_completo: "Ana Souza",
  secoes: [{ tipo: "EXPERIENCIAS", titulo: "Experiências", conteudo: "Dev — TechCorp" }],
  experiencias: null,
};

const contextoVaga: ContextoVaga = {
  descricao_vaga: "Vaga Java com Kafka.",
  idioma_alvo: "en",
  analise_vaga: {
    requisitos: [
      { nome: "Java", categoria: "TECNOLOGIA", tipo: "EXPLICITO", origem: "DESCRICAO_VAGA" },
    ],
    ambiguidade: [],
    texto_original: "Vaga Java com Kafka.",
  },
};

function servirSugestoes() {
  const pedidos: { rota: string; corpo: Record<string, unknown> }[] = [];
  servidorApi.use(
    http.post(`${API_TESTE}/v1/secoes-curriculo/sugestoes`, async ({ request }) => {
      const corpo = (await request.json()) as { secao: { tipo: string } };
      pedidos.push({ rota: "secao", corpo });
      return HttpResponse.json({
        conteudo_sugerido:
          corpo.secao.tipo === "TECNOLOGIAS"
            ? "Linguagens: Java, Go\nFerramentas: Git"
            : "Seção sugerida pela IA.",
        foco: "aderencia_vaga",
      });
    }),
    http.post(`${API_TESTE}/v1/experiencias-adaptadas/sugestoes`, async ({ request }) => {
      pedidos.push({
        rota: "experiencia",
        corpo: (await request.json()) as Record<string, unknown>,
      });
      return HttpResponse.json({
        conquistas: ["Conquista sugerida.", "Outra conquista sugerida."],
        contexto: "Contexto sugerido pela IA.",
        foco: "aderencia_vaga",
      });
    }),
  );
  return pedidos;
}

function renderizar(props: Partial<Parameters<typeof RevisaoCurriculoAdaptado>[0]> = {}) {
  const aoConfirmar = vi.fn();
  const aoVoltar = vi.fn();
  const resultado = render(
    <AppProviders apiClient={new HttpApiClient({ baseUrl: API_TESTE })}>
      <RevisaoCurriculoAdaptado
        rascunho={rascunhoDoPerfil}
        contextoVaga={contextoVaga}
        gerando={false}
        aoConfirmar={aoConfirmar}
        aoVoltar={aoVoltar}
        {...props}
      />
    </AppProviders>,
  );
  return { aoConfirmar, aoVoltar, ...resultado };
}

describe("RevisaoCurriculoAdaptado", () => {
  it("mostra todas as seções do rascunho, editáveis ao mesmo tempo", () => {
    renderizar();

    expect(screen.getByRole("heading", { name: "Revise o currículo adaptado" })).toHaveFocus();
    expect(screen.getByLabelText("Nome completo")).toHaveValue("Ana Souza");
    expect(screen.getByLabelText("Resumo profissional")).toHaveValue("Resumo da IA.");
    expect(screen.getByLabelText("Principais realizações")).toHaveValue("Conquista da IA.");
    expect(screen.getByLabelText("Contexto")).toHaveValue("Contexto da IA.");
    expect(screen.queryByLabelText("Descrição")).not.toBeInTheDocument();
    expect(
      within(screen.getByRole("group", { name: "Linguagens" })).getByText("Java"),
    ).toBeInTheDocument();
    expect(screen.queryByLabelText("Tecnologias")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Formação")).toHaveValue("ADS — Estácio");
    expect(screen.queryByRole("heading", { name: "Certificações" })).not.toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: /confirmar e gerar pdf/i })).toHaveLength(1);
  });

  it("confirma uma única vez com o estado editado de todas as seções", async () => {
    const usuario = userEvent.setup();
    const { aoConfirmar } = renderizar();

    await usuario.clear(screen.getByLabelText("Resumo profissional"));
    await usuario.type(screen.getByLabelText("Resumo profissional"), "Resumo revisado.");
    await usuario.clear(screen.getByLabelText("Principais realizações"));
    await usuario.type(screen.getByLabelText("Principais realizações"), "Primeira.{Enter}Segunda.");
    await usuario.clear(screen.getByLabelText("Contexto"));
    await usuario.type(screen.getByLabelText("Contexto"), "Contexto revisado.");
    await usuario.clear(screen.getByLabelText("Formação"));
    expect(screen.getByText("Alterações não confirmadas")).toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Confirmar e gerar PDF" }));

    expect(aoConfirmar).toHaveBeenCalledTimes(1);
    expect(aoConfirmar).toHaveBeenCalledWith({
      ...rascunhoDoPerfil,
      secoes: [
        { tipo: "PERFIL", titulo: "Perfil", conteudo: "Resumo revisado." },
        { tipo: "FORMACAO", titulo: "Formação acadêmica", conteudo: "" },
      ],
      competencias: [{ nome: "Linguagens", tags: ["Java"] }],
      titulo_competencias: "Tecnologias",
      experiencias: [
        {
          cargo: "Dev",
          empresa: "TechCorp",
          periodo: "2024",
          conquistas: ["Primeira.", "Segunda."],
          contexto: "Contexto revisado.",
          responsabilidades: [],
          skills: [],
        },
      ],
    });
  });

  describe("lacunas de tecnologia da vaga (JOB-0044)", () => {
    const comLacunas = { ...rascunhoDoPerfil, lacunas_tecnologia: ["Kafka", "RabbitMQ"] };
    const aviso = () =>
      screen.queryByRole("region", { name: "Tecnologias da vaga fora das competências" });

    it("mostra as lacunas do rascunho com a orientação de adicionar a tag", () => {
      renderizar({ rascunho: comLacunas });

      expect(aviso()).toHaveTextContent("Kafka, RabbitMQ");
    });

    it("não mostra o aviso quando não há lacunas", () => {
      renderizar();

      expect(aviso()).not.toBeInTheDocument();
    });

    it("a lacuna some quando o usuário adiciona a tag, sem diferenciar maiúsculas e minúsculas", async () => {
      const usuario = userEvent.setup();
      renderizar({ rascunho: comLacunas });

      await usuario.type(
        within(screen.getByRole("group", { name: "Linguagens" })).getByRole("textbox", {
          name: "Nova tag",
        }),
        "kafka{Enter}",
      );

      expect(aviso()).toHaveTextContent("RabbitMQ");
      expect(aviso()).not.toHaveTextContent("Kafka");
    });

    it("o aviso desaparece quando todas as lacunas viram tags", async () => {
      const usuario = userEvent.setup();
      renderizar({ rascunho: { ...rascunhoDoPerfil, lacunas_tecnologia: ["Kafka"] } });

      await usuario.type(
        within(screen.getByRole("group", { name: "Linguagens" })).getByRole("textbox", {
          name: "Nova tag",
        }),
        "Kafka{Enter}",
      );

      expect(aviso()).not.toBeInTheDocument();
    });

    it("na edição de um currículo salvo o aviso não aparece", () => {
      renderizar({ rascunho: comLacunas, modo: "edicao" });

      expect(aviso()).not.toBeInTheDocument();
    });
  });

  describe("competências por categoria e tag", () => {
    it("o bloco chama-se Competências", () => {
      renderizar();

      expect(screen.getByRole("region", { name: "Competências" })).toBeInTheDocument();
      expect(
        screen.queryByRole("region", { name: "Tecnologias e ferramentas" }),
      ).not.toBeInTheDocument();
    });

    it("a tag removida e a criada seguem na confirmação, e a seção de texto não é enviada", async () => {
      const usuario = userEvent.setup();
      const { aoConfirmar } = renderizar();

      const linguagens = within(screen.getByRole("group", { name: "Linguagens" }));
      await usuario.click(linguagens.getByRole("button", { name: "Remover Java" }));
      await usuario.type(linguagens.getByRole("textbox", { name: "Nova tag" }), "Kotlin{Enter}");
      await usuario.click(screen.getByRole("button", { name: "Confirmar e gerar PDF" }));

      const enviado = aoConfirmar.mock.calls[0]?.[0];
      expect(enviado.competencias).toEqual([{ nome: "Linguagens", tags: ["Kotlin"] }]);
      expect(enviado.secoes.map((secao: { tipo: string }) => secao.tipo)).toEqual([
        "PERFIL",
        "FORMACAO",
      ]);
    });

    it("cria uma categoria nova, com nome e tags, e a envia na confirmação", async () => {
      const usuario = userEvent.setup();
      const { aoConfirmar } = renderizar();

      await usuario.click(screen.getByRole("button", { name: "Adicionar categoria" }));
      const [, nova] = screen.getAllByRole("group", { name: /Linguagens|Categoria 2/ });
      await usuario.type(
        within(nova!).getByRole("textbox", { name: "Nome da categoria" }),
        "Ferramentas",
      );
      await usuario.type(
        within(screen.getByRole("group", { name: "Ferramentas" })).getByRole("textbox", {
          name: "Nova tag",
        }),
        "Git{Enter}",
      );
      await usuario.click(screen.getByRole("button", { name: "Confirmar e gerar PDF" }));

      expect(aoConfirmar.mock.calls[0]?.[0].competencias).toEqual([
        { nome: "Linguagens", tags: ["Java"] },
        { nome: "Ferramentas", tags: ["Git"] },
      ]);
    });

    it("excluir todas as categorias envia competências vazias", async () => {
      const usuario = userEvent.setup();
      const { aoConfirmar } = renderizar();

      await usuario.click(screen.getByRole("button", { name: "Excluir categoria Linguagens" }));
      await usuario.click(screen.getByRole("button", { name: "Confirmar e gerar PDF" }));

      expect(aoConfirmar.mock.calls[0]?.[0].competencias).toEqual([]);
    });

    it("editar as tags marca o formulário como alterado", async () => {
      const usuario = userEvent.setup();
      renderizar();

      await usuario.click(
        within(screen.getByRole("group", { name: "Linguagens" })).getByRole("button", {
          name: "Remover Java",
        }),
      );

      expect(screen.getByText("Alterações não confirmadas")).toBeInTheDocument();
    });

    it("com o rascunho de PDF sem tecnologias, permite criar a primeira categoria", () => {
      renderizar({ rascunho: rascunhoDePdf });

      expect(screen.getByText("Nenhuma categoria adicionada.")).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Adicionar categoria" })).toBeInTheDocument();
    });
  });

  it("não confirma com erros de validação e indica o campo", async () => {
    const usuario = userEvent.setup();
    const { aoConfirmar } = renderizar();

    await usuario.clear(screen.getByLabelText("Nome completo"));
    await usuario.clear(screen.getByLabelText("Cargo"));
    await usuario.click(screen.getByRole("button", { name: "Confirmar e gerar PDF" }));

    expect(aoConfirmar).not.toHaveBeenCalled();
    expect(screen.getByText("Informe o nome completo.")).toBeInTheDocument();
    expect(screen.getByText("Informe o cargo.")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome completo")).toHaveFocus();
  });

  it("permite adicionar e remover experiências no rascunho", async () => {
    const usuario = userEvent.setup();
    const { aoConfirmar } = renderizar();

    await usuario.click(screen.getByRole("button", { name: "Remover experiência 1" }));
    await usuario.click(screen.getByRole("button", { name: "Adicionar experiência" }));
    await usuario.type(screen.getByLabelText("Empresa"), "Starian");
    await usuario.type(screen.getByLabelText("Cargo"), "Engenheira");
    await usuario.click(screen.getByRole("button", { name: "Confirmar e gerar PDF" }));

    expect(aoConfirmar.mock.calls[0]?.[0].experiencias).toEqual([
      {
        cargo: "Engenheira",
        empresa: "Starian",
        periodo: "",
        conquistas: [],
        contexto: "",
        responsabilidades: [],
        skills: [],
      },
    ]);
  });

  it("mostra as experiências como texto quando a fonte é PDF", () => {
    renderizar({ rascunho: rascunhoDePdf });

    expect(screen.getByLabelText("Experiências")).toHaveValue("Dev — TechCorp");
    expect(screen.queryByRole("button", { name: "Adicionar experiência" })).not.toBeInTheDocument();
  });

  it("não exige e-mail, que pode faltar em um currículo vindo de PDF", async () => {
    const usuario = userEvent.setup();
    const { aoConfirmar } = renderizar({ rascunho: rascunhoDePdf });

    await usuario.click(screen.getByRole("button", { name: "Confirmar e gerar PDF" }));

    expect(aoConfirmar).toHaveBeenCalledTimes(1);
  });

  it("volta direto para a vaga quando não há alterações", async () => {
    const usuario = userEvent.setup();
    const { aoVoltar } = renderizar();

    await usuario.click(screen.getByRole("button", { name: "Voltar para a vaga" }));

    expect(aoVoltar).toHaveBeenCalledTimes(1);
  });

  it("pede confirmação antes de descartar alterações ao voltar", async () => {
    const usuario = userEvent.setup();
    const { aoVoltar } = renderizar();

    await usuario.type(screen.getByLabelText("Resumo profissional"), " Editado.");
    await usuario.click(screen.getByRole("button", { name: "Voltar para a vaga" }));
    const dialogo = screen.getByRole("dialog", { name: "Descartar a revisão?" });
    await usuario.click(within(dialogo).getByRole("button", { name: "Cancelar" }));

    expect(aoVoltar).not.toHaveBeenCalled();
    expect(screen.getByLabelText("Resumo profissional")).toHaveValue("Resumo da IA. Editado.");

    await usuario.click(screen.getByRole("button", { name: "Voltar para a vaga" }));
    await usuario.click(screen.getByRole("button", { name: "Descartar alterações" }));

    expect(aoVoltar).toHaveBeenCalledTimes(1);
  });

  it("preserva as edições quando a geração do PDF falha", async () => {
    const usuario = userEvent.setup();
    const { rerender, aoConfirmar, aoVoltar } = renderizar();

    await usuario.type(screen.getByLabelText("Resumo profissional"), " Editado.");
    rerender(
      <AppProviders apiClient={new HttpApiClient({ baseUrl: API_TESTE })}>
        <RevisaoCurriculoAdaptado
          rascunho={rascunhoDoPerfil}
          contextoVaga={contextoVaga}
          gerando={false}
          erro="Serviço indisponível."
          aoConfirmar={aoConfirmar}
          aoVoltar={aoVoltar}
        />
      </AppProviders>,
    );

    expect(screen.getByText(/Serviço indisponível\./)).toHaveTextContent(
      "Não foi possível gerar o PDF: Serviço indisponível.",
    );
    expect(screen.getByLabelText("Resumo profissional")).toHaveValue("Resumo da IA. Editado.");
  });

  it("avisa que a IA pode ter estimado números quando as experiências são estruturadas", () => {
    renderizar();

    expect(screen.getByText(/A IA pode ter estimado métricas e volumes/)).toBeInTheDocument();
  });

  it("o aviso pede para conferir trocas de tecnologia e atividades citadas pela IA", () => {
    renderizar();

    expect(screen.getByText(/A IA pode ter estimado métricas e volumes/)).toHaveTextContent(
      "defender em entrevista",
    );
  });

  it("mostra as trocas de tecnologia feitas pela IA", () => {
    renderizar({
      rascunho: {
        ...rascunhoDoPerfil,
        ajustes_tecnologia: [
          {
            indice_experiencia: 0,
            cargo: "Dev",
            empresa: "TechCorp",
            original: "React",
            alvo: "Angular",
          },
        ],
      },
    });

    expect(screen.getByRole("list", { name: "Ajustes de tecnologia" })).toHaveTextContent(
      "React → Angular em Dev — TechCorp",
    );
  });

  it("não mostra a lista de ajustes quando não houve troca", () => {
    renderizar();

    expect(screen.queryByRole("list", { name: "Ajustes de tecnologia" })).not.toBeInTheDocument();
  });

  it("não mostra o aviso de números estimados quando a fonte é PDF", () => {
    renderizar({ rascunho: rascunhoDePdf });

    expect(screen.queryByText(/A IA pode ter estimado métricas e volumes/)).not.toBeInTheDocument();
  });

  it("avalia a experiência com o texto composto de conquistas e contexto atuais", async () => {
    const usuario = userEvent.setup();
    let corpoRecebido: unknown;
    const dimensao = (score: number) => ({ score, nivel: "adequado", confianca: 0.9 });
    servidorApi.use(
      http.post(`${API_TESTE}/v1/experiencias-profissionais/avaliacoes`, async ({ request }) => {
        corpoRecebido = await request.json();
        return HttpResponse.json({
          score: 74,
          clareza_escrita: dimensao(80),
          qualidade_detalhe: dimensao(60),
          aderencia_vaga: dimensao(70),
          consistencia_textual: dimensao(86),
        });
      }),
    );
    renderizar();
    await usuario.type(
      screen.getByLabelText("Principais realizações"),
      "{Enter}Segunda conquista.",
    );

    await usuario.click(screen.getByRole("button", { name: "Avaliar experiência 1" }));
    const dialogo = screen.getByRole("dialog", { name: "Avaliar experiência" });
    await usuario.type(within(dialogo).getByLabelText("Descrição da vaga"), "Vaga Java");
    await usuario.click(within(dialogo).getByRole("button", { name: "Avaliar" }));
    await within(dialogo).findByText("74");

    expect(corpoRecebido).toEqual({
      experiencia: {
        empresa: "TechCorp",
        cargo: "Dev",
        periodo: "2024",
        descricao: "- Conquista da IA.\n- Segunda conquista.\nContexto da IA.",
      },
      descricao_vaga: "Vaga Java",
    });
  });

  describe("sugestões de IA", () => {
    const botao = (rotulo: string) =>
      screen.getByRole("button", { name: `Sugestões de IA para ${rotulo}` });

    it("oferece sugestão no resumo, nas tecnologias e em cada experiência, mas não na formação", () => {
      renderizar();

      expect(botao("resumo")).toBeInTheDocument();
      expect(botao("tecnologias")).toBeInTheDocument();
      expect(botao("experiência 1")).toBeInTheDocument();
      expect(screen.getAllByRole("button", { name: /^Sugestões de IA/ })).toHaveLength(3);
    });

    it("oferece sugestão no bloco de experiências em texto quando a fonte é PDF", () => {
      renderizar({ rascunho: rascunhoDePdf });

      expect(botao("experiências")).toBeInTheDocument();
      expect(botao("tecnologias")).toBeInTheDocument();
      expect(screen.getAllByRole("button", { name: /^Sugestões de IA/ })).toHaveLength(3);
    });

    it("envia o resumo editado com o contexto da vaga e só o altera ao aplicar", async () => {
      const usuario = userEvent.setup();
      const pedidos = servirSugestoes();
      renderizar();
      await usuario.type(screen.getByLabelText("Resumo profissional"), " Editado.");

      await usuario.click(botao("resumo"));
      await screen.findByText("Seção sugerida pela IA.");

      expect(pedidos[0]).toEqual({
        rota: "secao",
        corpo: {
          secao: { tipo: "PERFIL", titulo: "Perfil", conteudo: "Resumo da IA. Editado." },
          contexto_vaga: contextoVaga,
          refino: { tentativa: 1, sugestoes_anteriores: [] },
        },
      });
      expect(screen.getByLabelText("Resumo profissional")).toHaveValue("Resumo da IA. Editado.");

      await usuario.click(screen.getByRole("button", { name: "Aplicar sugestão em resumo" }));

      expect(screen.getByLabelText("Resumo profissional")).toHaveValue("Seção sugerida pela IA.");
      expect(screen.getByLabelText("Resumo profissional")).toHaveFocus();
      expect(screen.getByText("Alterações não confirmadas")).toBeInTheDocument();
    });

    it("sugere para as tecnologias sem alterar as outras seções", async () => {
      const usuario = userEvent.setup();
      const pedidos = servirSugestoes();
      renderizar();

      await usuario.click(botao("tecnologias"));
      await screen.findByText(/Ferramentas: Git/);
      await usuario.click(screen.getByRole("button", { name: "Aplicar sugestão em tecnologias" }));

      expect(pedidos[0]?.corpo).toMatchObject({
        secao: { tipo: "TECNOLOGIAS", conteudo: "Linguagens: Java" },
      });
      const linguagens = within(screen.getByRole("group", { name: "Linguagens" }));
      expect(linguagens.getByText("Go")).toBeInTheDocument();
      expect(
        within(screen.getByRole("group", { name: "Ferramentas" })).getByText("Git"),
      ).toBeInTheDocument();
      expect(screen.getByLabelText("Resumo profissional")).toHaveValue("Resumo da IA.");
      expect(screen.getByLabelText("Formação")).toHaveValue("ADS — Estácio");
    });

    it("sugere conquistas e contexto novos, com a vaga, e aplica os dois campos de uma vez", async () => {
      const usuario = userEvent.setup();
      const pedidos = servirSugestoes();
      renderizar();
      await usuario.type(screen.getByLabelText("Principais realizações"), " Editada.");
      await usuario.type(screen.getByLabelText("Contexto"), " Editado.");

      await usuario.click(botao("experiência 1"));
      const painel = await screen.findByRole("region", {
        name: "Sugestão da IA para experiência 1",
      });

      expect(pedidos[0]).toEqual({
        rota: "experiencia",
        corpo: {
          experiencia: {
            cargo: "Dev",
            empresa: "TechCorp",
            periodo: "2024",
            conquistas: ["Conquista da IA. Editada."],
            contexto: "Contexto da IA. Editado.",
            responsabilidades: [],
            skills: [],
          },
          contexto_vaga: contextoVaga,
          refino: { tentativa: 1, sugestoes_anteriores: [] },
        },
      });
      expect(painel).toHaveTextContent("Foco: aderência à vaga");
      expect(painel.querySelector("p:last-of-type")?.textContent).toBe(
        "- Conquista sugerida.\n- Outra conquista sugerida.\nContexto: Contexto sugerido pela IA.",
      );
      expect(screen.getByLabelText("Principais realizações")).toHaveValue(
        "Conquista da IA. Editada.",
      );

      await usuario.click(
        screen.getByRole("button", { name: "Aplicar sugestão em experiência 1" }),
      );

      expect(screen.getByLabelText("Principais realizações")).toHaveValue(
        "Conquista sugerida.\nOutra conquista sugerida.",
      );
      expect(screen.getByLabelText("Contexto")).toHaveValue("Contexto sugerido pela IA.");
      expect(screen.getByLabelText("Cargo")).toHaveValue("Dev");
      expect(screen.getByLabelText("Principais realizações")).toHaveFocus();
      expect(screen.getByText("Alterações não confirmadas")).toBeInTheDocument();
    });

    it("descartar a sugestão da experiência não altera os campos", async () => {
      const usuario = userEvent.setup();
      servirSugestoes();
      renderizar();

      await usuario.click(botao("experiência 1"));
      await usuario.click(
        await screen.findByRole("button", { name: "Descartar sugestão de experiência 1" }),
      );

      expect(screen.getByLabelText("Principais realizações")).toHaveValue("Conquista da IA.");
      expect(screen.getByLabelText("Contexto")).toHaveValue("Contexto da IA.");
    });

    it("a sugestão da experiência fica desabilitada sem conquistas nem contexto", async () => {
      const usuario = userEvent.setup();
      renderizar();

      await usuario.clear(screen.getByLabelText("Principais realizações"));
      await usuario.clear(screen.getByLabelText("Contexto"));

      expect(botao("experiência 1")).toBeDisabled();
    });

    it("mostra o erro da sugestão da experiência e mantém os textos", async () => {
      const usuario = userEvent.setup();
      servidorApi.use(
        http.post(`${API_TESTE}/v1/experiencias-adaptadas/sugestoes`, () =>
          HttpResponse.json(
            { type: "t", title: "Erro", status: 502, detail: "IA fora do ar.", instance: "i" },
            { status: 502 },
          ),
        ),
      );
      renderizar();

      await usuario.click(botao("experiência 1"));

      expect(await screen.findByText(/IA fora do ar\./)).toBeInTheDocument();
      expect(screen.getByLabelText("Principais realizações")).toHaveValue("Conquista da IA.");
    });

    it("mostra o erro no bloco e mantém o texto quando a IA falha", async () => {
      const usuario = userEvent.setup();
      servidorApi.use(
        http.post(`${API_TESTE}/v1/secoes-curriculo/sugestoes`, () =>
          HttpResponse.json(
            { type: "t", title: "Erro", status: 502, detail: "IA fora do ar.", instance: "i" },
            { status: 502 },
          ),
        ),
      );
      renderizar();

      await usuario.click(botao("resumo"));

      expect(await screen.findByText(/IA fora do ar\./)).toBeInTheDocument();
      expect(screen.getByLabelText("Resumo profissional")).toHaveValue("Resumo da IA.");
    });
  });
});

describe("RevisaoCurriculoAdaptado — quatro blocos", () => {
  const rascunhoComBlocos: RascunhoCurriculoAdaptado = {
    ...rascunhoDoPerfil,
    experiencias: [
      {
        cargo: "Dev",
        empresa: "TechCorp",
        periodo: "2024",
        conquistas: ["Atendi 1.000 usuários."],
        contexto: "ERP financeiro.",
        responsabilidades: ["Projetar telas", "Testar entregas"],
        skills: ["Java", "SQL"],
      },
    ],
  };
  const skills = () => within(screen.getByRole("group", { name: "Skills da experiência 1" }));

  it("mostra contexto, responsabilidades, realizações e skills da experiência", () => {
    renderizar({ rascunho: rascunhoComBlocos });

    expect(screen.getByLabelText("Contexto")).toHaveValue("ERP financeiro.");
    expect(screen.getByLabelText("Principais responsabilidades")).toHaveValue(
      "Projetar telas\nTestar entregas",
    );
    expect(screen.getByLabelText("Principais realizações")).toHaveValue("Atendi 1.000 usuários.");
    expect(skills().getByText("Java")).toBeInTheDocument();
    expect(skills().getByText("SQL")).toBeInTheDocument();
  });

  it("edita responsabilidades e skills e confirma com os quatro blocos", async () => {
    const usuario = userEvent.setup();
    const { aoConfirmar } = renderizar({ rascunho: rascunhoComBlocos });

    await usuario.type(
      screen.getByLabelText("Principais responsabilidades"),
      "{Enter}Mentorar o time",
    );
    await usuario.type(skills().getByLabelText("Nova skill"), "Flyway{Enter}");
    await usuario.click(skills().getByRole("button", { name: "Remover SQL" }));
    await usuario.click(screen.getByRole("button", { name: "Confirmar e gerar PDF" }));

    expect(aoConfirmar.mock.calls[0]?.[0].experiencias).toEqual([
      {
        cargo: "Dev",
        empresa: "TechCorp",
        periodo: "2024",
        conquistas: ["Atendi 1.000 usuários."],
        contexto: "ERP financeiro.",
        responsabilidades: ["Projetar telas", "Testar entregas", "Mentorar o time"],
        skills: ["Java", "Flyway"],
      },
    ]);
  });

  it("a avaliação recebe o texto composto dos quatro blocos", async () => {
    const usuario = userEvent.setup();
    let corpoRecebido: unknown;
    const dimensao = (score: number) => ({ score, nivel: "adequado", confianca: 0.9 });
    servidorApi.use(
      http.post(`${API_TESTE}/v1/experiencias-profissionais/avaliacoes`, async ({ request }) => {
        corpoRecebido = await request.json();
        return HttpResponse.json({
          score: 74,
          clareza_escrita: dimensao(80),
          qualidade_detalhe: dimensao(60),
          aderencia_vaga: dimensao(70),
          consistencia_textual: dimensao(86),
        });
      }),
    );
    renderizar({ rascunho: rascunhoComBlocos });

    await usuario.click(screen.getByRole("button", { name: "Avaliar experiência 1" }));
    const dialogo = screen.getByRole("dialog", { name: "Avaliar experiência" });
    await usuario.type(within(dialogo).getByLabelText("Descrição da vaga"), "Vaga Java");
    await usuario.click(within(dialogo).getByRole("button", { name: "Avaliar" }));
    await within(dialogo).findByText("74");

    expect(corpoRecebido).toMatchObject({
      experiencia: {
        descricao:
          "- Projetar telas\n- Testar entregas\n- Atendi 1.000 usuários.\nERP financeiro.\nJava, SQL",
      },
    });
  });

  it("a sugestão de IA envia e aplica os quatro blocos", async () => {
    const usuario = userEvent.setup();
    const pedidos: Record<string, unknown>[] = [];
    servidorApi.use(
      http.post(`${API_TESTE}/v1/experiencias-adaptadas/sugestoes`, async ({ request }) => {
        pedidos.push((await request.json()) as Record<string, unknown>);
        return HttpResponse.json({
          conquistas: ["Reduzi o fechamento em 30%."],
          contexto: "Plataforma financeira.",
          responsabilidades: ["Projetar o contas a receber"],
          skills: ["Java", "Flyway"],
          foco: "aderencia_vaga",
        });
      }),
    );
    renderizar({ rascunho: rascunhoComBlocos });

    await usuario.click(screen.getByRole("button", { name: "Sugestões de IA para experiência 1" }));
    const painel = await screen.findByRole("region", { name: "Sugestão da IA para experiência 1" });

    expect(pedidos[0]).toMatchObject({
      experiencia: {
        responsabilidades: ["Projetar telas", "Testar entregas"],
        skills: ["Java", "SQL"],
      },
    });
    expect(painel).toHaveTextContent("Responsabilidades: Projetar o contas a receber");
    expect(painel).toHaveTextContent("Skills: Java, Flyway");

    await usuario.click(screen.getByRole("button", { name: "Aplicar sugestão em experiência 1" }));

    expect(screen.getByLabelText("Principais realizações")).toHaveValue(
      "Reduzi o fechamento em 30%.",
    );
    expect(screen.getByLabelText("Contexto")).toHaveValue("Plataforma financeira.");
    expect(screen.getByLabelText("Principais responsabilidades")).toHaveValue(
      "Projetar o contas a receber",
    );
    expect(skills().getByText("Flyway")).toBeInTheDocument();
    expect(skills().queryByText("SQL")).not.toBeInTheDocument();
  });

  it("rascunho salvo antes dos novos blocos abre com responsabilidades e skills vazias", () => {
    renderizar();

    expect(screen.getByLabelText("Principais responsabilidades")).toHaveValue("");
    expect(skills().queryByRole("list")).not.toBeInTheDocument();
  });
});
