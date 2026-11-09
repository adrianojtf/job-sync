import {
  dominioDaUrl,
  formatarData,
  formatarDataHora,
  formatarTempoRelativo,
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

describe("formatarTempoRelativo", () => {
  const agora = new Date("2026-11-09T15:00:00");

  it.each([
    ["2026-11-09T08:00:00", "hoje"],
    ["2026-11-08T23:59:00", "há 1 dia"],
    ["2026-11-06T10:00:00", "há 3 dias"],
    ["2026-11-02T10:00:00", "há 1 semana"],
    ["2026-10-19T10:00:00", "há 3 semanas"],
    ["2026-10-05T10:00:00", "há 1 mês"],
    ["2026-05-09T10:00:00", "há 6 meses"],
    ["2025-11-09T10:00:00", "há 1 ano"],
    ["2023-11-09T10:00:00", "há 3 anos"],
  ])("formata %s como %s", (iso, esperado) => {
    expect(formatarTempoRelativo(iso, agora)).toBe(esperado);
  });

  it("trata datas futuras como hoje", () => {
    expect(formatarTempoRelativo("2026-11-12T10:00:00", agora)).toBe("hoje");
  });
});
