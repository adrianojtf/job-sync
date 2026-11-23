import type { RascunhoCurriculoAdaptado } from "../../api/tipos";
import {
  conquistasParaLinhas,
  descricaoParaAvaliacao,
  experienciaAdaptadaParaAvaliacao,
  experienciaAdaptadaParaFormulario,
  formularioParaExperienciaAdaptada,
  formularioParaRascunho,
  linhasParaConquistas,
  rascunhoParaFormulario,
  tituloCompetencias,
} from "./formulario-revisao";

const rascunhoDoPerfil: RascunhoCurriculoAdaptado = {
  nome_completo: "Ana Souza",
  email: "ana@ex.com",
  linkedin: "https://linkedin.com/in/ana",
  secoes: [
    { tipo: "FORMACAO", titulo: "Formação acadêmica", conteudo: "ADS — Estácio" },
    { tipo: "PERFIL", titulo: "Profile", conteudo: "Engenheira backend." },
  ],
  competencias: [{ nome: "Linguagens", tags: ["Java"] }],
  titulo_competencias: "Tecnologias",
  experiencias: [
    {
      cargo: "Dev",
      empresa: "TechCorp",
      periodo: "2024",
      conquistas: ["APIs."],
      contexto: "Empresa de TI.",
    },
  ],
  titulo_experiencias: "Experience",
};

const rascunhoComTecnologiasEmTexto: RascunhoCurriculoAdaptado = {
  nome_completo: "Ana Souza",
  secoes: [
    { tipo: "PERFIL", titulo: "Perfil", conteudo: "Engenheira backend." },
    {
      tipo: "TECNOLOGIAS",
      titulo: "Technical Skills",
      conteudo: "Linguagens: Java, Go\nBancos de Dados: SQL",
    },
  ],
  experiencias: null,
};

const rascunhoDePdf: RascunhoCurriculoAdaptado = {
  nome_completo: "Ana Souza",
  secoes: [{ tipo: "EXPERIENCIAS", titulo: "Experiências", conteudo: "Dev — TechCorp" }],
  experiencias: null,
};

describe("rascunhoParaFormulario", () => {
  it("leva a seção PERFIL para o resumo e ordena as demais seções como no cadastro", () => {
    const formulario = rascunhoParaFormulario(rascunhoDoPerfil);

    expect(formulario.resumo_profissional).toBe("Engenheira backend.");
    expect(formulario.secoes.map((secao) => secao.tipo)).toEqual(["FORMACAO"]);
    expect(formulario.competencias).toEqual([{ nome: "Linguagens", tags: ["Java"] }]);
    expect(formulario.experiencias).toEqual([
      {
        cargo: "Dev",
        empresa: "TechCorp",
        periodo: "2024",
        conquistas: "APIs.",
        contexto: "Empresa de TI.",
      },
    ]);
  });

  it("converte a seção de tecnologias em texto em categorias e tags", () => {
    const formulario = rascunhoParaFormulario(rascunhoComTecnologiasEmTexto);

    expect(formulario.competencias).toEqual([
      { nome: "Linguagens", tags: ["Java", "Go"] },
      { nome: "Bancos de Dados", tags: ["SQL"] },
    ]);
    expect(formulario.secoes.map((secao) => secao.tipo)).toEqual([]);
  });

  it("fica sem categorias quando o rascunho não traz competências nem tecnologias", () => {
    expect(rascunhoParaFormulario(rascunhoDePdf).competencias).toEqual([]);
  });

  it("preenche campos ausentes com texto vazio quando a fonte é PDF", () => {
    const formulario = rascunhoParaFormulario(rascunhoDePdf);

    expect(formulario.email).toBe("");
    expect(formulario.linkedin).toBe("");
    expect(formulario.resumo_profissional).toBe("");
    expect(formulario.experiencias).toEqual([]);
    expect(formulario.secoes).toEqual([
      { tipo: "EXPERIENCIAS", titulo: "Experiências", conteudo: "Dev — TechCorp" },
    ]);
  });
});

describe("tituloCompetencias", () => {
  it("sem título no rascunho nem seção de tecnologias, usa Competências", () => {
    expect(tituloCompetencias(rascunhoDePdf)).toBe("Competências");
  });

  it("usa o título que o rascunho traz", () => {
    expect(tituloCompetencias(rascunhoDoPerfil)).toBe("Tecnologias");
  });
});

describe("formularioParaRascunho", () => {
  it("devolve o rascunho original quando nada foi editado", () => {
    const formulario = rascunhoParaFormulario(rascunhoDoPerfil);

    const rascunho = formularioParaRascunho(formulario, rascunhoDoPerfil);

    expect(rascunho).toEqual({
      ...rascunhoDoPerfil,
      secoes: [
        { tipo: "PERFIL", titulo: "Profile", conteudo: "Engenheira backend." },
        { tipo: "FORMACAO", titulo: "Formação acadêmica", conteudo: "ADS — Estácio" },
      ],
    });
  });

  it("envia as competências por categoria e nunca a seção de tecnologias em texto", () => {
    const formulario = rascunhoParaFormulario(rascunhoComTecnologiasEmTexto);

    const rascunho = formularioParaRascunho(formulario, rascunhoComTecnologiasEmTexto);

    expect(rascunho.secoes.map((secao) => secao.tipo)).toEqual(["PERFIL"]);
    expect(rascunho.competencias).toEqual([
      { nome: "Linguagens", tags: ["Java", "Go"] },
      { nome: "Bancos de Dados", tags: ["SQL"] },
    ]);
    expect(rascunho.titulo_competencias).toBe("Technical Skills");
  });

  it("leva as tags e os nomes de categoria editados e apara os nomes", () => {
    const formulario = rascunhoParaFormulario(rascunhoDoPerfil);
    formulario.competencias = [
      { nome: "  Linguagens ", tags: ["Java", "Go"] },
      { nome: "Ferramentas", tags: ["Git"] },
    ];

    const rascunho = formularioParaRascunho(formulario, rascunhoDoPerfil);

    expect(rascunho.competencias).toEqual([
      { nome: "Linguagens", tags: ["Java", "Go"] },
      { nome: "Ferramentas", tags: ["Git"] },
    ]);
  });

  it("descarta categorias sem nome ou sem tags, como o servidor faz ao salvar", () => {
    const formulario = rascunhoParaFormulario(rascunhoDoPerfil);
    formulario.competencias = [
      { nome: "Linguagens", tags: [] },
      { nome: "  ", tags: ["Git"] },
      { nome: "Ferramentas", tags: ["Docker"] },
    ];

    const rascunho = formularioParaRascunho(formulario, rascunhoDoPerfil);

    expect(rascunho.competencias).toEqual([{ nome: "Ferramentas", tags: ["Docker"] }]);
  });

  it("envia lista vazia quando todas as categorias foram excluídas", () => {
    const formulario = rascunhoParaFormulario(rascunhoDoPerfil);
    formulario.competencias = [];

    expect(formularioParaRascunho(formulario, rascunhoDoPerfil).competencias).toEqual([]);
  });

  it("leva as edições de todas as seções e apara os espaços", () => {
    const formulario = rascunhoParaFormulario(rascunhoDoPerfil);
    formulario.nome_completo = "  Ana Corrigida ";
    formulario.resumo_profissional = "Resumo novo.";
    formulario.experiencias[0]!.conquistas = " Texto editado. \n\n Outra conquista. ";
    formulario.experiencias[0]!.contexto = " Contexto editado. ";
    formulario.secoes[0]!.conteudo = "ADS — Estácio, 2024";

    const rascunho = formularioParaRascunho(formulario, rascunhoDoPerfil);

    expect(rascunho.nome_completo).toBe("Ana Corrigida");
    expect(rascunho.secoes[0]).toEqual({
      tipo: "PERFIL",
      titulo: "Profile",
      conteudo: "Resumo novo.",
    });
    expect(rascunho.secoes[1]?.conteudo).toBe("ADS — Estácio, 2024");
    expect(rascunho.experiencias?.[0]).toEqual({
      cargo: "Dev",
      empresa: "TechCorp",
      periodo: "2024",
      conquistas: ["Texto editado.", "Outra conquista."],
      contexto: "Contexto editado.",
    });
  });

  it("mantém experiências nulas quando a fonte é PDF e cria o resumo com título padrão", () => {
    const formulario = rascunhoParaFormulario(rascunhoDePdf);
    formulario.resumo_profissional = "Resumo escrito na revisão.";

    const rascunho = formularioParaRascunho(formulario, rascunhoDePdf);

    expect(rascunho.experiencias).toBeNull();
    expect(rascunho.secoes[0]).toEqual({
      tipo: "PERFIL",
      titulo: "Perfil",
      conteudo: "Resumo escrito na revisão.",
    });
  });
});

describe("conquistas e linhas", () => {
  it("uma conquista por linha, sem linhas em branco e com os espaços aparados", () => {
    expect(linhasParaConquistas("  Criei APIs. \n\n  \nReduzi custos.\n")).toEqual([
      "Criei APIs.",
      "Reduzi custos.",
    ]);
  });

  it("texto vazio resulta em nenhuma conquista", () => {
    expect(linhasParaConquistas("  \n ")).toEqual([]);
  });

  it("junta as conquistas em linhas", () => {
    expect(conquistasParaLinhas(["Criei APIs.", "Reduzi custos."])).toBe(
      "Criei APIs.\nReduzi custos.",
    );
  });
});

describe("experiência adaptada no formulário", () => {
  const experiencia = {
    cargo: "Dev",
    empresa: "TechCorp",
    periodo: "2024",
    conquistas: ["Criei APIs.", "Reduzi custos."],
    contexto: "Empresa de pagamentos.",
  };

  it("leva conquistas e contexto para campos de texto", () => {
    expect(experienciaAdaptadaParaFormulario(experiencia)).toEqual({
      cargo: "Dev",
      empresa: "TechCorp",
      periodo: "2024",
      conquistas: "Criei APIs.\nReduzi custos.",
      contexto: "Empresa de pagamentos.",
    });
  });

  it("preenche campos ausentes com texto vazio", () => {
    expect(experienciaAdaptadaParaFormulario({ cargo: "Dev", empresa: "TechCorp" })).toEqual({
      cargo: "Dev",
      empresa: "TechCorp",
      periodo: "",
      conquistas: "",
      contexto: "",
    });
  });

  it("devolve ao formato da API com os textos aparados e conquistas em lista", () => {
    const formulario = {
      cargo: " Dev ",
      empresa: "TechCorp ",
      periodo: " 2024",
      conquistas: " Criei APIs. \n\nReduzi custos.",
      contexto: " Empresa de pagamentos. ",
    };

    expect(formularioParaExperienciaAdaptada(formulario)).toEqual(experiencia);
  });

  it("ida e volta preserva a experiência", () => {
    expect(
      formularioParaExperienciaAdaptada(experienciaAdaptadaParaFormulario(experiencia)),
    ).toEqual(experiencia);
  });
});

describe("texto para avaliação", () => {
  const formulario = {
    cargo: "Software Engineer",
    empresa: "SIPPulse",
    periodo: "2022 - Atual",
    conquistas: "Developed a VoIP billing system.\nAccelerated processing by 95%.",
    contexto: "Worked on the communications platform.",
  };

  it("compõe bullets e contexto, sem cabeçalho nem rótulo, como o backend", () => {
    expect(descricaoParaAvaliacao(formulario)).toBe(
      "- Developed a VoIP billing system.\n- Accelerated processing by 95%.\nWorked on the communications platform.",
    );
  });

  it("sem contexto traz só as conquistas", () => {
    expect(descricaoParaAvaliacao({ ...formulario, contexto: "  " })).toBe(
      "- Developed a VoIP billing system.\n- Accelerated processing by 95%.",
    );
  });

  it("ignora linhas em branco nas conquistas", () => {
    expect(
      descricaoParaAvaliacao({ ...formulario, conquistas: "A.\n\n  \nB.", contexto: "" }),
    ).toBe("- A.\n- B.");
  });

  it("sem conquistas e sem contexto devolve texto vazio", () => {
    expect(descricaoParaAvaliacao({ ...formulario, conquistas: "", contexto: "" })).toBe("");
  });

  it("entrega a experiência no formato do modal de avaliação", () => {
    expect(experienciaAdaptadaParaAvaliacao(formulario)).toEqual({
      empresa: "SIPPulse",
      cargo: "Software Engineer",
      periodo: "2022 - Atual",
      descricao:
        "- Developed a VoIP billing system.\n- Accelerated processing by 95%.\nWorked on the communications platform.",
    });
  });
});
