import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpApiClient } from "../../api/http-api-client";
import type { RascunhoCurriculoAdaptado } from "../../api/tipos";
import { AppProviders } from "../../app/AppProviders";
import { API_TESTE } from "../../test/servidor-api";
import { RevisaoCurriculoAdaptado } from "./RevisaoCurriculoAdaptado";

const rascunhoDoPerfil: RascunhoCurriculoAdaptado = {
  nome_completo: "Ana Souza",
  email: "ana@ex.com",
  linkedin: "",
  secoes: [
    { tipo: "PERFIL", titulo: "Perfil", conteudo: "Resumo da IA." },
    { tipo: "TECNOLOGIAS", titulo: "Tecnologias", conteudo: "Linguagens: Java" },
    { tipo: "FORMACAO", titulo: "Formação acadêmica", conteudo: "ADS — Estácio" },
  ],
  experiencias: [{ cargo: "Dev", empresa: "TechCorp", periodo: "2024", descricao: "Texto da IA." }],
  titulo_experiencias: "Experiências",
};

const rascunhoDePdf: RascunhoCurriculoAdaptado = {
  nome_completo: "Ana Souza",
  secoes: [{ tipo: "EXPERIENCIAS", titulo: "Experiências", conteudo: "Dev — TechCorp" }],
  experiencias: null,
};

function renderizar(props: Partial<Parameters<typeof RevisaoCurriculoAdaptado>[0]> = {}) {
  const aoConfirmar = vi.fn();
  const aoVoltar = vi.fn();
  const resultado = render(
    <AppProviders apiClient={new HttpApiClient({ baseUrl: API_TESTE })}>
      <RevisaoCurriculoAdaptado
        rascunho={rascunhoDoPerfil}
        gerando={false}
        aoConfirmar={aoConfirmar}
        aoVoltar={aoVoltar}
        {...props}
      />
    </AppProviders>,
  );
  return { aoConfirmar, aoVoltar, ...resultado };
}

describe("RevisaoCurriculoAdaptado", () => {
  it("mostra todas as seções do rascunho, editáveis ao mesmo tempo", () => {
    renderizar();

    expect(screen.getByRole("heading", { name: "Revise o currículo adaptado" })).toHaveFocus();
    expect(screen.getByLabelText("Nome completo")).toHaveValue("Ana Souza");
    expect(screen.getByLabelText("Resumo profissional")).toHaveValue("Resumo da IA.");
    expect(screen.getByLabelText("Descrição")).toHaveValue("Texto da IA.");
    expect(screen.getByLabelText("Tecnologias")).toHaveValue("Linguagens: Java");
    expect(screen.getByLabelText("Formação")).toHaveValue("ADS — Estácio");
    expect(screen.queryByRole("heading", { name: "Certificações" })).not.toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: /confirmar e gerar pdf/i })).toHaveLength(1);
  });

  it("confirma uma única vez com o estado editado de todas as seções", async () => {
    const usuario = userEvent.setup();
    const { aoConfirmar } = renderizar();

    await usuario.clear(screen.getByLabelText("Resumo profissional"));
    await usuario.type(screen.getByLabelText("Resumo profissional"), "Resumo revisado.");
    await usuario.clear(screen.getByLabelText("Descrição"));
    await usuario.type(screen.getByLabelText("Descrição"), "Texto revisado.");
    await usuario.clear(screen.getByLabelText("Formação"));
    expect(screen.getByText("Alterações não confirmadas")).toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Confirmar e gerar PDF" }));

    expect(aoConfirmar).toHaveBeenCalledTimes(1);
    expect(aoConfirmar).toHaveBeenCalledWith({
      ...rascunhoDoPerfil,
      secoes: [
        { tipo: "PERFIL", titulo: "Perfil", conteudo: "Resumo revisado." },
        { tipo: "TECNOLOGIAS", titulo: "Tecnologias", conteudo: "Linguagens: Java" },
        { tipo: "FORMACAO", titulo: "Formação acadêmica", conteudo: "" },
      ],
      experiencias: [
        { cargo: "Dev", empresa: "TechCorp", periodo: "2024", descricao: "Texto revisado." },
      ],
    });
  });

  it("não confirma com erros de validação e indica o campo", async () => {
    const usuario = userEvent.setup();
    const { aoConfirmar } = renderizar();

    await usuario.clear(screen.getByLabelText("Nome completo"));
    await usuario.clear(screen.getByLabelText("Cargo"));
    await usuario.click(screen.getByRole("button", { name: "Confirmar e gerar PDF" }));

    expect(aoConfirmar).not.toHaveBeenCalled();
    expect(screen.getByText("Informe o nome completo.")).toBeInTheDocument();
    expect(screen.getByText("Informe o cargo.")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome completo")).toHaveFocus();
  });

  it("permite adicionar e remover experiências no rascunho", async () => {
    const usuario = userEvent.setup();
    const { aoConfirmar } = renderizar();

    await usuario.click(screen.getByRole("button", { name: "Remover experiência 1" }));
    await usuario.click(screen.getByRole("button", { name: "Adicionar experiência" }));
    await usuario.type(screen.getByLabelText("Empresa"), "Starian");
    await usuario.type(screen.getByLabelText("Cargo"), "Engenheira");
    await usuario.click(screen.getByRole("button", { name: "Confirmar e gerar PDF" }));

    expect(aoConfirmar.mock.calls[0]?.[0].experiencias).toEqual([
      { cargo: "Engenheira", empresa: "Starian", periodo: "", descricao: "" },
    ]);
  });

  it("mostra as experiências como texto quando a fonte é PDF", () => {
    renderizar({ rascunho: rascunhoDePdf });

    expect(screen.getByLabelText("Experiências")).toHaveValue("Dev — TechCorp");
    expect(screen.queryByRole("button", { name: "Adicionar experiência" })).not.toBeInTheDocument();
  });

  it("não exige e-mail, que pode faltar em um currículo vindo de PDF", async () => {
    const usuario = userEvent.setup();
    const { aoConfirmar } = renderizar({ rascunho: rascunhoDePdf });

    await usuario.click(screen.getByRole("button", { name: "Confirmar e gerar PDF" }));

    expect(aoConfirmar).toHaveBeenCalledTimes(1);
  });

  it("volta direto para a vaga quando não há alterações", async () => {
    const usuario = userEvent.setup();
    const { aoVoltar } = renderizar();

    await usuario.click(screen.getByRole("button", { name: "Voltar para a vaga" }));

    expect(aoVoltar).toHaveBeenCalledTimes(1);
  });

  it("pede confirmação antes de descartar alterações ao voltar", async () => {
    const usuario = userEvent.setup();
    const { aoVoltar } = renderizar();

    await usuario.type(screen.getByLabelText("Resumo profissional"), " Editado.");
    await usuario.click(screen.getByRole("button", { name: "Voltar para a vaga" }));
    const dialogo = screen.getByRole("dialog", { name: "Descartar a revisão?" });
    await usuario.click(within(dialogo).getByRole("button", { name: "Cancelar" }));

    expect(aoVoltar).not.toHaveBeenCalled();
    expect(screen.getByLabelText("Resumo profissional")).toHaveValue("Resumo da IA. Editado.");

    await usuario.click(screen.getByRole("button", { name: "Voltar para a vaga" }));
    await usuario.click(screen.getByRole("button", { name: "Descartar alterações" }));

    expect(aoVoltar).toHaveBeenCalledTimes(1);
  });

  it("preserva as edições quando a geração do PDF falha", async () => {
    const usuario = userEvent.setup();
    const { rerender, aoConfirmar, aoVoltar } = renderizar();

    await usuario.type(screen.getByLabelText("Resumo profissional"), " Editado.");
    rerender(
      <AppProviders apiClient={new HttpApiClient({ baseUrl: API_TESTE })}>
        <RevisaoCurriculoAdaptado
          rascunho={rascunhoDoPerfil}
          gerando={false}
          erro="Serviço indisponível."
          aoConfirmar={aoConfirmar}
          aoVoltar={aoVoltar}
        />
      </AppProviders>,
    );

    expect(screen.getByText(/Serviço indisponível\./)).toHaveTextContent(
      "Não foi possível gerar o PDF: Serviço indisponível.",
    );
    expect(screen.getByLabelText("Resumo profissional")).toHaveValue("Resumo da IA. Editado.");
  });
});
