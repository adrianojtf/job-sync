import { QueryClient } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ApiClient } from "../../api/api-client";
import { ApiError } from "../../api/api-error";
import type { DadosVaga } from "../../api/tipos";
import { AppProviders } from "../../app/AppProviders";
import { usuarioDeTeste } from "../../test/usuario-de-teste";
import { CHAVE_QUERY_SESSAO } from "../sessao/sessao-context";
import { PreencherPeloTexto } from "./PreencherPeloTexto";

const DADOS: DadosVaga = { cargo: "Engenheiro", empresa: "Barte", descricao: "Texto da vaga" };

function montar(extrair: ApiClient["extrairDadosVaga"], texto: string, aoLer = vi.fn()) {
  const queryClient = new QueryClient();
  queryClient.setQueryData(CHAVE_QUERY_SESSAO, usuarioDeTeste("adriano"));
  render(
    <AppProviders
      apiClient={{ extrairDadosVaga: extrair } as unknown as ApiClient}
      queryClient={queryClient}
    >
      <PreencherPeloTexto texto={texto} aoLer={aoLer} campos={["cargo", "empresa"]} />
    </AppProviders>,
  );
  return aoLer;
}

describe("PreencherPeloTexto", () => {
  it("fica desabilitado enquanto não há texto", () => {
    montar(vi.fn(), "   ");

    expect(screen.getByRole("button", { name: "Preencher os campos pelo texto" })).toBeDisabled();
  });

  it("envia o texto, entrega o rascunho e informa o que foi identificado", async () => {
    const extrair = vi.fn().mockResolvedValue(DADOS);
    const aoLer = montar(extrair, "  Texto da vaga  ");

    await userEvent.click(screen.getByRole("button", { name: "Preencher os campos pelo texto" }));

    expect(
      await screen.findByText(
        "Dados identificados no texto: título, empresa e descrição. Confira antes de continuar.",
      ),
    ).toBeInTheDocument();
    expect(extrair).toHaveBeenCalledWith({ texto: "Texto da vaga" });
    expect(aoLer).toHaveBeenCalledWith(DADOS);
  });

  it("mostra a falha da API", async () => {
    const extrair = vi
      .fn()
      .mockRejectedValue(
        new ApiError(429, "Limite de leituras de vaga atingido", "Tente novamente mais tarde."),
      );
    montar(extrair, "Texto da vaga");

    await userEvent.click(screen.getByRole("button", { name: "Preencher os campos pelo texto" }));

    expect(await screen.findByText("Tente novamente mais tarde.")).toBeInTheDocument();
  });
});
