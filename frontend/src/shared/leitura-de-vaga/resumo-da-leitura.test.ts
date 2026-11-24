import type { DadosVaga } from "../../api/tipos";
import { juntarEmPortugues, resumirLeitura } from "./resumo-da-leitura";

const BASE: DadosVaga = { descricao: "Descrição da vaga." };

describe("resumirLeitura", () => {
  it("separa o que foi preenchido do que não foi encontrado", () => {
    const resumo = resumirLeitura({ ...BASE, cargo: "Engenheiro", empresa: "Barte" });

    expect(resumo.preenchidos).toEqual(["título", "empresa", "descrição"]);
    expect(resumo.ausentes).toEqual(["local"]);
  });

  it("considera apenas os campos que a tela usa", () => {
    const resumo = resumirLeitura({ ...BASE, cargo: "Engenheiro" }, ["cargo", "empresa"]);

    expect(resumo.preenchidos).toEqual(["título", "descrição"]);
    expect(resumo.ausentes).toEqual(["empresa"]);
  });

  it("trata texto vazio ou nulo como não encontrado", () => {
    const resumo = resumirLeitura({ ...BASE, cargo: "", empresa: null, local: "Brasil" });

    expect(resumo.preenchidos).toEqual(["local", "descrição"]);
    expect(resumo.ausentes).toEqual(["título", "empresa"]);
  });

  it("a descrição sempre consta como preenchida", () => {
    expect(resumirLeitura(BASE).preenchidos).toEqual(["descrição"]);
  });
});

describe("juntarEmPortugues", () => {
  it.each([
    [[], ""],
    [["título"], "título"],
    [["título", "empresa"], "título e empresa"],
    [["título", "empresa", "local"], "título, empresa e local"],
  ])("junta %j como %j", (itens, esperado) => {
    expect(juntarEmPortugues(itens)).toBe(esperado);
  });
});
