import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { API_TESTE, renderizarApp } from "../test/renderizar-app";
import { servidorApi } from "../test/servidor-api";

describe("Rotas e AppShell", () => {
  it("sem sessão, uma rota protegida leva para Entrar", async () => {
    renderizarApp({ caminho: "/candidaturas" });

    expect(await screen.findByRole("heading", { name: "Entrar" })).toBeInTheDocument();
  });

  it("com sessão, mostra o shell com a trilha e o item ativo do menu", async () => {
    renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });

    const trilha = await screen.findByRole("navigation", { name: "Trilha" });
    expect(within(trilha).getByText("Candidaturas")).toHaveAttribute("aria-current", "page");
    const menu = screen.getByRole("navigation", { name: "Menu principal" });
    expect(within(menu).getByRole("link", { name: /Candidaturas/ })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("heading", { level: 1, name: "Candidaturas" })).toBeInTheDocument();
    expect(document.title).toBe("Candidaturas · job-sync");
  });

  it("navega pelo menu lateral", async () => {
    renderizarApp({ caminho: "/", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("link", { name: /Meu perfil/ }));

    expect(
      await screen.findByRole("heading", { level: 1, name: "Meu perfil" }),
    ).toBeInTheDocument();
  });

  it("mostra o usuário logado e Sair encerra a sessão no servidor e volta para Entrar", async () => {
    let sessaoEncerrada = false;
    servidorApi.use(
      http.delete(`${API_TESTE}/v1/sessoes/atual`, () => {
        sessaoEncerrada = true;
        return new HttpResponse(null, { status: 204 });
      }),
    );
    renderizarApp({ caminho: "/", perfil: "adriano" });
    expect(await screen.findByText("adriano")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Sair" }));

    expect(await screen.findByRole("heading", { name: "Entrar" })).toBeInTheDocument();
    expect(sessaoEncerrada).toBe(true);
  });

  it("uma resposta 401 em qualquer tela encerra a sessão local e leva para Entrar", async () => {
    servidorApi.use(
      http.get(`${API_TESTE}/v1/candidaturas`, () =>
        HttpResponse.json(
          {
            type: "t",
            title: "Não autenticado",
            status: 401,
            detail: "Faça login para continuar.",
            instance: "i",
          },
          { status: 401 },
        ),
      ),
    );
    renderizarApp({ caminho: "/candidaturas", perfil: "adriano" });

    expect(await screen.findByRole("heading", { name: "Entrar" })).toBeInTheDocument();
  });

  it("pergunta ao servidor se há sessão e mostra Carregando até a resposta", async () => {
    servidorApi.use(
      http.get(`${API_TESTE}/v1/usuarios/me`, async () => {
        await new Promise((resolver) => setTimeout(resolver, 30));
        return HttpResponse.json({
          id: "1",
          email: "ana@exemplo.com",
          nome: "Ana",
          perfil_identificador: "u-ana",
        });
      }),
    );
    renderizarApp({ caminho: "/candidaturas", consultarSessao: true });

    expect(screen.getByText("Carregando…")).toBeInTheDocument();
    expect(
      await screen.findByRole("heading", { level: 1, name: "Candidaturas" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Ana")).toBeInTheDocument();
  });

  it("consultar a sessão sem cookie válido leva para Entrar", async () => {
    renderizarApp({ caminho: "/candidaturas", consultarSessao: true });

    expect(await screen.findByRole("heading", { name: "Entrar" })).toBeInTheDocument();
  });

  it("o botão de menu móvel abre e fecha a navegação", async () => {
    renderizarApp({ caminho: "/", perfil: "adriano" });
    const botao = await screen.findByRole("button", { name: "Abrir menu" });
    expect(botao).toHaveAttribute("aria-expanded", "false");

    await userEvent.click(botao);

    expect(screen.getByRole("button", { name: "Fechar menu" })).toHaveAttribute(
      "aria-expanded",
      "true",
    );

    await userEvent.keyboard("{Escape}");

    expect(screen.getByRole("button", { name: "Abrir menu" })).toHaveAttribute(
      "aria-expanded",
      "false",
    );
  });

  it("rota desconhecida volta para a Visão geral", async () => {
    renderizarApp({ caminho: "/nao-existe", perfil: "adriano" });

    expect(
      await screen.findByRole("heading", { level: 1, name: /^(Bom dia|Boa tarde|Boa noite), / }),
    ).toBeInTheDocument();
  });

  it("com sessão, Entrar redireciona para a Visão geral", async () => {
    renderizarApp({ caminho: "/entrar", perfil: "adriano" });

    expect(
      await screen.findByRole("heading", { level: 1, name: /^(Bom dia|Boa tarde|Boa noite), / }),
    ).toBeInTheDocument();
  });

  it("oferece um link para pular direto ao conteúdo", async () => {
    renderizarApp({ caminho: "/", perfil: "adriano" });

    expect(await screen.findByRole("link", { name: "Pular para o conteúdo" })).toHaveAttribute(
      "href",
      "#conteudo",
    );
  });
});
