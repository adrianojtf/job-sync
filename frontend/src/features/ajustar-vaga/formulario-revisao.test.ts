import type { RascunhoCurriculoAdaptado } from "../../api/tipos";
import { formularioParaRascunho, rascunhoParaFormulario } from "./formulario-revisao";

const rascunhoDoPerfil: RascunhoCurriculoAdaptado = {
  nome_completo: "Ana Souza",
  email: "ana@ex.com",
  linkedin: "https://linkedin.com/in/ana",
  secoes: [
    { tipo: "FORMACAO", titulo: "Formação acadêmica", conteudo: "ADS — Estácio" },
    { tipo: "PERFIL", titulo: "Profile", conteudo: "Engenheira backend." },
    { tipo: "TECNOLOGIAS", titulo: "Tecnologias", conteudo: "Linguagens: Java" },
  ],
  experiencias: [{ cargo: "Dev", empresa: "TechCorp", periodo: "2024", descricao: "APIs." }],
  titulo_experiencias: "Experience",
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
    expect(formulario.secoes.map((secao) => secao.tipo)).toEqual(["TECNOLOGIAS", "FORMACAO"]);
    expect(formulario.experiencias).toEqual([
      { cargo: "Dev", empresa: "TechCorp", periodo: "2024", descricao: "APIs." },
    ]);
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

describe("formularioParaRascunho", () => {
  it("devolve o rascunho original quando nada foi editado", () => {
    const formulario = rascunhoParaFormulario(rascunhoDoPerfil);

    const rascunho = formularioParaRascunho(formulario, rascunhoDoPerfil);

    expect(rascunho).toEqual({
      ...rascunhoDoPerfil,
      secoes: [
        { tipo: "PERFIL", titulo: "Profile", conteudo: "Engenheira backend." },
        { tipo: "TECNOLOGIAS", titulo: "Tecnologias", conteudo: "Linguagens: Java" },
        { tipo: "FORMACAO", titulo: "Formação acadêmica", conteudo: "ADS — Estácio" },
      ],
    });
  });

  it("leva as edições de todas as seções e apara os espaços", () => {
    const formulario = rascunhoParaFormulario(rascunhoDoPerfil);
    formulario.nome_completo = "  Ana Corrigida ";
    formulario.resumo_profissional = "Resumo novo.";
    formulario.experiencias[0]!.descricao = " Texto editado. ";
    formulario.secoes[0]!.conteudo = "Linguagens: Java, Go";

    const rascunho = formularioParaRascunho(formulario, rascunhoDoPerfil);

    expect(rascunho.nome_completo).toBe("Ana Corrigida");
    expect(rascunho.secoes[0]).toEqual({
      tipo: "PERFIL",
      titulo: "Profile",
      conteudo: "Resumo novo.",
    });
    expect(rascunho.secoes[1]?.conteudo).toBe("Linguagens: Java, Go");
    expect(rascunho.experiencias?.[0]?.descricao).toBe("Texto editado.");
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
