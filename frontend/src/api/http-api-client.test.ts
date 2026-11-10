import { delay, http, HttpResponse } from "msw";
import { servidorApi } from "../test/servidor-api";
import { ApiError } from "./api-error";
import { HttpApiClient } from "./http-api-client";

const BASE = "http://api.test";

function criarCliente(opcoes: { timeoutPadraoMs?: number; timeoutIaMs?: number } = {}) {
  return new HttpApiClient({ baseUrl: BASE, ...opcoes });
}

async function capturarErro(promessa: Promise<unknown>): Promise<ApiError> {
  try {
    await promessa;
  } catch (erro) {
    return erro as ApiError;
  }
  throw new Error("A promessa deveria ter falhado.");
}

describe("HttpApiClient", () => {
  it("usa a URL base, envia a query e devolve os itens da listagem", async () => {
    servidorApi.use(
      http.get(`${BASE}/v1/vagas`, ({ request }) => {
        const perfil = new URL(request.url).searchParams.get("perfil_identificador");
        return HttpResponse.json({
          items: [
            {
              id: "v1",
              perfil_identificador: perfil,
              texto_descricao: "Vaga",
              data_captura: "2026-11-06T10:00:00",
            },
          ],
          total: 1,
          limite: 100,
          offset: 0,
        });
      }),
    );

    const vagas = await criarCliente().listarVagas("adriano");

    expect(vagas).toHaveLength(1);
    expect(vagas[0]?.perfil_identificador).toBe("adriano");
  });

  it("envia o corpo em JSON nas operações de escrita", async () => {
    let corpoRecebido: unknown;
    servidorApi.use(
      http.post(`${BASE}/v1/tokens-captura`, async ({ request }) => {
        corpoRecebido = await request.json();
        return HttpResponse.json(
          { token: "abc", perfil_identificador: "adriano" },
          { status: 201 },
        );
      }),
    );

    const token = await criarCliente().criarTokenCaptura("adriano");

    expect(corpoRecebido).toEqual({ perfil_identificador: "adriano" });
    expect(token.token).toBe("abc");
  });

  it("codifica parâmetros de caminho", async () => {
    let caminho = "";
    servidorApi.use(
      http.put(`${BASE}/v1/confirmacoes-email/:token`, ({ request }) => {
        caminho = new URL(request.url).pathname;
        return new HttpResponse(null, { status: 204 });
      }),
    );

    await criarCliente().confirmarEmail("a b/c");

    expect(caminho).toBe("/v1/confirmacoes-email/a%20b%2Fc");
  });

  it("envia o cookie de sessão nas requisições", async () => {
    let credenciais = "";
    servidorApi.use(
      http.get(`${BASE}/v1/usuarios/me`, ({ request }) => {
        credenciais = request.credentials;
        return HttpResponse.json({
          id: "1",
          email: "a@b.com",
          nome: null,
          perfil_identificador: "u-1",
        });
      }),
    );

    await criarCliente().obterUsuarioAtual();

    expect(credenciais).toBe("include");
  });

  describe("autenticação", () => {
    const problema = (status: number, detail: string) =>
      HttpResponse.json({ type: "t", title: "Erro", status, detail, instance: "i" }, { status });

    it("obterUsuarioAtual devolve null quando não há sessão (401)", async () => {
      servidorApi.use(http.get(`${BASE}/v1/usuarios/me`, () => problema(401, "sem sessão")));

      expect(await criarCliente().obterUsuarioAtual()).toBeNull();
    });

    it("obterUsuarioAtual repassa falhas que não são 401", async () => {
      servidorApi.use(http.get(`${BASE}/v1/usuarios/me`, () => problema(500, "falha")));

      await expect(criarCliente().obterUsuarioAtual()).rejects.toMatchObject({ status: 500 });
    });

    it("entrarComSenha envia e-mail e senha e devolve o usuário", async () => {
      let corpo: unknown;
      servidorApi.use(
        http.post(`${BASE}/v1/sessoes`, async ({ request }) => {
          corpo = await request.json();
          return HttpResponse.json(
            { id: "1", email: "ana@exemplo.com", nome: null, perfil_identificador: "u-1" },
            { status: 201 },
          );
        }),
      );

      const usuario = await criarCliente().entrarComSenha("ana@exemplo.com", "segredo-longo-1");

      expect(corpo).toEqual({ email: "ana@exemplo.com", senha: "segredo-longo-1" });
      expect(usuario.perfil_identificador).toBe("u-1");
    });

    it("entrarComSenha propaga o 401 como ApiError", async () => {
      servidorApi.use(
        http.post(`${BASE}/v1/sessoes`, () => problema(401, "E-mail ou senha incorretos.")),
      );

      await expect(criarCliente().entrarComSenha("a@b.com", "x")).rejects.toMatchObject({
        status: 401,
        message: "E-mail ou senha incorretos.",
      });
    });

    it("entrarComIdentificador usa a rota de desenvolvimento", async () => {
      let corpo: unknown;
      servidorApi.use(
        http.post(`${BASE}/v1/sessoes/simples`, async ({ request }) => {
          corpo = await request.json();
          return HttpResponse.json(
            { id: "1", email: "dev@simples.local", nome: null, perfil_identificador: "ana" },
            { status: 201 },
          );
        }),
      );

      await criarCliente().entrarComIdentificador("ana");

      expect(corpo).toEqual({ identificador: "ana" });
    });

    it("sair chama DELETE /v1/sessoes/atual", async () => {
      let metodo = "";
      servidorApi.use(
        http.delete(`${BASE}/v1/sessoes/atual`, ({ request }) => {
          metodo = request.method;
          return new HttpResponse(null, { status: 204 });
        }),
      );

      await criarCliente().sair();

      expect(metodo).toBe("DELETE");
    });

    it("cadastrar, solicitarRedefinicaoSenha e redefinirSenha enviam os corpos esperados", async () => {
      const corpos: Record<string, unknown> = {};
      servidorApi.use(
        http.post(`${BASE}/v1/usuarios`, async ({ request }) => {
          corpos.cadastro = await request.json();
          return HttpResponse.json({ mensagem: "ok" }, { status: 202 });
        }),
        http.post(`${BASE}/v1/redefinicoes-senha`, async ({ request }) => {
          corpos.pedido = await request.json();
          return HttpResponse.json({ mensagem: "ok" }, { status: 202 });
        }),
        http.put(`${BASE}/v1/redefinicoes-senha/:token`, async ({ request, params }) => {
          corpos.redefinicao = { token: params.token, corpo: await request.json() };
          return new HttpResponse(null, { status: 204 });
        }),
      );
      const cliente = criarCliente();

      await cliente.cadastrar("ana@exemplo.com", "segredo-longo-1");
      await cliente.solicitarRedefinicaoSenha("ana@exemplo.com");
      await cliente.redefinirSenha("tok", "nova-senha-longa");

      expect(corpos).toEqual({
        cadastro: { email: "ana@exemplo.com", senha: "segredo-longo-1" },
        pedido: { email: "ana@exemplo.com" },
        redefinicao: { token: "tok", corpo: { nova_senha: "nova-senha-longa" } },
      });
    });

    it("urlAutorizacao monta a URL de redirecionamento com o destino codificado", () => {
      const url = criarCliente().urlAutorizacao("google", "/candidaturas?aba=ativas");

      expect(url).toBe(
        `${BASE}/v1/provedores/google/autorizacao?destino=%2Fcandidaturas%3Faba%3Dativas`,
      );
    });
  });

  it("resolve sem valor em respostas 204", async () => {
    let metodo = "";
    servidorApi.use(
      http.delete(`${BASE}/v1/curriculos/:id`, ({ request }) => {
        metodo = request.method;
        return new HttpResponse(null, { status: 204 });
      }),
    );

    const resultado = await criarCliente().removerCurriculo("c1", "adriano");

    expect(resultado).toBeUndefined();
    expect(metodo).toBe("DELETE");
  });

  it("devolve null quando o perfil estruturado não existe (404)", async () => {
    servidorApi.use(
      http.get(`${BASE}/v1/perfil-estruturado/:perfil`, () =>
        HttpResponse.json(
          {
            type: "t",
            title: "Não encontrado",
            status: 404,
            detail: "Perfil estruturado nao encontrado",
            instance: "i",
          },
          { status: 404 },
        ),
      ),
    );

    const perfil = await criarCliente().buscarPerfilEstruturado("adriano");

    expect(perfil).toBeNull();
  });

  it("converte 404 em ApiError nas demais rotas", async () => {
    servidorApi.use(
      http.get(`${BASE}/v1/curriculos/:id/conteudo`, () =>
        HttpResponse.json(
          {
            type: "t",
            title: "Não encontrado",
            status: 404,
            detail: "Currículo não encontrado",
            instance: "i",
          },
          { status: 404 },
        ),
      ),
    );

    const erro = await capturarErro(criarCliente().baixarCurriculo("c1", "adriano"));

    expect(erro).toBeInstanceOf(ApiError);
    expect(erro.status).toBe(404);
  });

  it("converte ProblemaResponse 422 em ApiError com título, detalhe e instância", async () => {
    servidorApi.use(
      http.post(`${BASE}/v1/vagas`, () =>
        HttpResponse.json(
          {
            type: "https://jobsync.com/erros/validacao",
            title: "Erro de validação",
            status: 422,
            detail: "body.texto_descricao: Field required",
            instance: "http://api.test/v1/vagas",
          },
          { status: 422 },
        ),
      ),
    );

    const erro = await capturarErro(
      criarCliente().capturarVaga({ perfil_identificador: "adriano", texto_descricao: "" }),
    );

    expect(erro.status).toBe(422);
    expect(erro.title).toBe("Erro de validação");
    expect(erro.detail).toBe("body.texto_descricao: Field required");
    expect(erro.instance).toBe("http://api.test/v1/vagas");
    expect(erro.message).toBe("body.texto_descricao: Field required");
  });

  it("converte 500 sem corpo JSON em ApiError genérico", async () => {
    servidorApi.use(
      http.get(`${BASE}/v1/candidaturas`, () => new HttpResponse("falhou", { status: 500 })),
    );

    const erro = await capturarErro(criarCliente().listarCandidaturas("adriano"));

    expect(erro.status).toBe(500);
    expect(erro.title).toBe("Erro inesperado da API");
  });

  it("converte falha de rede em ApiError de conexão", async () => {
    servidorApi.use(http.get(`${BASE}/v1/health`, () => HttpResponse.error()));

    const erro = await capturarErro(criarCliente().verificarSaude());

    expect(erro.status).toBe(0);
    expect(erro.title).toBe("Falha de conexão");
  });

  it("aborta pelo timeout padrão nas rotas comuns", async () => {
    servidorApi.use(
      http.get(`${BASE}/v1/vagas`, async () => {
        await delay(200);
        return HttpResponse.json({ items: [], total: 0, limite: 100, offset: 0 });
      }),
    );

    const erro = await capturarErro(criarCliente({ timeoutPadraoMs: 20 }).listarVagas("adriano"));

    expect(erro.title).toBe("Tempo esgotado");
  });

  it("usa o timeout longo nas rotas de IA", async () => {
    servidorApi.use(
      http.post(`${BASE}/v1/vagas/avaliacoes`, async () => {
        await delay(100);
        return HttpResponse.json({ score: 80 });
      }),
    );

    const avaliacao = await criarCliente({ timeoutPadraoMs: 20, timeoutIaMs: 2000 }).avaliarVaga(
      "Vaga",
    );

    expect(avaliacao.score).toBe(80);
  });

  it("gera o rascunho adaptado pela rota de IA, sem PDF", async () => {
    let caminho = "";
    servidorApi.use(
      http.post(`${BASE}/v1/curriculos/:id/rascunhos-adaptados`, ({ request }) => {
        caminho = new URL(request.url).pathname;
        return HttpResponse.json({
          rascunho: { nome_completo: "Ana", secoes: [], experiencias: null },
        });
      }),
    );

    const resposta = await criarCliente().gerarRascunhoAdaptado("perfil-estruturado", {
      descricao_vaga: "Vaga",
      idioma_alvo: "pt",
      cargo_alvo: "Dev",
      empresa_alvo: "TechCorp",
      perfil_identificador: "ana",
    });

    expect(caminho).toBe("/v1/curriculos/perfil-estruturado/rascunhos-adaptados");
    expect(resposta.rascunho.nome_completo).toBe("Ana");
  });

  it("envia o rascunho revisado para gerar o PDF", async () => {
    let corpoRecebido: unknown;
    servidorApi.use(
      http.post(`${BASE}/v1/curriculos-revisados`, async ({ request }) => {
        corpoRecebido = await request.json();
        return HttpResponse.json({ nome_arquivo: "Ana.pdf", pdf_base64: "JVBERg==" });
      }),
    );
    const dados = {
      rascunho: { nome_completo: "Ana Editada", secoes: [], experiencias: null },
      idioma_alvo: "pt",
      cargo_alvo: "Dev",
      empresa_alvo: "TechCorp",
    };

    const resposta = await criarCliente().gerarPdfCurriculoRevisado(dados);

    expect(corpoRecebido).toEqual(dados);
    expect(resposta.nome_arquivo).toBe("Ana.pdf");
  });

  it("pede sugestão de seção pela rota de IA e devolve o texto sugerido", async () => {
    let corpoRecebido: unknown;
    servidorApi.use(
      http.post(`${BASE}/v1/secoes-curriculo/sugestoes`, async ({ request }) => {
        corpoRecebido = await request.json();
        return HttpResponse.json({ conteudo_sugerido: "Texto novo." });
      }),
    );
    const dados = { secao: { tipo: "PERFIL" as const, titulo: "Perfil", conteudo: "Texto." } };

    const resposta = await criarCliente().sugerirAjusteSecao(dados);

    expect(corpoRecebido).toEqual(dados);
    expect(resposta.conteudo_sugerido).toBe("Texto novo.");
  });

  it("pede sugestão de experiência e devolve a descrição sugerida", async () => {
    let corpoRecebido: unknown;
    servidorApi.use(
      http.post(`${BASE}/v1/experiencias-profissionais/sugestoes`, async ({ request }) => {
        corpoRecebido = await request.json();
        return HttpResponse.json({ descricao_sugerida: "Descrição nova." });
      }),
    );
    const dados = {
      experiencia: { cargo: "Dev", empresa: "TechCorp", periodo: "2024", descricao: "Antiga." },
    };

    const resposta = await criarCliente().sugerirAjusteExperiencia(dados);

    expect(corpoRecebido).toEqual(dados);
    expect(resposta.descricao_sugerida).toBe("Descrição nova.");
  });

  it("usa o timeout longo nas sugestões de IA", async () => {
    servidorApi.use(
      http.post(`${BASE}/v1/secoes-curriculo/sugestoes`, async () => {
        await delay(60);
        return HttpResponse.json({ conteudo_sugerido: "ok" });
      }),
    );

    const resposta = await criarCliente({
      timeoutPadraoMs: 20,
      timeoutIaMs: 500,
    }).sugerirAjusteSecao({
      secao: { tipo: "PERFIL", titulo: "Perfil", conteudo: "Texto." },
    });

    expect(resposta.conteudo_sugerido).toBe("ok");
  });

  describe("sugestão de experiência adaptada", () => {
    const dados = {
      experiencia: {
        cargo: "Dev",
        empresa: "TechCorp",
        periodo: "2024",
        conquistas: ["Criei APIs.", "Reduzi custos."],
        contexto: "Empresa de pagamentos.",
      },
      contexto_vaga: {
        descricao_vaga: "Vaga Java",
        idioma_alvo: "en",
        analise_vaga: { requisitos: [], ambiguidade: [], texto_original: "Vaga Java" },
      },
    };

    it("envia as conquistas, o contexto e a vaga e devolve os textos refinados", async () => {
      let corpoRecebido: unknown;
      servidorApi.use(
        http.post(`${BASE}/v1/experiencias-adaptadas/sugestoes`, async ({ request }) => {
          corpoRecebido = await request.json();
          return HttpResponse.json({
            conquistas: ["Desenvolvi APIs REST."],
            contexto: "Plataforma de pagamentos.",
          });
        }),
      );

      const resposta = await criarCliente().sugerirAjusteExperienciaAdaptada(dados);

      expect(corpoRecebido).toEqual(dados);
      expect(resposta).toEqual({
        conquistas: ["Desenvolvi APIs REST."],
        contexto: "Plataforma de pagamentos.",
      });
    });

    it("usa o timeout longo das rotas de IA", async () => {
      servidorApi.use(
        http.post(`${BASE}/v1/experiencias-adaptadas/sugestoes`, async () => {
          await delay(60);
          return HttpResponse.json({ conquistas: ["ok"], contexto: "" });
        }),
      );

      const resposta = await criarCliente({
        timeoutPadraoMs: 20,
        timeoutIaMs: 500,
      }).sugerirAjusteExperienciaAdaptada(dados);

      expect(resposta.conquistas).toEqual(["ok"]);
    });

    it("traz a mensagem do servidor quando a IA está indisponível", async () => {
      servidorApi.use(
        http.post(`${BASE}/v1/experiencias-adaptadas/sugestoes`, () =>
          HttpResponse.json(
            {
              type: "t",
              title: "Sugestão de IA indisponível",
              status: 502,
              detail: "O serviço de sugestões de IA está indisponível.",
              instance: "i",
            },
            { status: 502 },
          ),
        ),
      );

      const erro = await capturarErro(criarCliente().sugerirAjusteExperienciaAdaptada(dados));

      expect(erro.status).toBe(502);
      expect(erro.message).toBe("O serviço de sugestões de IA está indisponível.");
    });
  });

  describe("confirmação de candidatura a partir do ajuste", () => {
    const dados = {
      perfil_identificador: "ana",
      cargo: "Engenheiro de Software",
      empresa: "TechCorp",
      descricao_vaga: "Vaga de backend.",
      nome_arquivo: "Ana-Engenheiro-TechCorp.pdf",
      pdf_base64: "JVBERg==",
    };

    it("envia a vaga e o PDF gerado e devolve a candidatura criada", async () => {
      let corpoRecebido: unknown;
      servidorApi.use(
        http.post(`${BASE}/v1/candidaturas-ajustadas`, async ({ request }) => {
          corpoRecebido = await request.json();
          return HttpResponse.json(
            { id: "c1", status: "APLICADO", empresa: "TechCorp", cargo: "Engenheiro de Software" },
            { status: 201 },
          );
        }),
      );

      const candidatura = await criarCliente().confirmarCandidaturaAjustada(dados);

      expect(corpoRecebido).toEqual(dados);
      expect(candidatura.id).toBe("c1");
      expect(candidatura.status).toBe("APLICADO");
    });

    it("converte 409 de biblioteca cheia em ApiError com a mensagem do servidor", async () => {
      servidorApi.use(
        http.post(`${BASE}/v1/candidaturas-ajustadas`, () =>
          HttpResponse.json(
            {
              type: "https://jobsync.com/erros/limite-curriculos-salvos",
              title: "Biblioteca de currículos cheia",
              status: 409,
              detail:
                "Sua biblioteca de currículos está cheia. Remova um currículo para confirmar a candidatura.",
              instance: "http://api.test/v1/candidaturas-ajustadas",
            },
            { status: 409 },
          ),
        ),
      );

      const erro = await capturarErro(criarCliente().confirmarCandidaturaAjustada(dados));

      expect(erro.status).toBe(409);
      expect(erro.title).toBe("Biblioteca de currículos cheia");
      expect(erro.message).toBe(
        "Sua biblioteca de currículos está cheia. Remova um currículo para confirmar a candidatura.",
      );
    });

    it("converte 422 em ApiError com o detalhe do problema", async () => {
      servidorApi.use(
        http.post(`${BASE}/v1/candidaturas-ajustadas`, () =>
          HttpResponse.json(
            {
              type: "https://jobsync.com/erros/422",
              title: "A empresa da candidatura é obrigatória.",
              status: 422,
              detail: "A empresa da candidatura é obrigatória.",
              instance: "http://api.test/v1/candidaturas-ajustadas",
            },
            { status: 422 },
          ),
        ),
      );

      const erro = await capturarErro(
        criarCliente().confirmarCandidaturaAjustada({ ...dados, empresa: "" }),
      );

      expect(erro.status).toBe(422);
      expect(erro.message).toBe("A empresa da candidatura é obrigatória.");
    });

    it("usa o timeout padrão, não o das rotas de IA", async () => {
      servidorApi.use(
        http.post(`${BASE}/v1/candidaturas-ajustadas`, async () => {
          await delay(200);
          return HttpResponse.json({ id: "c1", status: "APLICADO" }, { status: 201 });
        }),
      );

      const erro = await capturarErro(
        criarCliente({ timeoutPadraoMs: 20, timeoutIaMs: 5000 }).confirmarCandidaturaAjustada(
          dados,
        ),
      );

      expect(erro.title).toBe("Tempo esgotado");
    });
  });

  it("move a candidatura enviando o novo status", async () => {
    let corpoRecebido: unknown;
    servidorApi.use(
      http.post(`${BASE}/v1/candidaturas/:id/submissao`, async ({ request }) => {
        corpoRecebido = await request.json();
        return HttpResponse.json({ id: "c1", status: "ENTREVISTA" });
      }),
    );

    await criarCliente().moverCandidatura("c1", "ENTREVISTA");

    expect(corpoRecebido).toEqual({ novo_status: "entrevista" });
  });

  it("envia a posição na coluna de destino quando informada", async () => {
    let corpoRecebido: unknown;
    servidorApi.use(
      http.post(`${BASE}/v1/candidaturas/:id/submissao`, async ({ request }) => {
        corpoRecebido = await request.json();
        return HttpResponse.json({ id: "c1", status: "OFERTA", posicao: 2 });
      }),
    );

    const candidatura = await criarCliente().moverCandidatura("c1", "OFERTA", 2);

    expect(corpoRecebido).toEqual({ novo_status: "oferta", posicao: 2 });
    expect(candidatura.posicao).toBe(2);
  });

  it("envia a posição zero, sem confundi-la com posição ausente", async () => {
    let corpoRecebido: unknown;
    servidorApi.use(
      http.post(`${BASE}/v1/candidaturas/:id/submissao`, async ({ request }) => {
        corpoRecebido = await request.json();
        return HttpResponse.json({ id: "c1", status: "OFERTA", posicao: 0 });
      }),
    );

    await criarCliente().moverCandidatura("c1", "OFERTA", 0);

    expect(corpoRecebido).toEqual({ novo_status: "oferta", posicao: 0 });
  });

  it("converte 404 e 422 do movimento em ApiError", async () => {
    servidorApi.use(
      http.post(`${BASE}/v1/candidaturas/:id/submissao`, () =>
        HttpResponse.json({ detail: "Candidatura não encontrada." }, { status: 404 }),
      ),
    );
    const naoEncontrada = await capturarErro(criarCliente().moverCandidatura("x", "OFERTA", 0));

    servidorApi.use(
      http.post(`${BASE}/v1/candidaturas/:id/submissao`, () =>
        HttpResponse.json({ detail: "Posição inválida." }, { status: 422 }),
      ),
    );
    const invalida = await capturarErro(criarCliente().moverCandidatura("c1", "OFERTA", 0));

    expect([naoEncontrada.status, invalida.status]).toEqual([404, 422]);
  });
});
