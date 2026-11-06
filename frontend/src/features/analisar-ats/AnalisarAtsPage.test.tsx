import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { servirDadosBase, VAGA_SALVA } from "../../test/fixtures";
import { API_TESTE, renderizarApp } from "../../test/renderizar-app";
import { servidorApi } from "../../test/servidor-api";

function servirAts() {
  const corpos: Record<string, unknown>[] = [];
  servidorApi.use(
    http.post(`${API_TESTE}/v1/curriculos/:id/analises-ats`, async ({ request }) => {
      corpos.push((await request.json()) as Record<string, unknown>);
      return HttpResponse.json({
        nome_completo: "Adriano",
        nota: 54,
        requisitos_faltantes: [{ nome: "AWS", categoria: "FERRAMENTA", tipo: "EXPLICITO" }],
        sugestoes: [],
      });
    }),
  );
  return corpos;
}

describe("AnalisarAtsPage", () => {
  it("analisa uma descrição colada com o perfil estruturado", async () => {
    servirDadosBase();
    const corpos = servirAts();
    renderizarApp({ caminho: "/analisar-ats", perfil: "adriano" });

    await userEvent.type(await screen.findByLabelText("Descrição da vaga"), "Vaga com AWS.");
    await userEvent.click(screen.getByRole("button", { name: "Analisar ATS" }));

    const ats = await screen.findByRole("region", { name: "Aderência ATS" });
    expect(await within(ats).findByText("54")).toBeInTheDocument();
    expect(within(ats).getByText("AWS")).toBeInTheDocument();
    expect(within(ats).getByText("Nenhuma sugestão adicional.")).toBeInTheDocument();
    expect(corpos).toEqual([{ descricao_vaga: "Vaga com AWS.", perfil_identificador: "adriano" }]);
  });

  it("usa a descrição de uma vaga salva", async () => {
    servirDadosBase();
    const corpos = servirAts();
    renderizarApp({ caminho: "/analisar-ats", perfil: "adriano" });

    await userEvent.click(await screen.findByLabelText("Usar uma vaga salva"));
    await userEvent.selectOptions(await screen.findByLabelText("Vaga salva"), VAGA_SALVA.id);
    await userEvent.click(screen.getByRole("button", { name: "Analisar ATS" }));

    await screen.findByRole("region", { name: "Aderência ATS" });
    expect(corpos[0]?.descricao_vaga).toBe(VAGA_SALVA.texto_descricao);
  });

  it("exige a descrição da vaga", async () => {
    servirDadosBase();
    const corpos = servirAts();
    renderizarApp({ caminho: "/analisar-ats", perfil: "adriano" });

    await userEvent.click(await screen.findByRole("button", { name: "Analisar ATS" }));

    expect(screen.getByLabelText("Descrição da vaga")).toHaveAccessibleDescription(
      "Cole a descrição da vaga.",
    );
    expect(corpos).toHaveLength(0);
  });

  it("aceita a descrição pré-preenchida pela navegação", async () => {
    servirDadosBase();
    const { router } = renderizarApp({ caminho: "/", perfil: "adriano" });
    await screen.findByRole("heading", { level: 1 });

    await router.navigate("/analisar-ats", { state: { descricao: "Vaga vinda de outra tela." } });

    expect(await screen.findByLabelText("Descrição da vaga")).toHaveValue(
      "Vaga vinda de outra tela.",
    );
  });
});
