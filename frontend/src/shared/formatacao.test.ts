import {
  dominioDaUrl,
  formatarData,
  formatarDataHora,
  paraSlug,
  primeiraLinha,
} from "./formatacao";

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

describe("dominioDaUrl", () => {
  it("devolve o domínio sem www", () => {
    expect(dominioDaUrl("https://www.linkedin.com/jobs/view/1")).toBe("linkedin.com");
  });

  it("devolve vazio para URL ausente ou inválida", () => {
    expect(dominioDaUrl(null)).toBe("");
    expect(dominioDaUrl("não é url")).toBe("");
  });
});

describe("formatarDataHora", () => {
  it("formata data e hora no padrão brasileiro", () => {
    expect(formatarDataHora("2026-11-06T15:30:00")).toBe("06/11/2026 15:30");
  });
});
