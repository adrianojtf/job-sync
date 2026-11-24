import { act, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { servirDadosBase } from "../test/fixtures";
import { API_TESTE, renderizarApp } from "../test/renderizar-app";
import { servidorApi } from "../test/servidor-api";

const sair = (router: ReturnType<typeof renderizarApp>["router"], para = "/curriculos") =>
  act(async () => {
    void router.navigate(para);
  });
const dialogo = () => screen.queryByRole("dialog", { name: "Sair sem salvar?" });

describe("Aviso ao sair com alterações não enviadas", () => {
  beforeEach(() => servirDadosBase());

  describe("Analisar ATS", () => {
    it("sem texto digitado navega direto", async () => {
      const { router } = renderizarApp({ caminho: "/analisar-ats", perfil: "adriano" });
      await screen.findByLabelText("Descrição da vaga");

      await sair(router);

      expect(dialogo()).not.toBeInTheDocument();
      await waitFor(() => expect(router.state.location.pathname).toBe("/curriculos"));
    });

    it("com texto digitado pergunta, e cancelar mantém a tela", async () => {
      const { router } = renderizarApp({ caminho: "/analisar-ats", perfil: "adriano" });
      await userEvent.type(await screen.findByLabelText("Descrição da vaga"), "Vaga com AWS.");

      await sair(router);

      expect(await screen.findByRole("dialog", { name: "Sair sem salvar?" })).toBeInTheDocument();
      await userEvent.click(screen.getByRole("button", { name: "Cancelar" }));
      expect(router.state.location.pathname).toBe("/analisar-ats");
      expect(screen.getByLabelText("Descrição da vaga")).toHaveValue("Vaga com AWS.");
    });

    it("com texto digitado, confirmar sai da tela", async () => {
      const { router } = renderizarApp({ caminho: "/analisar-ats", perfil: "adriano" });
      await userEvent.type(await screen.findByLabelText("Descrição da vaga"), "Vaga com AWS.");
      await sair(router);

      await userEvent.click(await screen.findByRole("button", { name: "Sair sem salvar" }));

      await waitFor(() => expect(router.state.location.pathname).toBe("/curriculos"));
    });

    it("depois de enviar a análise com sucesso, não pergunta mais", async () => {
      servidorApi.use(
        http.post(`${API_TESTE}/v1/curriculos/:id/analises-ats`, () =>
          HttpResponse.json({
            nome_completo: "Adriano",
            nota: 54,
            requisitos_faltantes: [],
            sugestoes: [],
          }),
        ),
      );
      const { router } = renderizarApp({ caminho: "/analisar-ats", perfil: "adriano" });
      await userEvent.type(await screen.findByLabelText("Descrição da vaga"), "Vaga com AWS.");
      await userEvent.click(screen.getByRole("button", { name: "Analisar ATS" }));
      await screen.findByRole("region", { name: "Aderência ATS" });

      await sair(router);

      expect(dialogo()).not.toBeInTheDocument();
      await waitFor(() => expect(router.state.location.pathname).toBe("/curriculos"));
    });
  });

  describe("Descobrir vagas", () => {
    it("com o termo digitado e não buscado, pergunta antes de sair", async () => {
      const { router } = renderizarApp({ caminho: "/descobrir-vagas", perfil: "adriano" });
      await userEvent.type(await screen.findByLabelText("Termo de busca"), "backend");

      await sair(router);

      expect(await screen.findByRole("dialog", { name: "Sair sem salvar?" })).toBeInTheDocument();
    });

    it("sem alteração navega direto", async () => {
      const { router } = renderizarApp({ caminho: "/descobrir-vagas", perfil: "adriano" });
      await screen.findByLabelText("Termo de busca");

      await sair(router);

      expect(dialogo()).not.toBeInTheDocument();
    });
  });

  describe("Ajustar vaga", () => {
    it("com a descrição digitada e não enviada, pergunta antes de sair", async () => {
      const { router } = renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
      await userEvent.type(await screen.findByLabelText("Descrição da vaga"), "Vaga Java sênior.");

      await sair(router);

      expect(await screen.findByRole("dialog", { name: "Sair sem salvar?" })).toBeInTheDocument();
    });

    it("sem alteração navega direto", async () => {
      const { router } = renderizarApp({ caminho: "/ajustar-vaga", perfil: "adriano" });
      await screen.findByLabelText("Descrição da vaga");

      await sair(router);

      expect(dialogo()).not.toBeInTheDocument();
    });
  });

  describe("Fechar ou recarregar a aba", () => {
    it("com texto não enviado, aciona o aviso do navegador", async () => {
      renderizarApp({ caminho: "/analisar-ats", perfil: "adriano" });
      await userEvent.type(await screen.findByLabelText("Descrição da vaga"), "Vaga.");
      const evento = new Event("beforeunload", { cancelable: true });

      act(() => {
        window.dispatchEvent(evento);
      });

      expect(evento.defaultPrevented).toBe(true);
    });
  });
});
