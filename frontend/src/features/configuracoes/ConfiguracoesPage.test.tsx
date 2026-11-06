import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

describe("ConfiguracoesPage", () => {
  it("explica como usar a extensão", async () => {
    renderizarApp({ caminho: "/configuracoes", perfil: "adriano" });

    const passos = await screen.findByRole("list", { name: "Como usar a extensão" });
    expect(passos).toHaveTextContent("extensao-chrome");
    expect(passos).toHaveTextContent("Salvar token");
    expect(screen.getByText(/localhost:8502/)).toBeInTheDocument();
  });

  it("gera o token do perfil e permite copiar", async () => {
    let corpo: unknown;
    servidorApi.use(
      http.post(`${API_TESTE}/v1/tokens-captura`, async ({ request }) => {
        corpo = await request.json();
        return HttpResponse.json(
          { token: "tok-123", perfil_identificador: "adriano" },
          { status: 201 },
        );
      }),
    );
    const escrever = vi.fn(() => Promise.resolve());
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: escrever },
      configurable: true,
    });
    renderizarApp({ caminho: "/configuracoes", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("button", { name: "Gerar token" }));

    expect(await screen.findByLabelText("Token de captura")).toHaveValue("tok-123");
    expect(screen.getByText(/o token não é exibido de novo/)).toBeInTheDocument();
    expect(corpo).toEqual({ perfil_identificador: "adriano" });
    await userEvent.click(screen.getByRole("button", { name: "Copiar token" }));
    expect(escrever).toHaveBeenCalledWith("tok-123");
    expect(await screen.findByRole("status")).toHaveTextContent("Token copiado.");
  });

  it("mostra a falha ao gerar o token", async () => {
    servidorApi.use(
      http.post(`${API_TESTE}/v1/tokens-captura`, () =>
        HttpResponse.json(
          { type: "t", title: "Erro", status: 500, detail: "Falha ao gerar.", instance: "i" },
          { status: 500 },
        ),
      ),
    );
    renderizarApp({ caminho: "/configuracoes", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("button", { name: "Gerar token" }));

    expect(await screen.findByText("Falha ao gerar.")).toBeInTheDocument();
  });
});
