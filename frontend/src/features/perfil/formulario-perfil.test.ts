import type { PerfilEstruturado } from "../../api/tipos";
import {
  formularioParaEntrada,
  perfilParaFormulario,
  type FormularioPerfil,
} from "./formulario-perfil";

const perfil: PerfilEstruturado = {
  perfil_identificador: "adriano",
  nome_completo: "Adriano Teixeira",
  email: "adriano@email.com",
  linkedin: "https://linkedin.com/in/adriano",
  resumo_profissional: "Backend Java.",
  experiencias: [{ empresa: "Neoway", cargo: "Dev", periodo: "2020-2024", descricao: "APIs" }],
  formacoes: [{ instituicao: "UFSC", curso: "Computação", periodo: "2015" }],
  certificacoes: [{ nome: "AWS SAA", instituicao: "AWS", ano: "2023" }],
  idiomas: [{ idioma: "Inglês", nivel: "AVANCADO" }],
  tecnologias: ["Java", "AWS"],
};

describe("perfilParaFormulario", () => {
  it("devolve um formulário vazio quando não há perfil", () => {
    const formulario = perfilParaFormulario(null);

    expect(formulario.nome_completo).toBe("");
    expect(formulario.experiencias).toEqual([]);
    expect(formulario.tecnologias).toBe("");
  });

  it("copia os dados do perfil e junta as tecnologias com vírgula", () => {
    const formulario = perfilParaFormulario(perfil);

    expect(formulario.nome_completo).toBe("Adriano Teixeira");
    expect(formulario.experiencias).toEqual(perfil.experiencias);
    expect(formulario.idiomas).toEqual([{ idioma: "Inglês", nivel: "AVANCADO" }]);
    expect(formulario.tecnologias).toBe("Java, AWS");
  });
});

describe("formularioParaEntrada", () => {
  it("monta a entrada da API com o identificador, textos aparados e tecnologias em lista", () => {
    const formulario: FormularioPerfil = {
      ...perfilParaFormulario(perfil),
      nome_completo: "  Adriano Teixeira ",
      experiencias: [{ empresa: " Neoway ", cargo: "Dev ", periodo: "2020", descricao: " APIs " }],
      tecnologias: " Java,  AWS ,, Kafka ,",
    };

    const entrada = formularioParaEntrada(formulario, "adriano");

    expect(entrada.perfil_identificador).toBe("adriano");
    expect(entrada.nome_completo).toBe("Adriano Teixeira");
    expect(entrada.experiencias).toEqual([
      { empresa: "Neoway", cargo: "Dev", periodo: "2020", descricao: "APIs" },
    ]);
    expect(entrada.tecnologias).toEqual(["Java", "AWS", "Kafka"]);
  });

  it("faz o caminho de ida e volta sem perder dados", () => {
    const entrada = formularioParaEntrada(perfilParaFormulario(perfil), "adriano");

    expect(entrada).toEqual(perfil);
  });
});
