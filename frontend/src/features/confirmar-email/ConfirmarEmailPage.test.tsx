import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

const problema = (status: number) =>
  HttpResponse.json(
    { type: "t", title: "Erro", status, detail: "Link inválido ou expirado.", instance: "i" },
    { status },
  );

describe("ConfirmarEmailPage", () => {
  it("não consome o link ao abrir a página, só quando o usuário confirma", async () => {
    let chamadas = 0;
    servidorApi.use(
      http.put(`${API_TESTE}/v1/confirmacoes-email/:token`, () => {
        chamadas += 1;
        return new HttpResponse(null, { status: 204 });
      }),
    );
    renderizarApp({ caminho: "/confirmar-email?token=abc" });

    await screen.findByRole("button", { name: "Confirmar meu e-mail" });

    expect(chamadas).toBe(0);
  });

  it("confirma o e-mail com o token do link e leva a Entrar", async () => {
    let tokenRecebido = "";
    servidorApi.use(
      http.put(`${API_TESTE}/v1/confirmacoes-email/:token`, ({ params }) => {
        tokenRecebido = String(params.token);
        return new HttpResponse(null, { status: 204 });
      }),
    );
    renderizarApp({ caminho: "/confirmar-email?token=abc123" });

    await userEvent.click(await screen.findByRole("button", { name: "Confirmar meu e-mail" }));

    expect(await screen.findByRole("heading", { name: "E-mail confirmado" })).toBeInTheDocument();
    expect(tokenRecebido).toBe("abc123");
    expect(screen.getByRole("link", { name: "Entrar" })).toHaveAttribute("href", "/entrar");
  });

  it("explica quando o link é inválido ou expirou", async () => {
    servidorApi.use(http.put(`${API_TESTE}/v1/confirmacoes-email/:token`, () => problema(400)));
    renderizarApp({ caminho: "/confirmar-email?token=velho" });

    await userEvent.click(await screen.findByRole("button", { name: "Confirmar meu e-mail" }));

    expect(await screen.findByText(/Link inválido ou expirado/)).toBeInTheDocument();
  });

  it("mostra mensagem genérica em falhas que não são do link", async () => {
    servidorApi.use(http.put(`${API_TESTE}/v1/confirmacoes-email/:token`, () => problema(500)));
    renderizarApp({ caminho: "/confirmar-email?token=abc" });

    await userEvent.click(await screen.findByRole("button", { name: "Confirmar meu e-mail" }));

    expect(await screen.findByText(/Não foi possível confirmar agora/)).toBeInTheDocument();
  });

  it("sem token no endereço, avisa que o link está incompleto", async () => {
    renderizarApp({ caminho: "/confirmar-email" });

    expect(await screen.findByText(/Link incompleto/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirmar meu e-mail" })).not.toBeInTheDocument();
  });

  it("abre mesmo com sessão ativa, porque o link vem do e-mail", async () => {
    renderizarApp({ caminho: "/confirmar-email?token=abc", perfil: "adriano" });

    expect(await screen.findByRole("button", { name: "Confirmar meu e-mail" })).toBeInTheDocument();
  });
});
