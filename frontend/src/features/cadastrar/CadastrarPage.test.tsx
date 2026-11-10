import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

async function preencher(email: string, senha: string, confirmacao: string) {
  await userEvent.type(await screen.findByLabelText("E-mail"), email);
  await userEvent.type(screen.getByLabelText("Senha"), senha);
  await userEvent.type(screen.getByLabelText("Confirmar senha"), confirmacao);
}

describe("CadastrarPage", () => {
  it("exige e-mail e senha", async () => {
    renderizarApp({ caminho: "/cadastrar" });

    await userEvent.click(await screen.findByRole("button", { name: "Criar conta" }));

    expect(screen.getByLabelText("Confirmar senha")).toHaveAccessibleDescription(
      /Informe o e-mail e a senha\./,
    );
  });

  it("recusa senhas diferentes sem chamar a API", async () => {
    renderizarApp({ caminho: "/cadastrar" });

    await preencher("ana@exemplo.com", "senha-longa-123", "senha-longa-999");
    await userEvent.click(screen.getByRole("button", { name: "Criar conta" }));

    expect(await screen.findByText("As senhas não conferem.")).toBeInTheDocument();
  });

  it("cadastra e avisa que é preciso confirmar o e-mail", async () => {
    let corpo: unknown;
    servidorApi.use(
      http.post(`${API_TESTE}/v1/usuarios`, async ({ request }) => {
        corpo = await request.json();
        return HttpResponse.json({ mensagem: "ok" }, { status: 202 });
      }),
    );
    renderizarApp({ caminho: "/cadastrar" });

    await preencher(" ana@exemplo.com ", "senha-longa-123", "senha-longa-123");
    await userEvent.click(screen.getByRole("button", { name: "Criar conta" }));

    expect(
      await screen.findByRole("heading", { name: "Verifique seu e-mail" }),
    ).toBeInTheDocument();
    expect(screen.getByText(/ana@exemplo\.com/)).toBeInTheDocument();
    expect(corpo).toEqual({ email: "ana@exemplo.com", senha: "senha-longa-123" });
  });

  it("mostra o motivo quando a senha não atende à política", async () => {
    servidorApi.use(
      http.post(`${API_TESTE}/v1/usuarios`, () =>
        HttpResponse.json(
          {
            type: "t",
            title: "Requisição inválida",
            status: 422,
            detail: "A senha deve ter entre 10 e 128 caracteres.",
            instance: "i",
          },
          { status: 422 },
        ),
      ),
    );
    renderizarApp({ caminho: "/cadastrar" });

    await preencher("ana@exemplo.com", "curta", "curta");
    await userEvent.click(screen.getByRole("button", { name: "Criar conta" }));

    expect(
      await screen.findByText("A senha deve ter entre 10 e 128 caracteres."),
    ).toBeInTheDocument();
  });

  it("mostra mensagem genérica quando a API fica indisponível", async () => {
    servidorApi.use(http.post(`${API_TESTE}/v1/usuarios`, () => HttpResponse.error()));
    renderizarApp({ caminho: "/cadastrar" });

    await preencher("ana@exemplo.com", "senha-longa-123", "senha-longa-123");
    await userEvent.click(screen.getByRole("button", { name: "Criar conta" }));

    expect(await screen.findByText(/Não foi possível criar a conta agora/)).toBeInTheDocument();
  });

  it("com sessão ativa, volta para a Visão geral", async () => {
    renderizarApp({ caminho: "/cadastrar", perfil: "adriano" });

    expect(
      await screen.findByRole("heading", { level: 1, name: /^(Bom dia|Boa tarde|Boa noite), / }),
    ).toBeInTheDocument();
  });
});
