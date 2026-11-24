import { QueryClient } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import type { ApiClient } from "../../api/api-client";
import { ApiError } from "../../api/api-error";
import type { DadosVaga } from "../../api/tipos";
import { AppProviders } from "../../app/AppProviders";
import { CHAVE_QUERY_SESSAO } from "../sessao/sessao-context";
import { usuarioDeTeste } from "../../test/usuario-de-teste";
import { CampoLinkVaga } from "./CampoLinkVaga";

const URL_VAGA = "https://www.linkedin.com/jobs/view/4484559483/";
const DADOS: DadosVaga = {
  cargo: "Engenheiro de Software",
  empresa: "Barte",
  local: null,
  descricao: "Descrição original da vaga.",
  url: URL_VAGA,
};

function Cenario({
  api,
  aoLer,
  aoEnviar,
  inicial = "",
}: {
  api: ApiClient;
  aoLer: (dados: DadosVaga) => void;
  aoEnviar?: () => void;
  inicial?: string;
}) {
  const [valor, setValor] = useState(inicial);
  const [queryClient] = useState(() => {
    const cliente = new QueryClient();
    cliente.setQueryData(CHAVE_QUERY_SESSAO, usuarioDeTeste("adriano"));
    return cliente;
  });
  return (
    <AppProviders apiClient={api} queryClient={queryClient}>
      <form
        onSubmit={(evento) => {
          evento.preventDefault();
          aoEnviar?.();
        }}
      >
        <CampoLinkVaga valor={valor} aoAlterar={setValor} aoLer={aoLer} />
      </form>
    </AppProviders>
  );
}

function apiCom(extrairDadosVaga: ApiClient["extrairDadosVaga"]) {
  return { extrairDadosVaga } as unknown as ApiClient;
}

describe("CampoLinkVaga", () => {
  it("começa com o botão de leitura desabilitado e a ajuda ligada ao campo", () => {
    render(<Cenario api={apiCom(vi.fn())} aoLer={vi.fn()} />);

    expect(screen.getByRole("button", { name: "Ler vaga" })).toBeDisabled();
    expect(screen.getByLabelText("Link da vaga")).toHaveAccessibleDescription(
      "Funciona com vagas públicas. Se o site bloquear, cole o texto da vaga.",
    );
  });

  it("lê o link, entrega o rascunho e informa o que foi preenchido", async () => {
    const extrair = vi.fn().mockResolvedValue(DADOS);
    const aoLer = vi.fn();
    render(<Cenario api={apiCom(extrair)} aoLer={aoLer} />);

    await userEvent.type(screen.getByLabelText("Link da vaga"), `  ${URL_VAGA}  `);
    await userEvent.click(screen.getByRole("button", { name: "Ler vaga" }));

    expect(
      await screen.findByText(
        "Dados lidos do link: título, empresa e descrição. Não encontramos: local. Confira antes de continuar.",
      ),
    ).toBeInTheDocument();
    expect(extrair).toHaveBeenCalledWith({ url: URL_VAGA });
    expect(aoLer).toHaveBeenCalledWith(DADOS);
  });

  it("Enter lê a vaga sem enviar o formulário", async () => {
    const extrair = vi.fn().mockResolvedValue(DADOS);
    const aoEnviar = vi.fn();
    render(<Cenario api={apiCom(extrair)} aoLer={vi.fn()} aoEnviar={aoEnviar} />);

    await userEvent.type(screen.getByLabelText("Link da vaga"), `${URL_VAGA}{Enter}`);

    await waitFor(() => expect(extrair).toHaveBeenCalledTimes(1));
    expect(aoEnviar).not.toHaveBeenCalled();
  });

  it("mostra o andamento e ignora o resultado quando a leitura é cancelada", async () => {
    let concluir: (dados: DadosVaga) => void = () => undefined;
    const extrair = vi
      .fn()
      .mockReturnValue(new Promise<DadosVaga>((resolve) => (concluir = resolve)));
    const aoLer = vi.fn();
    render(<Cenario api={apiCom(extrair)} aoLer={aoLer} inicial={URL_VAGA} />);

    await userEvent.click(screen.getByRole("button", { name: "Ler vaga" }));
    expect(await screen.findByText("Lendo a vaga…")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Cancelar leitura" }));
    concluir(DADOS);
    await new Promise((resolve) => setTimeout(resolve, 20));

    expect(screen.queryByText("Lendo a vaga…")).not.toBeInTheDocument();
    expect(screen.queryByText(/Dados lidos do link/)).not.toBeInTheDocument();
    expect(aoLer).not.toHaveBeenCalled();
  });

  it("não dispara uma segunda leitura enquanto a primeira está em andamento", async () => {
    const extrair = vi.fn().mockReturnValue(new Promise<DadosVaga>(() => undefined));
    render(<Cenario api={apiCom(extrair)} aoLer={vi.fn()} inicial={URL_VAGA} />);

    await userEvent.click(screen.getByRole("button", { name: "Ler vaga" }));
    await userEvent.click(screen.getByRole("button", { name: "Ler vaga" }));

    expect(extrair).toHaveBeenCalledTimes(1);
  });

  it("mostra o motivo da falha e não entrega rascunho", async () => {
    const detalhe =
      "O site não permitiu a leitura desta vaga. Cole o texto da vaga para continuar.";
    const extrair = vi
      .fn()
      .mockRejectedValue(new ApiError(502, "Leitura da vaga indisponível", detalhe));
    const aoLer = vi.fn();
    render(<Cenario api={apiCom(extrair)} aoLer={aoLer} inicial={URL_VAGA} />);

    await userEvent.click(screen.getByRole("button", { name: "Ler vaga" }));

    expect(await screen.findByText(detalhe)).toBeInTheDocument();
    expect(aoLer).not.toHaveBeenCalled();
  });

  it("limpa a falha anterior ao tentar de novo", async () => {
    const extrair = vi
      .fn()
      .mockRejectedValueOnce(new ApiError(502, "Leitura da vaga indisponível", "Falhou."))
      .mockResolvedValueOnce(DADOS);
    render(<Cenario api={apiCom(extrair)} aoLer={vi.fn()} inicial={URL_VAGA} />);

    await userEvent.click(screen.getByRole("button", { name: "Ler vaga" }));
    await screen.findByText("Falhou.");
    await userEvent.click(screen.getByRole("button", { name: "Ler vaga" }));

    expect(await screen.findByText(/Dados lidos do link/)).toBeInTheDocument();
    expect(screen.queryByText("Falhou.")).not.toBeInTheDocument();
  });

  it("repassa cada alteração do texto digitado", async () => {
    render(<Cenario api={apiCom(vi.fn())} aoLer={vi.fn()} />);

    await userEvent.type(screen.getByLabelText("Link da vaga"), "abc");

    expect(screen.getByLabelText("Link da vaga")).toHaveValue("abc");
    expect(screen.getByRole("button", { name: "Ler vaga" })).toBeEnabled();
  });
});
