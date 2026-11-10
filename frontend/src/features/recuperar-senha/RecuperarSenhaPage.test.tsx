import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

describe("RecuperarSenhaPage", () => {
  it("exige o e-mail", async () => {
    renderizarApp({ caminho: "/recuperar-senha" });

    await userEvent.click(await screen.findByRole("button", { name: "Enviar link" }));

    expect(screen.getByLabelText("E-mail")).toHaveAccessibleDescription(/Informe o e-mail\./);
  });

  it("pede o link e mostra uma resposta que não revela se o e-mail existe", async () => {
    let corpo: unknown;
    servidorApi.use(
      http.post(`${API_TESTE}/v1/redefinicoes-senha`, async ({ request }) => {
        corpo = await request.json();
        return HttpResponse.json({ mensagem: "ok" }, { status: 202 });
      }),
    );
    renderizarApp({ caminho: "/recuperar-senha" });

    await userEvent.type(await screen.findByLabelText("E-mail"), " ana@exemplo.com ");
    await userEvent.click(screen.getByRole("button", { name: "Enviar link" }));

    expect(await screen.findByText(/Se esse e-mail tiver cadastro/)).toBeInTheDocument();
    expect(corpo).toEqual({ email: "ana@exemplo.com" });
  });

  it("mostra erro quando o envio falha", async () => {
    servidorApi.use(http.post(`${API_TESTE}/v1/redefinicoes-senha`, () => HttpResponse.error()));
    renderizarApp({ caminho: "/recuperar-senha" });

    await userEvent.type(await screen.findByLabelText("E-mail"), "ana@exemplo.com");
    await userEvent.click(screen.getByRole("button", { name: "Enviar link" }));

    expect(await screen.findByText(/Não foi possível enviar agora/)).toBeInTheDocument();
  });
});
