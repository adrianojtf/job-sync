import type { PerfilEstruturado } from "../../api/tipos";
import {
  ehLegada,
  experienciaParaIA,
  formularioParaEntrada,
  temBlocos,
  textoDosBlocos,
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
    {
      empresa: "Neoway",
      cargo: "Dev",
      periodo: "2020-2024",
      descricao: "APIs",
      contexto: "",
      responsabilidades: [],
      conquistas: [],
      skills: [],
    },
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
    expect(formulario.experiencias).toEqual([
      {
        empresa: "Neoway",
        cargo: "Dev",
        periodo: "2020-2024",
        descricao: "APIs",
        contexto: "",
        responsabilidades: "",
        conquistas: [],
        skills: [],
      },
    ]);
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
          contexto: "",
          responsabilidades: "",
          conquistas: [],
          skills: [],
        },
      ],
      tecnologias: " Java,  AWS ,, Kafka ,",
    };

    const entrada = formularioParaEntrada(formulario, "adriano");

    expect(entrada.perfil_identificador).toBe("adriano");
    expect(entrada.nome_completo).toBe("Adriano Teixeira");
    expect(entrada.experiencias).toEqual([
      {
        empresa: "Neoway",
        cargo: "Dev",
        periodo: "2020",
        descricao: "APIs",
        contexto: "",
        responsabilidades: [],
        conquistas: [],
        skills: [],
      },
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
          contexto: "",
          responsabilidades: "",
          skills: [],
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

const BLOCOS = {
  empresa: "Starian",
  cargo: "Dev",
  periodo: "2024 - Atual",
  descricao: "",
  contexto: "  ERP financeiro.  ",
  responsabilidades: "Projetar telas\n\n  Testar entregas  \n",
  conquistas: [{ texto: "Atendi 1.000 usuários.", origem: "MANUAL" as const }],
  skills: ["Java", "SQL"],
};

describe("quatro blocos da experiência", () => {
  it("perfil com blocos abre com as responsabilidades em linhas e as skills em tags", () => {
    const comBlocos: PerfilEstruturado = {
      ...perfil,
      experiencias: [
        {
          empresa: "Starian",
          cargo: "Dev",
          periodo: "2024",
          descricao: "",
          contexto: "ERP.",
          responsabilidades: ["Projetar telas", "Testar entregas"],
          conquistas: [],
          skills: ["Java", "SQL"],
        },
      ],
    };

    const experiencia = perfilParaFormulario(comBlocos).experiencias[0]!;

    expect(experiencia.contexto).toBe("ERP.");
    expect(experiencia.responsabilidades).toBe("Projetar telas\nTestar entregas");
    expect(experiencia.skills).toEqual(["Java", "SQL"]);
  });

  it("na entrada apara o contexto e separa as responsabilidades em lista sem linhas em branco", () => {
    const formulario: FormularioPerfil = {
      ...perfilParaFormulario(perfil),
      experiencias: [BLOCOS],
    };

    const experiencia = formularioParaEntrada(formulario, "adriano").experiencias![0]!;

    expect(experiencia.contexto).toBe("ERP financeiro.");
    expect(experiencia.responsabilidades).toEqual(["Projetar telas", "Testar entregas"]);
    expect(experiencia.skills).toEqual(["Java", "SQL"]);
  });

  it("temBlocos e ehLegada distinguem o perfil antigo do estruturado", () => {
    expect(temBlocos(BLOCOS)).toBe(true);
    expect(ehLegada(BLOCOS)).toBe(false);
    const antiga = {
      ...BLOCOS,
      descricao: "APIs.",
      contexto: "",
      responsabilidades: "",
      conquistas: [],
      skills: [],
    };
    expect(temBlocos(antiga)).toBe(false);
    expect(ehLegada(antiga)).toBe(true);
    expect(ehLegada({ ...antiga, descricao: "  " })).toBe(false);
  });

  it("experienciaParaIA leva a descrição e os quatro blocos limpos", () => {
    expect(experienciaParaIA(BLOCOS)).toEqual({
      empresa: "Starian",
      cargo: "Dev",
      periodo: "2024 - Atual",
      descricao: "",
      contexto: "ERP financeiro.",
      responsabilidades: ["Projetar telas", "Testar entregas"],
      conquistas: ["Atendi 1.000 usuários."],
      skills: ["Java", "SQL"],
    });
  });

  it("textoDosBlocos junta os blocos um item por linha, como o backend", () => {
    expect(textoDosBlocos(BLOCOS)).toBe(
      "Projetar telas\nTestar entregas\nAtendi 1.000 usuários.\nERP financeiro.\nJava, SQL",
    );
  });
});
