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
  experiencias: [
    { empresa: "Neoway", cargo: "Dev", periodo: "2020-2024", descricao: "APIs", conquistas: [] },
  ],
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
      experiencias: [
        {
          empresa: " Neoway ",
          cargo: "Dev ",
          periodo: "2020",
          descricao: " APIs ",
          conquistas: [],
        },
      ],
      tecnologias: " Java,  AWS ,, Kafka ,",
    };

    const entrada = formularioParaEntrada(formulario, "adriano");

    expect(entrada.perfil_identificador).toBe("adriano");
    expect(entrada.nome_completo).toBe("Adriano Teixeira");
    expect(entrada.experiencias).toEqual([
      { empresa: "Neoway", cargo: "Dev", periodo: "2020", descricao: "APIs", conquistas: [] },
    ]);
    expect(entrada.tecnologias).toEqual(["Java", "AWS", "Kafka"]);
  });

  it("faz o caminho de ida e volta sem perder dados", () => {
    const entrada = formularioParaEntrada(perfilParaFormulario(perfil), "adriano");

    expect(entrada).toEqual(perfil);
  });
});

describe("conquistas da experiência", () => {
  const conquistas = [
    { texto: "Reduzi o tempo de deploy.", origem: "MANUAL" as const },
    { texto: "Atuei com o cliente em um MVP.", origem: "RESPOSTA_PERGUNTA" as const },
  ];

  it("perfil salvo antes do banco de conquistas abre com a lista vazia", () => {
    const antigo: PerfilEstruturado = {
      ...perfil,
      experiencias: [{ empresa: "Neoway", cargo: "Dev", periodo: "2020", descricao: "APIs" }],
    };

    const formulario = perfilParaFormulario(antigo);

    expect(formulario.experiencias[0]?.conquistas).toEqual([]);
  });

  it("copia as conquistas com a origem para o formulário", () => {
    const comConquistas: PerfilEstruturado = {
      ...perfil,
      experiencias: [{ ...perfil.experiencias![0]!, conquistas }],
    };

    const formulario = perfilParaFormulario(comConquistas);

    expect(formulario.experiencias[0]?.conquistas).toEqual(conquistas);
  });

  it("na entrada apara o texto, mantém a origem e descarta conquistas em branco", () => {
    const formulario: FormularioPerfil = {
      ...perfilParaFormulario(perfil),
      experiencias: [
        {
          empresa: "Neoway",
          cargo: "Dev",
          periodo: "2020",
          descricao: "APIs",
          conquistas: [
            { texto: "  Reduzi o tempo de deploy.  ", origem: "MANUAL" },
            { texto: "   ", origem: "MANUAL" },
            { texto: "Atuei com o cliente em um MVP.", origem: "RESPOSTA_PERGUNTA" },
          ],
        },
      ],
    };

    const entrada = formularioParaEntrada(formulario, "adriano");

    expect(entrada.experiencias?.[0]?.conquistas).toEqual(conquistas);
  });
});
