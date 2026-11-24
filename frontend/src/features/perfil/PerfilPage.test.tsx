import { act, cleanup, screen, waitFor, within } from "@testing-library/react";
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

const CARTOES_ABERTOS = [
  ["experiencias", ["Neoway|Dev Java|2020-2024", "Starian|Dev|2024 - Atual"]],
  ["dados", ["dados"]],
] as const;

beforeEach(() => {
  CARTOES_ABERTOS.forEach(([lista, chaves]) =>
    window.localStorage.setItem(`jobsync:perfil:cartoes:adriano:${lista}`, JSON.stringify(chaves)),
  );
});
afterEach(() => window.localStorage.clear());

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
    expect(screen.getByRole("list", { name: "Tags de tecnologias" })).toHaveTextContent("Java");
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
    await userEvent.type(screen.getByLabelText("Nova tecnologia"), "Python, FastAPI{Enter}");
    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));

    expect(await screen.findByText("Perfil salvo.")).toBeInTheDocument();
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

    expect(
      await screen.findByText("Perfil salvo. Tecnologias incluídas pelas skills: SQL."),
    ).toBeInTheDocument();
    const tecnologias = screen.getByRole("list", { name: "Tags de tecnologias" });
    expect(tecnologias).toHaveTextContent("Java");
    expect(tecnologias).toHaveTextContent("SQL");
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

const PERFIL_VARIOS: PerfilEstruturado = {
  ...PERFIL,
  experiencias: [
    {
      empresa: "Alfa",
      cargo: "Dev",
      periodo: "2018 - 2020",
      descricao: "",
      contexto: "Primeira linha.\nSegunda.",
      responsabilidades: ["Projetar"],
      conquistas: [],
      skills: ["Java", "SQL"],
    },
    {
      empresa: "Beta",
      cargo: "Líder",
      periodo: "2020 - 2022",
      descricao: "",
      contexto: "",
      responsabilidades: [],
      conquistas: [],
      skills: [],
    },
    {
      empresa: "Gama",
      cargo: "Arquiteta",
      periodo: "Mar 2022 - Atual",
      descricao: "Texto antigo da Gama.",
      contexto: "",
      responsabilidades: [],
      conquistas: [],
      skills: [],
    },
  ],
  formacoes: [
    { instituicao: "USP", curso: "Computação", periodo: "2012 - 2016" },
    { instituicao: "FIAP", curso: "MBA em Arquitetura", periodo: "2019 - 2020" },
  ],
  certificacoes: [
    { nome: "AWS SAA", instituicao: "AWS", ano: "2021" },
    { nome: "Scrum PSM I", instituicao: "Scrum.org", ano: "2023" },
  ],
  idiomas: [
    { idioma: "Português", nivel: "NATIVO" },
    { idioma: "Inglês", nivel: "AVANCADO" },
  ],
};

const cartoesDa = (lista: string) =>
  within(screen.getByRole("region", { name: lista }))
    .getAllByRole("group")
    .filter((g) => g.hasAttribute("data-item-id"));
const titulosDa = (lista: string) =>
  cartoesDa(lista).map(
    (cartao) =>
      within(cartao)
        .getByRole("button", { name: /^Editar / })
        .getAttribute("aria-label")
        ?.replace(/^Editar /, "") ?? "",
  );
const navegar = (router: ReturnType<typeof renderizarApp>["router"], para: string) =>
  act(async () => {
    void router.navigate(para);
  });

describe("PerfilPage — listas compactas e reordenáveis", () => {
  beforeEach(() => window.localStorage.clear());

  it("abre com os cartões recolhidos, com resumo e chips dos quatro blocos", async () => {
    servirPerfil(PERFIL_VARIOS);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    const experiencias = await screen.findByRole("region", { name: "Experiências profissionais" });
    const [alfa, beta, gama] = cartoesDa("Experiências profissionais");

    expect(within(alfa!).getByText("Dev · Alfa")).toBeInTheDocument();
    expect(within(alfa!).getByText("Primeira linha.")).toBeInTheDocument();
    expect(within(alfa!).getByText("2018 - 2020")).toBeInTheDocument();
    expect(within(alfa!).getByText("contexto")).toBeInTheDocument();
    expect(within(alfa!).getByText("1 responsabilidade")).toBeInTheDocument();
    expect(within(alfa!).getByText("sem realizações")).toBeInTheDocument();
    expect(within(alfa!).getByText("2 skills")).toBeInTheDocument();
    expect(within(beta!).getByText("sem contexto")).toBeInTheDocument();
    expect(within(gama!).getByText("Formato antigo")).toBeInTheDocument();
    expect(within(gama!).getByText("Texto antigo da Gama.")).toBeInTheDocument();
    expect(within(alfa!).getByLabelText("Empresa")).not.toBeVisible();
    expect(experiencias).toBeInTheDocument();
  });

  it("os dados pessoais ficam num cartão recolhido com nome e e-mail", async () => {
    servirPerfil(PERFIL_VARIOS);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    const dados = await screen.findByRole("region", { name: "Dados pessoais e resumo" });

    expect(within(dados).getByText("Adriano Teixeira · adriano@email.com")).toBeInTheDocument();
    expect(within(dados).getByLabelText("Nome completo")).not.toBeVisible();
    await userEvent.click(within(dados).getByRole("button", { name: "Editar" }));
    expect(within(dados).getByLabelText("Nome completo")).toBeVisible();
  });

  it("um perfil novo abre os dados pessoais, para o primeiro preenchimento", async () => {
    servirPerfil(null);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });

    expect(await screen.findByLabelText("Nome completo")).toBeVisible();
  });

  it("reordena uma experiência pelo botão e envia a nova ordem ao salvar", async () => {
    const { envios } = servirPerfil(PERFIL_VARIOS);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    await screen.findByRole("region", { name: "Experiências profissionais" });

    await userEvent.click(screen.getByRole("button", { name: "Mover Dev · Alfa para baixo" }));
    expect(screen.getByText("Alterações não salvas")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));

    await waitFor(() => expect(envios).toHaveLength(1));
    const empresas = (envios[0]!.corpo as { experiencias: { empresa: string }[] }).experiencias.map(
      (e) => e.empresa,
    );
    expect(empresas).toEqual(["Beta", "Alfa", "Gama"]);
  });

  it("ordena as experiências por período, com o período em andamento primeiro", async () => {
    servirPerfil(PERFIL_VARIOS);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    const painel = within(
      await screen.findByRole("region", { name: "Experiências profissionais" }),
    );

    await userEvent.click(painel.getByRole("button", { name: "Ordenar por período" }));

    expect(titulosDa("Experiências profissionais")).toEqual([
      "Arquiteta · Gama",
      "Líder · Beta",
      "Dev · Alfa",
    ]);
    await userEvent.click(screen.getByRole("button", { name: "Desfazer" }));
    expect(titulosDa("Experiências profissionais")).toEqual([
      "Dev · Alfa",
      "Líder · Beta",
      "Arquiteta · Gama",
    ]);
  });

  it("ordena as certificações por ano e as formações por período", async () => {
    servirPerfil(PERFIL_VARIOS);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    await screen.findByRole("region", { name: "Certificações" });

    await userEvent.click(
      within(screen.getByRole("region", { name: "Certificações" })).getByRole("button", {
        name: "Ordenar por ano",
      }),
    );
    await userEvent.click(
      within(screen.getByRole("region", { name: "Formação acadêmica" })).getByRole("button", {
        name: "Ordenar por período",
      }),
    );

    expect(titulosDa("Certificações")).toEqual(["Scrum PSM I", "AWS SAA"]);
    expect(titulosDa("Formação acadêmica")).toEqual(["MBA em Arquitetura", "Computação"]);
  });

  it("reordena os idiomas pela linha e envia a nova ordem", async () => {
    const { envios } = servirPerfil(PERFIL_VARIOS);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    await screen.findByRole("region", { name: "Idiomas" });

    await userEvent.click(screen.getByRole("button", { name: "Mover Português para baixo" }));
    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));

    await waitFor(() => expect(envios).toHaveLength(1));
    const idiomas = (envios[0]!.corpo as { idiomas: { idioma: string }[] }).idiomas.map(
      (i) => i.idioma,
    );
    expect(idiomas).toEqual(["Inglês", "Português"]);
  });

  it("período fora do formato bloqueia o salvar, mostra o erro e abre o cartão", async () => {
    const { envios } = servirPerfil(PERFIL_VARIOS);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    await screen.findByRole("region", { name: "Experiências profissionais" });
    const [alfa] = cartoesDa("Experiências profissionais");
    await userEvent.click(within(alfa!).getByRole("button", { name: "Editar Dev · Alfa" }));
    const periodo = within(alfa!).getByLabelText("Período");
    await userEvent.clear(periodo);
    await userEvent.type(periodo, "ontem");
    await userEvent.click(within(alfa!).getByRole("button", { name: "Concluir" }));

    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));

    expect(
      await within(alfa!).findByText("Use o formato Mar 2024 - Atual ou 2020 - 2022."),
    ).toBeInTheDocument();
    expect(within(alfa!).getByLabelText("Período")).toBeVisible();
    expect(envios).toHaveLength(0);
  });

  it("ano de certificação inválido bloqueia o salvar", async () => {
    const { envios } = servirPerfil(PERFIL_VARIOS);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    await screen.findByRole("region", { name: "Certificações" });
    const [aws] = cartoesDa("Certificações");
    await userEvent.click(within(aws!).getByRole("button", { name: "Editar AWS SAA" }));
    const ano = within(aws!).getByLabelText("Ano");
    await userEvent.clear(ano);
    await userEvent.type(ano, "23");

    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));

    expect(
      await within(aws!).findByText("Use um ano com quatro dígitos, como 2023."),
    ).toBeInTheDocument();
    expect(envios).toHaveLength(0);
  });

  it("período vazio é aceito", async () => {
    const { envios } = servirPerfil({
      ...PERFIL_VARIOS,
      formacoes: [{ instituicao: "USP", curso: "Computação", periodo: "" }],
    });
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    await screen.findByRole("region", { name: "Formação acadêmica" });
    await userEvent.type(screen.getByLabelText("Resumo profissional"), " Mais.");

    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));

    await waitFor(() => expect(envios).toHaveLength(1));
  });

  it("no limite de 15 itens o botão de adicionar fica desabilitado", async () => {
    servirPerfil({
      ...PERFIL_VARIOS,
      formacoes: Array.from({ length: 15 }, (_, n) => ({
        instituicao: `Inst ${n}`,
        curso: `Curso ${n}`,
        periodo: "",
      })),
    });
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    const painel = within(await screen.findByRole("region", { name: "Formação acadêmica" }));

    expect(painel.getByRole("button", { name: "Adicionar formação" })).toBeDisabled();
    expect(painel.getByRole("note")).toHaveTextContent("limite de 15 itens");
    expect(
      within(screen.getByRole("region", { name: "Certificações" })).getByRole("button", {
        name: "Adicionar certificação",
      }),
    ).toBeEnabled();
  });

  it("mostra a mensagem de validação que a API devolver (422)", async () => {
    servirPerfil(PERFIL_VARIOS);
    servidorApi.use(
      http.put(`${API_TESTE}/v1/perfil-estruturado/:perfil`, () =>
        HttpResponse.json(
          {
            type: "t",
            title: "Inválido",
            status: 422,
            detail:
              "Experiência 1: período inválido. Use o formato Mar 2024 - Atual ou 2020 - 2022.",
            instance: "i",
          },
          { status: 422 },
        ),
      ),
    );
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    await userEvent.type(await screen.findByLabelText("Resumo profissional"), " Mais.");

    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));

    expect(await screen.findByText(/Experiência 1: período inválido/)).toBeInTheDocument();
  });

  it("pergunta antes de sair com alterações não salvas e não pergunta depois de salvar", async () => {
    servirPerfil(PERFIL_VARIOS);
    const { router } = renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    await userEvent.click(
      await screen.findByRole("button", { name: "Mover Dev · Alfa para baixo" }),
    );

    await navegar(router, "/curriculos");
    expect(await screen.findByRole("dialog", { name: "Sair sem salvar?" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(router.state.location.pathname).toBe("/perfil");

    await userEvent.click(screen.getByRole("button", { name: "Salvar perfil" }));
    await screen.findByText("Perfil salvo.");
    await navegar(router, "/curriculos");

    await waitFor(() => expect(router.state.location.pathname).toBe("/curriculos"));
  });

  it("Descartar restaura a ordem salva e oferece desfazer", async () => {
    servirPerfil(PERFIL_VARIOS);
    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    await userEvent.click(
      await screen.findByRole("button", { name: "Mover Dev · Alfa para baixo" }),
    );
    expect(titulosDa("Experiências profissionais")[0]).toBe("Líder · Beta");

    await userEvent.click(screen.getByRole("button", { name: "Descartar" }));

    expect(titulosDa("Experiências profissionais")).toEqual([
      "Dev · Alfa",
      "Líder · Beta",
      "Arquiteta · Gama",
    ]);
    expect(screen.queryByText("Alterações não salvas")).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Desfazer" }));
    expect(titulosDa("Experiências profissionais")[0]).toBe("Líder · Beta");
  });

  it("lembra os cartões abertos ao voltar para o perfil", async () => {
    servirPerfil(PERFIL_VARIOS);
    const primeira = renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    await screen.findByRole("region", { name: "Experiências profissionais" });
    const [alfa] = cartoesDa("Experiências profissionais");
    await userEvent.click(within(alfa!).getByRole("button", { name: "Editar Dev · Alfa" }));
    primeira.router.dispose();
    cleanup();

    renderizarApp({ caminho: "/perfil", perfil: "adriano" });
    await screen.findByRole("region", { name: "Experiências profissionais" });

    const [alfaDeNovo, betaDeNovo] = cartoesDa("Experiências profissionais");
    await waitFor(() => expect(within(alfaDeNovo!).getByLabelText("Empresa")).toBeVisible());
    expect(within(betaDeNovo!).getByLabelText("Empresa")).not.toBeVisible();
  });
});
