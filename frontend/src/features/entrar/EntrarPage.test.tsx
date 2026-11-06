import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { CHAVE_SESSAO } from "../../shared/sessao/sessao-context";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

describe("EntrarPage", () => {
  it("exige o identificador sem chamar a API", async () => {
    renderizarApp({ caminho: "/entrar" });

    await userEvent.click(await screen.findByRole("button", { name: "Entrar" }));

    const campo = screen.getByLabelText("Identificador");
    expect(campo).toHaveAccessibleDescription(/Informe seu identificador\./);
    expect(campo).toHaveAttribute("aria-invalid", "true");
  });

  it("entra, grava a sessão e volta para a página pedida", async () => {
    let identificadorRecebido = "";
    servidorApi.use(
      http.get(`${API_TESTE}/v1/perfis/:id`, ({ params }) => {
        identificadorRecebido = String(params.id);
        return HttpResponse.json({ identificador: String(params.id) });
      }),
    );
    renderizarApp({ caminho: "/candidaturas" });

    await userEvent.type(await screen.findByLabelText("Identificador"), "  adriano  ");
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(
      await screen.findByRole("heading", { level: 1, name: "Candidaturas" }),
    ).toBeInTheDocument();
    expect(identificadorRecebido).toBe("adriano");
    expect(localStorage.getItem(CHAVE_SESSAO)).toBe("adriano");
  });

  it("entra pela tela Entrar e vai para a Visão geral", async () => {
    servidorApi.use(
      http.get(`${API_TESTE}/v1/perfis/:id`, () => HttpResponse.json({ identificador: "ana" })),
    );
    renderizarApp({ caminho: "/entrar" });

    await userEvent.type(await screen.findByLabelText("Identificador"), "ana{Enter}");

    expect(
      await screen.findByRole("heading", { level: 1, name: "Visão geral" }),
    ).toBeInTheDocument();
  });

  it("mostra o erro da API e permanece em Entrar", async () => {
    servidorApi.use(
      http.get(`${API_TESTE}/v1/perfis/:id`, () =>
        HttpResponse.json(
          {
            type: "t",
            title: "Erro de validação",
            status: 422,
            detail: "Identificador inválido.",
            instance: "i",
          },
          { status: 422 },
        ),
      ),
    );
    renderizarApp({ caminho: "/entrar" });

    await userEvent.type(await screen.findByLabelText("Identificador"), "x");
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByText("Identificador inválido.")).toBeInTheDocument();
    expect(screen.getByLabelText("Identificador")).toHaveAccessibleDescription(
      /Identificador inválido\./,
    );
    expect(localStorage.getItem(CHAVE_SESSAO)).toBeNull();
  });
});
