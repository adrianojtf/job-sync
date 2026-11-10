import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

const problema = (status: number, detail: string) =>
  HttpResponse.json({ type: "t", title: "Erro", status, detail, instance: "i" }, { status });

async function preencher(senha: string, confirmacao: string) {
  await userEvent.type(await screen.findByLabelText("Nova senha"), senha);
  await userEvent.type(screen.getByLabelText("Confirmar nova senha"), confirmacao);
}

describe("RedefinirSenhaPage", () => {
  it("redefine a senha com o token do link", async () => {
    let recebido: unknown;
    servidorApi.use(
      http.put(`${API_TESTE}/v1/redefinicoes-senha/:token`, async ({ params, request }) => {
        recebido = { token: params.token, corpo: await request.json() };
        return new HttpResponse(null, { status: 204 });
      }),
    );
    renderizarApp({ caminho: "/redefinir-senha?token=tok1" });

    await preencher("nova-senha-longa-1", "nova-senha-longa-1");
    await userEvent.click(screen.getByRole("button", { name: "Salvar nova senha" }));

    expect(await screen.findByRole("heading", { name: "Senha redefinida" })).toBeInTheDocument();
    expect(recebido).toEqual({ token: "tok1", corpo: { nova_senha: "nova-senha-longa-1" } });
  });

  it("recusa senhas diferentes sem chamar a API", async () => {
    renderizarApp({ caminho: "/redefinir-senha?token=tok1" });

    await preencher("nova-senha-longa-1", "outra-senha-longa-2");
    await userEvent.click(screen.getByRole("button", { name: "Salvar nova senha" }));

    expect(await screen.findByText("As senhas não conferem.")).toBeInTheDocument();
  });

  it("mostra o motivo quando a senha não atende à política", async () => {
    servidorApi.use(
      http.put(`${API_TESTE}/v1/redefinicoes-senha/:token`, () =>
        problema(422, "A senha deve ter entre 10 e 128 caracteres."),
      ),
    );
    renderizarApp({ caminho: "/redefinir-senha?token=tok1" });

    await preencher("curta", "curta");
    await userEvent.click(screen.getByRole("button", { name: "Salvar nova senha" }));

    expect(
      await screen.findByText("A senha deve ter entre 10 e 128 caracteres."),
    ).toBeInTheDocument();
  });

  it("oferece pedir novo link quando o link é inválido ou expirou", async () => {
    servidorApi.use(
      http.put(`${API_TESTE}/v1/redefinicoes-senha/:token`, () =>
        problema(400, "Link inválido ou expirado."),
      ),
    );
    renderizarApp({ caminho: "/redefinir-senha?token=velho" });

    await preencher("nova-senha-longa-1", "nova-senha-longa-1");
    await userEvent.click(screen.getByRole("button", { name: "Salvar nova senha" }));

    expect(await screen.findByText(/Link inválido ou expirado/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Peça um novo link" })).toHaveAttribute(
      "href",
      "/recuperar-senha",
    );
  });

  it("sem token no endereço, avisa que o link está incompleto", async () => {
    renderizarApp({ caminho: "/redefinir-senha" });

    expect(await screen.findByText(/Link incompleto/)).toBeInTheDocument();
  });
});
