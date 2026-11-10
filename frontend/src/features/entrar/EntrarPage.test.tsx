import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

const usuario = {
  id: "1",
  email: "ana@exemplo.com",
  nome: "Ana",
  perfil_identificador: "u-ana",
};

const problema = (status: number, detail: string) =>
  HttpResponse.json({ type: "t", title: "Erro", status, detail, instance: "i" }, { status });

async function preencher(email: string, senha: string) {
  await userEvent.type(await screen.findByLabelText("E-mail"), email);
  await userEvent.type(screen.getByLabelText("Senha"), senha);
}

describe("EntrarPage", () => {
  it("exige e-mail e senha sem chamar a API", async () => {
    renderizarApp({ caminho: "/entrar" });

    await userEvent.click(await screen.findByRole("button", { name: "Entrar" }));

    const campo = screen.getByLabelText("Senha");
    expect(campo).toHaveAccessibleDescription(/Informe o e-mail e a senha\./);
    expect(campo).toHaveAttribute("aria-invalid", "true");
  });

  it("entra com e-mail e senha e volta para a página pedida", async () => {
    let corpo: unknown;
    servidorApi.use(
      http.post(`${API_TESTE}/v1/sessoes`, async ({ request }) => {
        corpo = await request.json();
        return HttpResponse.json(usuario, { status: 201 });
      }),
    );
    renderizarApp({ caminho: "/candidaturas" });

    await preencher("  ana@exemplo.com  ", "segredo-longo-1");
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(
      await screen.findByRole("heading", { level: 1, name: "Candidaturas" }),
    ).toBeInTheDocument();
    expect(corpo).toEqual({ email: "ana@exemplo.com", senha: "segredo-longo-1" });
  });

  it("entra pela tela Entrar e vai para a Visão geral", async () => {
    servidorApi.use(
      http.post(`${API_TESTE}/v1/sessoes`, () => HttpResponse.json(usuario, { status: 201 })),
    );
    renderizarApp({ caminho: "/entrar" });

    await preencher("ana@exemplo.com", "segredo-longo-1");
    await userEvent.type(screen.getByLabelText("Senha"), "{Enter}");

    expect(
      await screen.findByRole("heading", { level: 1, name: /^(Bom dia|Boa tarde|Boa noite), / }),
    ).toBeInTheDocument();
  });

  it("credenciais incorretas mostram uma mensagem única e mantêm a tela", async () => {
    servidorApi.use(
      http.post(`${API_TESTE}/v1/sessoes`, () => problema(401, "E-mail ou senha incorretos.")),
    );
    renderizarApp({ caminho: "/entrar" });

    await preencher("ana@exemplo.com", "senha-errada-1");
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByText(/E-mail ou senha incorretos\./)).toBeInTheDocument();
    expect(screen.getByText(/confirme o e-mail pelo link/)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Entrar" })).toBeInTheDocument();
  });

  it("excesso de tentativas mostra aviso de espera", async () => {
    servidorApi.use(
      http.post(`${API_TESTE}/v1/sessoes`, () => problema(429, "Muitas tentativas.")),
    );
    renderizarApp({ caminho: "/entrar" });

    await preencher("ana@exemplo.com", "qualquer-senha-1");
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(
      await screen.findByText(/Muitas tentativas\. Tente novamente em alguns minutos\./),
    ).toBeInTheDocument();
  });

  it("oferece Entrar com Google levando o destino pedido", async () => {
    renderizarApp({ caminho: "/candidaturas" });

    const link = await screen.findByRole("link", { name: "Entrar com Google" });

    expect(link).toHaveAttribute(
      "href",
      `${API_TESTE}/v1/provedores/google/autorizacao?destino=%2Fcandidaturas`,
    );
  });

  it("mostra o logotipo do Google no botão sem alterar o nome acessível", async () => {
    renderizarApp({ caminho: "/entrar" });

    const link = await screen.findByRole("link", { name: "Entrar com Google" });
    const icone = within(link).getByTestId("icone-google");

    expect(icone).toHaveAttribute("aria-hidden", "true");
    expect(link).toHaveAccessibleName("Entrar com Google");
  });

  it("não mostra o Google quando o servidor não o oferece", async () => {
    servidorApi.use(
      http.get(`${API_TESTE}/v1/provedores`, () =>
        HttpResponse.json({ provedores: [], senha: true, login_simples: false }),
      ),
    );
    renderizarApp({ caminho: "/entrar" });

    await screen.findByLabelText("E-mail");

    expect(screen.queryByRole("link", { name: "Entrar com Google" })).not.toBeInTheDocument();
  });

  it("continua usável por e-mail e senha se a lista de provedores falhar", async () => {
    servidorApi.use(http.get(`${API_TESTE}/v1/provedores`, () => problema(500, "falha")));
    renderizarApp({ caminho: "/entrar" });

    expect(await screen.findByLabelText("E-mail")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Entrar com Google" })).not.toBeInTheDocument();
  });

  it.each([
    ["acesso_negado", /cancelou o login com o Google/],
    ["estado_invalido", /Não foi possível concluir o login/],
    ["email_nao_verificado", /não confirmou o e-mail/],
    ["provedor_indisponivel", /indisponível agora/],
    ["codigo_desconhecido", /Não foi possível entrar/],
  ])("mostra a mensagem do erro %s vindo do retorno do provedor", async (codigo, mensagem) => {
    renderizarApp({ caminho: `/entrar?erro=${codigo}` });

    expect(await screen.findByText(mensagem)).toBeInTheDocument();
  });

  it("não mostra erro quando não há parâmetro erro", async () => {
    renderizarApp({ caminho: "/entrar" });

    await screen.findByLabelText("E-mail");

    expect(screen.queryByText(/cancelou o login com o Google/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Não foi possível (concluir|entrar)/)).not.toBeInTheDocument();
  });

  it("liga para cadastro e recuperação de senha", async () => {
    renderizarApp({ caminho: "/entrar" });

    expect(await screen.findByRole("link", { name: "Criar conta" })).toHaveAttribute(
      "href",
      "/cadastrar",
    );
    expect(screen.getByRole("link", { name: "Esqueci minha senha" })).toHaveAttribute(
      "href",
      "/recuperar-senha",
    );
  });

  describe("login por identificador (somente desenvolvimento)", () => {
    beforeEach(() => {
      servidorApi.use(
        http.get(`${API_TESTE}/v1/provedores`, () =>
          HttpResponse.json({ provedores: [], senha: true, login_simples: true }),
        ),
      );
    });

    it("aparece só quando o servidor o habilita e entra no perfil informado", async () => {
      let corpo: unknown;
      servidorApi.use(
        http.post(`${API_TESTE}/v1/sessoes/simples`, async ({ request }) => {
          corpo = await request.json();
          return HttpResponse.json({ ...usuario, perfil_identificador: "ana" }, { status: 201 });
        }),
      );
      renderizarApp({ caminho: "/entrar" });

      await userEvent.type(
        await screen.findByLabelText("Identificador (somente desenvolvimento)"),
        "  ana  ",
      );
      await userEvent.click(screen.getByRole("button", { name: "Entrar por identificador" }));

      expect(
        await screen.findByRole("heading", { level: 1, name: /^(Bom dia|Boa tarde|Boa noite), / }),
      ).toBeInTheDocument();
      expect(corpo).toEqual({ identificador: "ana" });
    });

    it("fica oculto quando o servidor não o habilita", async () => {
      servidorApi.use(
        http.get(`${API_TESTE}/v1/provedores`, () =>
          HttpResponse.json({ provedores: [], senha: true, login_simples: false }),
        ),
      );
      renderizarApp({ caminho: "/entrar" });

      await screen.findByLabelText("E-mail");

      expect(
        screen.queryByLabelText("Identificador (somente desenvolvimento)"),
      ).not.toBeInTheDocument();
    });
  });
});
