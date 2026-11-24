import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { delay, http, HttpResponse } from "msw";
import type { PerfilEstruturado } from "../../api/tipos";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

const PERFIL: PerfilEstruturado = {
  perfil_identificador: "adriano",
  nome_completo: "Adriano Teixeira",
  email: "adriano@email.com",
  linkedin: "",
  resumo_profissional: "Backend.",
  experiencias: [
    {
      empresa: "Neoway",
      cargo: "Dev Java",
      periodo: "2020-2024",
      descricao: "APIs em Java.",
      conquistas: [],
    },
  ],
  formacoes: [],
  certificacoes: [],
  idiomas: [],
  tecnologias: ["Java"],
};

const NAO_ENCONTRADO = HttpResponse.json(
  {
    type: "t",
    title: "Não encontrado",
    status: 404,
    detail: "Perfil estruturado nao encontrado",
    instance: "i",
  },
  { status: 404 },
);

function servirPerfil(perfil: PerfilEstruturado | null) {
  const envios: { metodo: string; corpo: unknown }[] = [];
  servidorApi.use(
    http.get(`${API_TESTE}/v1/perfil-estruturado/:perfil`, () =>
      perfil ? HttpResponse.json(perfil) : NAO_ENCONTRADO.clone(),
    ),
    http.post(`${API_TESTE}/v1/perfil-estruturado`, async ({ request }) => {
      const corpo = await request.json();
      envios.push({ metodo: "POST", corpo });
      return HttpResponse.json(corpo);
    }),
    http.put(`${API_TESTE}/v1/perfil-estruturado/:perfil`, async ({ request }) => {
      const corpo = await request.json();
      envios.push({ metodo: "PUT", corpo });
      return HttpResponse.json(corpo);
    }),
    http.get(`${API_TESTE}/v1/curriculos`, () =>
      HttpResponse.json({
        items: [
          {
            id: "c1",
            perfil_identificador: "adriano",
            nome_referencia: "LinkedIn",
            data_upload: "2026-11-01T10:00:00",
          },
        ],
        total: 1,
      }),
    ),
  );
  return { envios };
}

describe("PerfilPage", () => {
  it("sem perfil salvo, orienta o primeiro passo e mostra o formulário vazio", async () => {
    servirPerfil(null);

    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    expect(await screen.findByText(/Você ainda não tem um currículo mestre/)).toBeInTheDocument();
    expect(screen.getByLabelText("Nome completo")).toHaveValue("");
  });

  it("carrega o perfil salvo nos campos", async () => {
    servirPerfil(PERFIL);

    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    expect(await screen.findByLabelText("Nome completo")).toHaveValue("Adriano Teixeira");
    const experiencia = screen.getByRole("group", { name: "Experiência 1" });
    expect(within(experiencia).getByLabelText("Empresa")).toHaveValue("Neoway");
    expect(screen.getByLabelText("Tecnologias")).toHaveValue("Java");
  });

  it("adiciona e remove itens e salva um perfil novo com POST", async () => {
    const { envios } = servirPerfil(null);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await userEvent.type(await screen.findByLabelText("Nome completo"), "Ana Lima");
    await userEvent.type(screen.getByLabelText("E-mail"), "ana@email.com");
    await userEvent.click(screen.getByRole("button", { name: "Adicionar experiência" }));
    await userEvent.click(screen.getByRole("button", { name: "Adicionar experiência" }));
    const primeira = screen.getByRole("group", { name: "Experiência 1" });
    await userEvent.type(within(primeira).getByLabelText("Empresa"), "Olist");
    await userEvent.type(within(primeira).getByLabelText("Cargo"), "Backend");
    await userEvent.click(screen.getByRole("button", { name: "Remover experiência 2" }));
    await userEvent.click(screen.getByRole("button", { name: "Adicionar idioma" }));
    const idioma = screen.getByRole("group", { name: "Idioma 1" });
    await userEvent.type(within(idioma).getByLabelText("Idioma"), "Inglês");
    await userEvent.selectOptions(within(idioma).getByLabelText("Nível"), "FLUENTE");
    await userEvent.type(screen.getByLabelText("Tecnologias"), "Python, FastAPI");
    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));

    expect(await screen.findByRole("status")).toHaveTextContent("Perfil salvo.");
    expect(envios).toEqual([
      {
        metodo: "POST",
        corpo: {
          perfil_identificador: "adriano",
          nome_completo: "Ana Lima",
          email: "ana@email.com",
          linkedin: "",
          resumo_profissional: "",
          experiencias: [
            {
              empresa: "Olist",
              cargo: "Backend",
              periodo: "",
              descricao: "",
              contexto: "",
              responsabilidades: [],
              conquistas: [],
              skills: [],
            },
          ],
          formacoes: [],
          certificacoes: [],
          idiomas: [{ idioma: "Inglês", nivel: "FLUENTE" }],
          tecnologias: ["Python", "FastAPI"],
        },
      },
    ]);
  });

  it("atualiza um perfil existente com PUT", async () => {
    const { envios } = servirPerfil(PERFIL);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    const nome = await screen.findByLabelText("Nome completo");
    await userEvent.clear(nome);
    await userEvent.type(nome, "Adriano J. Teixeira");
    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));

    await waitFor(() => expect(envios).toHaveLength(1));
    expect(envios[0]).toMatchObject({
      metodo: "PUT",
      corpo: { nome_completo: "Adriano J. Teixeira" },
    });
  });

  it("bloqueia o envio com campos obrigatórios vazios", async () => {
    const { envios } = servirPerfil(null);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("button", { name: "Adicionar experiência" }));
    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));

    expect(await screen.findByText("Informe o nome completo.")).toBeInTheDocument();
    expect(screen.getByText("Informe o e-mail.")).toBeInTheDocument();
    const experiencia = screen.getByRole("group", { name: "Experiência 1" });
    expect(within(experiencia).getByLabelText("Empresa")).toHaveAccessibleDescription(
      "Informe a empresa.",
    );
    expect(envios).toHaveLength(0);
  });

  it("importa de um PDF novo e pré-preenche sem salvar", async () => {
    const { envios } = servirPerfil(null);
    let pdfRecebido = "";
    servidorApi.use(
      http.post(`${API_TESTE}/v1/perfil-estruturado/importacoes`, async ({ request }) => {
        pdfRecebido = ((await request.json()) as { pdf_base64: string }).pdf_base64;
        return HttpResponse.json({
          ...PERFIL,
          perfil_identificador: null,
          nome_completo: "Nome Importado",
        });
      }),
    );
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("button", { name: "Importar de PDF" }));
    const dialogo = screen.getByRole("dialog", { name: "Importar currículo de um PDF" });
    await userEvent.upload(
      within(dialogo).getByLabelText("Arquivo PDF"),
      new File(["%PDF-1.4"], "linkedin.pdf", { type: "application/pdf" }),
    );
    await userEvent.click(
      within(dialogo).getByRole("button", { name: "Importar e pré-preencher" }),
    );

    expect(await screen.findByLabelText("Nome completo")).toHaveValue("Nome Importado");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.getByText("Alterações não salvas")).toBeInTheDocument();
    expect(atob(pdfRecebido)).toBe("%PDF-1.4");
    expect(envios).toHaveLength(0);
  });

  it("importa a partir de um currículo da biblioteca", async () => {
    servirPerfil(null);
    servidorApi.use(
      http.get(`${API_TESTE}/v1/curriculos/:id/conteudo`, () =>
        HttpResponse.json({
          id: "c1",
          nome_referencia: "LinkedIn",
          pdf_base64: btoa("%PDF-biblioteca"),
        }),
      ),
      http.post(`${API_TESTE}/v1/perfil-estruturado/importacoes`, async ({ request }) => {
        const { pdf_base64 } = (await request.json()) as { pdf_base64: string };
        return HttpResponse.json({ ...PERFIL, nome_completo: atob(pdf_base64) });
      }),
    );
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("button", { name: "Importar de PDF" }));
    const dialogo = screen.getByRole("dialog", { name: "Importar currículo de um PDF" });
    await userEvent.click(within(dialogo).getByLabelText("Currículo da biblioteca"));
    await userEvent.selectOptions(await within(dialogo).findByLabelText("Currículo"), "c1");
    await userEvent.click(
      within(dialogo).getByRole("button", { name: "Importar e pré-preencher" }),
    );

    expect(await screen.findByLabelText("Nome completo")).toHaveValue("%PDF-biblioteca");
  });

  it("avalia uma experiência contra a descrição da vaga", async () => {
    servirPerfil(PERFIL);
    let corpoRecebido: unknown;
    const dimensao = (score: number) => ({ score, nivel: "adequado", confianca: 0.9 });
    servidorApi.use(
      http.post(`${API_TESTE}/v1/experiencias-profissionais/avaliacoes`, async ({ request }) => {
        corpoRecebido = await request.json();
        await delay(10);
        return HttpResponse.json({
          score: 74,
          clareza_escrita: dimensao(80),
          qualidade_detalhe: dimensao(60),
          aderencia_vaga: dimensao(70),
          consistencia_textual: dimensao(86),
        });
      }),
    );
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("button", { name: "Avaliar experiência 1" }));
    const dialogo = screen.getByRole("dialog", { name: "Avaliar experiência" });
    await userEvent.type(within(dialogo).getByLabelText("Descrição da vaga"), "Vaga Java sênior");
    await userEvent.click(within(dialogo).getByRole("button", { name: "Avaliar" }));

    expect(await within(dialogo).findByText("74")).toBeInTheDocument();
    expect(within(dialogo).getByRole("meter", { name: "Aderência à vaga" })).toHaveAttribute(
      "aria-valuenow",
      "70",
    );
    expect(within(dialogo).getAllByRole("meter")).toHaveLength(4);
    expect(corpoRecebido).toEqual({
      experiencia: {
        empresa: "Neoway",
        cargo: "Dev Java",
        periodo: "2020-2024",
        descricao: "APIs em Java.",
        contexto: "",
        responsabilidades: [],
        conquistas: [],
        skills: [],
      },
      descricao_vaga: "Vaga Java sênior",
    });
  });

  it("mostra a falha do avaliador sem fechar o diálogo", async () => {
    servirPerfil(PERFIL);
    servidorApi.use(
      http.post(`${API_TESTE}/v1/experiencias-profissionais/avaliacoes`, () =>
        HttpResponse.json(
          {
            type: "t",
            title: "Avaliação indisponível",
            status: 502,
            detail: "O avaliador está indisponível.",
            instance: "i",
          },
          { status: 502 },
        ),
      ),
    );
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("button", { name: "Avaliar experiência 1" }));
    const dialogo = screen.getByRole("dialog", { name: "Avaliar experiência" });
    await userEvent.type(within(dialogo).getByLabelText("Descrição da vaga"), "Vaga");
    await userEvent.click(within(dialogo).getByRole("button", { name: "Avaliar" }));

    expect(await within(dialogo).findByText("O avaliador está indisponível.")).toBeInTheDocument();
  });

  describe("sugestões de IA", () => {
    function servirSugestoes() {
      const pedidos: { rota: string; corpo: Record<string, unknown> }[] = [];
      servidorApi.use(
        http.post(`${API_TESTE}/v1/secoes-curriculo/sugestoes`, async ({ request }) => {
          pedidos.push({ rota: "secao", corpo: (await request.json()) as Record<string, unknown> });
          return HttpResponse.json({ conteudo_sugerido: "Resumo mais claro.", foco: "impacto" });
        }),
        http.post(`${API_TESTE}/v1/experiencias-profissionais/sugestoes`, async ({ request }) => {
          pedidos.push({
            rota: "experiencia",
            corpo: (await request.json()) as Record<string, unknown>,
          });
          return HttpResponse.json({
            descricao_sugerida: "Desenvolvi APIs REST em Java.",
            foco: "impacto",
          });
        }),
      );
      return pedidos;
    }

    it("oferece sugestão no resumo e em cada experiência, mas não em formação ou tecnologias", async () => {
      servirPerfil(PERFIL);
      renderizarApp({ caminho: "/perfil", perfil: "adriano" });

      await screen.findByRole("button", { name: "Sugestões de IA para resumo" });

      expect(
        screen.getByRole("button", { name: "Sugestões de IA para experiência 1" }),
      ).toBeVisible();
      expect(screen.getAllByRole("button", { name: /^Sugestões de IA/ })).toHaveLength(2);
    });

    it("pede a melhoria do resumo sem contexto de vaga e só o altera ao aplicar, sem salvar", async () => {
      const { envios } = servirPerfil(PERFIL);
      const pedidos = servirSugestoes();
      renderizarApp({ caminho: "/perfil", perfil: "adriano" });
      await userEvent.type(await screen.findByLabelText("Resumo profissional"), " Com APIs.");

      await userEvent.click(screen.getByRole("button", { name: "Sugestões de IA para resumo" }));
      await userEvent.click(
        await screen.findByRole("button", { name: "Aplicar sugestão em resumo" }),
      );

      expect(pedidos[0]).toEqual({
        rota: "secao",
        corpo: {
          secao: { tipo: "PERFIL", titulo: "Perfil", conteudo: "Backend. Com APIs." },
          refino: { tentativa: 1, sugestoes_anteriores: [] },
        },
      });
      expect(screen.getByLabelText("Resumo profissional")).toHaveValue("Resumo mais claro.");
      expect(screen.getByText("Alterações não salvas")).toBeInTheDocument();
      expect(envios).toHaveLength(0);
    });

    it("pede a melhoria de uma experiência preservando seus dados e aplica só a descrição", async () => {
      const { envios } = servirPerfil(PERFIL);
      const pedidos = servirSugestoes();
      renderizarApp({ caminho: "/perfil", perfil: "adriano" });

      await userEvent.click(
        await screen.findByRole("button", { name: "Sugestões de IA para experiência 1" }),
      );
      await userEvent.click(
        await screen.findByRole("button", { name: "Aplicar sugestão em experiência 1" }),
      );

      expect(pedidos[0]).toEqual({
        rota: "experiencia",
        corpo: {
          experiencia: {
            empresa: "Neoway",
            cargo: "Dev Java",
            periodo: "2020-2024",
            descricao: "APIs em Java.",
          },
          refino: { tentativa: 1, sugestoes_anteriores: [] },
        },
      });
      expect(screen.getByLabelText("Descrição")).toHaveValue("Desenvolvi APIs REST em Java.");
      expect(screen.getByLabelText("Cargo")).toHaveValue("Dev Java");
      expect(envios).toHaveLength(0);
    });

    it("descartar a sugestão não altera o campo", async () => {
      servirPerfil(PERFIL);
      servirSugestoes();
      renderizarApp({ caminho: "/perfil", perfil: "adriano" });

      await userEvent.click(
        await screen.findByRole("button", { name: "Sugestões de IA para resumo" }),
      );
      await userEvent.click(
        await screen.findByRole("button", { name: "Descartar sugestão de resumo" }),
      );

      expect(screen.getByLabelText("Resumo profissional")).toHaveValue("Backend.");
      expect(screen.queryByText("Alterações não salvas")).not.toBeInTheDocument();
    });
  });
});

const CONQUISTA_DEPLOY = { texto: "Reduzi o tempo de deploy.", origem: "MANUAL" } as const;

const PERFIL_COM_CONQUISTAS: PerfilEstruturado = {
  ...PERFIL,
  experiencias: [{ ...PERFIL.experiencias![0]!, conquistas: [CONQUISTA_DEPLOY] }],
};

function servirParecidas(parecidas: string[]) {
  const consultas: unknown[] = [];
  servidorApi.use(
    http.post(`${API_TESTE}/v1/perfil-estruturado/conquistas/parecidas`, async ({ request }) => {
      consultas.push(await request.json());
      return HttpResponse.json({ parecidas });
    }),
  );
  return { consultas };
}

function conquistasDaExperiencia(indice = 1) {
  return screen.getByRole("group", { name: `Conquistas da experiência ${indice}` });
}

describe("PerfilPage — banco de conquistas", () => {
  it("mostra as conquistas salvas na experiência", async () => {
    servirPerfil(PERFIL_COM_CONQUISTAS);

    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await screen.findByLabelText("Nome completo");
    expect(within(conquistasDaExperiencia()).getByLabelText("Conquista 1")).toHaveValue(
      "Reduzi o tempo de deploy.",
    );
  });

  it("sem conquistas, indica que o banco está vazio", async () => {
    servirPerfil(PERFIL);

    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await screen.findByLabelText("Nome completo");
    expect(
      within(conquistasDaExperiencia()).getByText("Nenhuma conquista cadastrada."),
    ).toBeInTheDocument();
  });

  it("cadastra uma conquista nova, consulta as parecidas e salva com origem manual", async () => {
    const { envios } = servirPerfil(PERFIL_COM_CONQUISTAS);
    const { consultas } = servirParecidas([]);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await screen.findByLabelText("Nome completo");
    const grupo = conquistasDaExperiencia();
    await userEvent.type(
      within(grupo).getByLabelText("Nova conquista"),
      "Liderei a migração do banco.",
    );
    await userEvent.click(within(grupo).getByRole("button", { name: "Adicionar conquista" }));
    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));

    await waitFor(() => expect(envios).toHaveLength(1));
    expect(consultas).toEqual([
      { texto: "Liderei a migração do banco.", conquistas: ["Reduzi o tempo de deploy."] },
    ]);
    expect(envios[0]?.corpo).toMatchObject({
      experiencias: [
        {
          conquistas: [
            { texto: "Reduzi o tempo de deploy.", origem: "MANUAL" },
            { texto: "Liderei a migração do banco.", origem: "MANUAL" },
          ],
        },
      ],
    });
  });

  it("avisa quando a conquista nova se parece com outra e não a adiciona até o usuário decidir", async () => {
    servirPerfil(PERFIL_COM_CONQUISTAS);
    servirParecidas(["Reduzi o tempo de deploy."]);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await screen.findByLabelText("Nome completo");
    const grupo = conquistasDaExperiencia();
    await userEvent.type(
      within(grupo).getByLabelText("Nova conquista"),
      "Reduzi o deploy com pipeline.",
    );
    await userEvent.click(within(grupo).getByRole("button", { name: "Adicionar conquista" }));

    expect(await within(grupo).findByText(/se parece com outra já cadastrada/)).toBeInTheDocument();
    expect(
      within(grupo).getByText("Reduzi o tempo de deploy.", { selector: "li" }),
    ).toBeInTheDocument();
    expect(within(grupo).queryByLabelText("Conquista 2")).not.toBeInTheDocument();
  });

  it("'Salvar mesmo assim' adiciona a conquista parecida", async () => {
    servirPerfil(PERFIL_COM_CONQUISTAS);
    servirParecidas(["Reduzi o tempo de deploy."]);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await screen.findByLabelText("Nome completo");
    const grupo = conquistasDaExperiencia();
    await userEvent.type(
      within(grupo).getByLabelText("Nova conquista"),
      "Reduzi o deploy com pipeline.",
    );
    await userEvent.click(within(grupo).getByRole("button", { name: "Adicionar conquista" }));
    await userEvent.click(await within(grupo).findByRole("button", { name: "Salvar mesmo assim" }));

    expect(within(grupo).getByLabelText("Conquista 2")).toHaveValue(
      "Reduzi o deploy com pipeline.",
    );
    expect(within(grupo).queryByText(/se parece com outra já cadastrada/)).not.toBeInTheDocument();
  });

  it("'Cancelar' descarta o aviso sem adicionar a conquista", async () => {
    servirPerfil(PERFIL_COM_CONQUISTAS);
    servirParecidas(["Reduzi o tempo de deploy."]);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await screen.findByLabelText("Nome completo");
    const grupo = conquistasDaExperiencia();
    await userEvent.type(
      within(grupo).getByLabelText("Nova conquista"),
      "Reduzi o deploy com pipeline.",
    );
    await userEvent.click(within(grupo).getByRole("button", { name: "Adicionar conquista" }));
    await userEvent.click(await within(grupo).findByRole("button", { name: "Cancelar" }));

    expect(within(grupo).queryByText(/se parece com outra já cadastrada/)).not.toBeInTheDocument();
    expect(within(grupo).queryByLabelText("Conquista 2")).not.toBeInTheDocument();
  });

  it("edita e exclui conquistas e salva o resultado", async () => {
    const { envios } = servirPerfil({
      ...PERFIL_COM_CONQUISTAS,
      experiencias: [
        {
          ...PERFIL.experiencias![0]!,
          conquistas: [CONQUISTA_DEPLOY, { texto: "Entreguei um MVP.", origem: "MANUAL" }],
        },
      ],
    });
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await screen.findByLabelText("Nome completo");
    const grupo = conquistasDaExperiencia();
    const primeira = within(grupo).getByLabelText("Conquista 1");
    await userEvent.clear(primeira);
    await userEvent.type(primeira, "Cortei o deploy de 40 para 10 minutos.");
    await userEvent.click(
      within(grupo).getByRole("button", { name: "Remover conquista 2 da experiência 1" }),
    );
    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));

    await waitFor(() => expect(envios).toHaveLength(1));
    expect(envios[0]?.corpo).toMatchObject({
      experiencias: [
        { conquistas: [{ texto: "Cortei o deploy de 40 para 10 minutos.", origem: "MANUAL" }] },
      ],
    });
  });

  it("não adiciona conquista em branco", async () => {
    servirPerfil(PERFIL);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await screen.findByLabelText("Nome completo");

    expect(
      within(conquistasDaExperiencia()).getByRole("button", { name: "Adicionar conquista" }),
    ).toBeDisabled();
  });

  it("se a verificação de parecidas falhar, mostra o erro e não adiciona a conquista", async () => {
    servirPerfil(PERFIL);
    servidorApi.use(
      http.post(`${API_TESTE}/v1/perfil-estruturado/conquistas/parecidas`, () =>
        HttpResponse.json(
          { type: "t", title: "Erro", status: 500, detail: "Falha interna", instance: "i" },
          { status: 500 },
        ),
      ),
    );
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await screen.findByLabelText("Nome completo");
    const grupo = conquistasDaExperiencia();
    await userEvent.type(within(grupo).getByLabelText("Nova conquista"), "Entreguei um MVP.");
    await userEvent.click(within(grupo).getByRole("button", { name: "Adicionar conquista" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Falha interna");
    expect(within(grupo).queryByLabelText("Conquista 1")).not.toBeInTheDocument();
  });
});

const PERFIL_COM_BLOCOS: PerfilEstruturado = {
  ...PERFIL,
  experiencias: [
    {
      empresa: "Starian",
      cargo: "Dev",
      periodo: "2024 - Atual",
      descricao: "",
      contexto: "ERP financeiro.",
      responsabilidades: ["Projetar telas", "Testar entregas"],
      conquistas: [{ texto: "Atendi 1.000 usuários.", origem: "MANUAL" }],
      skills: ["Java", "SQL"],
    },
  ],
};

function experiencia1() {
  return screen.getByRole("group", { name: "Experiência 1" });
}

describe("PerfilPage — quatro blocos por experiência", () => {
  it("mostra contexto, responsabilidades, realizações e skills da experiência", async () => {
    servirPerfil(PERFIL_COM_BLOCOS);

    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await screen.findByLabelText("Nome completo");
    const grupo = within(experiencia1());
    expect(grupo.getByLabelText("Contexto")).toHaveValue("ERP financeiro.");
    expect(grupo.getByLabelText("Principais responsabilidades")).toHaveValue(
      "Projetar telas\nTestar entregas",
    );
    expect(grupo.getByRole("heading", { name: "Principais realizações" })).toBeInTheDocument();
    expect(grupo.getByLabelText("Conquista 1")).toHaveValue("Atendi 1.000 usuários.");
    expect(
      within(screen.getByRole("group", { name: "Skills da experiência 1" })).getByText("Java"),
    ).toBeInTheDocument();
    expect(grupo.queryByLabelText("Descrição")).not.toBeInTheDocument();
  });

  it("cria e remove skills como tags e envia as skills no salvamento", async () => {
    const { envios } = servirPerfil(PERFIL_COM_BLOCOS);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    await screen.findByLabelText("Nome completo");
    const skills = within(screen.getByRole("group", { name: "Skills da experiência 1" }));

    await userEvent.type(skills.getByLabelText("Nova skill"), "Flyway{Enter}");
    await userEvent.click(skills.getByRole("button", { name: "Remover SQL" }));
    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));

    await waitFor(() => expect(envios).toHaveLength(1));
    expect(envios[0]).toMatchObject({
      metodo: "PUT",
      corpo: {
        experiencias: [
          {
            contexto: "ERP financeiro.",
            responsabilidades: ["Projetar telas", "Testar entregas"],
            skills: ["Java", "Flyway"],
          },
        ],
      },
    });
  });

  it("edita as responsabilidades uma por linha e envia como lista", async () => {
    const { envios } = servirPerfil(PERFIL_COM_BLOCOS);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    const campo = await screen.findByLabelText("Principais responsabilidades");

    await userEvent.clear(campo);
    await userEvent.type(campo, "Revisar código{Enter}{Enter}Mentorar o time");
    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));

    await waitFor(() => expect(envios).toHaveLength(1));
    expect(envios[0]).toMatchObject({
      corpo: { experiencias: [{ responsabilidades: ["Revisar código", "Mentorar o time"] }] },
    });
  });

  it("informa as tecnologias que as skills acrescentaram ao salvar", async () => {
    servirPerfil(PERFIL_COM_BLOCOS);
    servidorApi.use(
      http.put(`${API_TESTE}/v1/perfil-estruturado/:perfil`, async ({ request }) => {
        const corpo = (await request.json()) as PerfilEstruturado;
        return HttpResponse.json({
          ...corpo,
          tecnologias: ["Java", "SQL"],
          tecnologias_incluidas: ["SQL"],
        });
      }),
    );
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    const nome = await screen.findByLabelText("Nome completo");
    await userEvent.type(nome, " Jr");

    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));

    expect(await screen.findByRole("status")).toHaveTextContent(
      "Perfil salvo. Tecnologias incluídas pelas skills: SQL.",
    );
    expect(screen.getByLabelText("Tecnologias")).toHaveValue("Java, SQL");
  });

  it("aplica a sugestão de IA nos quatro blocos de uma vez", async () => {
    servirPerfil(PERFIL_COM_BLOCOS);
    const pedidos: unknown[] = [];
    servidorApi.use(
      http.post(`${API_TESTE}/v1/experiencias-profissionais/sugestoes`, async ({ request }) => {
        pedidos.push(await request.json());
        return HttpResponse.json({
          descricao_sugerida: "",
          contexto: "Plataforma financeira.",
          responsabilidades: ["Projetar telas do contas a receber"],
          conquistas: ["Atendi 1.000 usuários.", "Reduzi o fechamento em 30%."],
          skills: ["Java", "Flyway"],
          foco: "impacto",
        });
      }),
    );
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await userEvent.click(
      await screen.findByRole("button", { name: "Sugestões de IA para experiência 1" }),
    );
    await userEvent.click(
      await screen.findByRole("button", { name: "Aplicar sugestão em experiência 1" }),
    );

    expect(pedidos[0]).toMatchObject({
      experiencia: {
        contexto: "ERP financeiro.",
        responsabilidades: ["Projetar telas", "Testar entregas"],
        conquistas: ["Atendi 1.000 usuários."],
        skills: ["Java", "SQL"],
      },
    });
    const grupo = within(experiencia1());
    expect(grupo.getByLabelText("Contexto")).toHaveValue("Plataforma financeira.");
    expect(grupo.getByLabelText("Principais responsabilidades")).toHaveValue(
      "Projetar telas do contas a receber",
    );
    expect(grupo.getByLabelText("Conquista 2")).toHaveValue("Reduzi o fechamento em 30%.");
    expect(
      within(screen.getByRole("group", { name: "Skills da experiência 1" })).getByText("Flyway"),
    ).toBeInTheDocument();
  });
});

describe("PerfilPage — migração de perfil antigo", () => {
  const RASCUNHO: PerfilEstruturado = {
    ...PERFIL,
    experiencias: [
      {
        empresa: "Neoway",
        cargo: "Dev Java",
        periodo: "2020-2024",
        descricao: "",
        contexto: "Empresa de dados.",
        responsabilidades: ["Desenvolver APIs"],
        conquistas: [{ texto: "Reduzi o tempo de resposta.", origem: "MANUAL" }],
        skills: ["Java"],
      },
    ],
  };

  it("oferece estruturar as experiências antigas e mostra o rascunho sem salvar", async () => {
    const { envios } = servirPerfil(PERFIL);
    servidorApi.use(
      http.post(`${API_TESTE}/v1/perfil-estruturado/adriano/migracoes-de-experiencias`, () =>
        HttpResponse.json(RASCUNHO),
      ),
    );
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    expect(await screen.findByLabelText("Descrição")).toHaveValue("APIs em Java.");

    await userEvent.click(screen.getByRole("button", { name: "Estruturar experiências" }));

    expect(await screen.findByLabelText("Contexto")).toHaveValue("Empresa de dados.");
    expect(screen.getByLabelText("Principais responsabilidades")).toHaveValue("Desenvolver APIs");
    expect(screen.queryByLabelText("Descrição")).not.toBeInTheDocument();
    expect(screen.getByText(/A IA pode ter estimado métricas e contextos/)).toBeInTheDocument();
    expect(screen.getByText("Alterações não salvas")).toBeInTheDocument();
    expect(envios).toHaveLength(0);
  });

  it("não oferece estruturar quando nenhuma experiência é antiga", async () => {
    servirPerfil(PERFIL_COM_BLOCOS);

    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    await screen.findByLabelText("Nome completo");
    expect(
      screen.queryByRole("button", { name: "Estruturar experiências" }),
    ).not.toBeInTheDocument();
  });

  it("com alterações não salvas, o botão de estruturar fica desabilitado", async () => {
    servirPerfil(PERFIL);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    const resumo = await screen.findByLabelText("Resumo profissional");

    await userEvent.type(resumo, " Mais.");

    expect(screen.getByRole("button", { name: "Estruturar experiências" })).toBeDisabled();
  });

  it("mostra o erro da migração e mantém o formulário", async () => {
    servirPerfil(PERFIL);
    servidorApi.use(
      http.post(`${API_TESTE}/v1/perfil-estruturado/adriano/migracoes-de-experiencias`, () =>
        HttpResponse.json(
          { type: "t", title: "IA", status: 502, detail: "A IA está indisponível.", instance: "i" },
          { status: 502 },
        ),
      ),
    );
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    await screen.findByLabelText("Descrição");

    await userEvent.click(screen.getByRole("button", { name: "Estruturar experiências" }));

    expect(await screen.findByText("A IA está indisponível.")).toBeInTheDocument();
    expect(screen.getByLabelText("Descrição")).toHaveValue("APIs em Java.");
  });

  it("o perfil importado de PDF também pede para conferir as estimativas da IA", async () => {
    servirPerfil(null);
    servidorApi.use(
      http.post(`${API_TESTE}/v1/perfil-estruturado/importacoes`, () =>
        HttpResponse.json(RASCUNHO),
      ),
    );
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    await userEvent.click(await screen.findByRole("button", { name: "Importar de PDF" }));
    const dialogo = screen.getByRole("dialog");
    await userEvent.upload(
      within(dialogo).getByLabelText("Arquivo PDF"),
      new File(["%PDF-1.4"], "curriculo.pdf", { type: "application/pdf" }),
    );
    await userEvent.click(
      within(dialogo).getByRole("button", { name: "Importar e pré-preencher" }),
    );

    expect(
      await screen.findByText(/A IA pode ter estimado métricas e contextos/),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Contexto")).toHaveValue("Empresa de dados.");
  });
});
