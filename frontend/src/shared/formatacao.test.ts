import { formatarData, paraSlug, primeiraLinha } from "./formatacao";

describe("formatarData", () => {
  it("formata datas ISO da API no padrão brasileiro", () => {
    expect(formatarData("2026-11-06T10:30:00")).toBe("06/11/2026");
  });
});

describe("primeiraLinha", () => {
  it("devolve a primeira linha não vazia", () => {
    expect(primeiraLinha("\n  Senior Java Backend  \nRequisitos")).toBe("Senior Java Backend");
  });

  it("encurta textos longos com reticências", () => {
    expect(primeiraLinha("a".repeat(100), 10)).toBe("aaaaaaaaa…");
  });
});

describe("paraSlug", () => {
  it("gera um trecho de nome de arquivo sem acentos e espaços", () => {
    expect(paraSlug("Sênior Java / Olist")).toBe("senior-java-olist");
  });
});
