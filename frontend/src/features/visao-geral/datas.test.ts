import { dataPorExtenso, saudacao, tempoRelativo } from "./datas";

const AGORA = new Date(2026, 10, 6, 14, 30);

describe("saudacao", () => {
  it.each([
    [new Date(2026, 10, 6, 5, 0), "Bom dia"],
    [new Date(2026, 10, 6, 11, 59), "Bom dia"],
    [new Date(2026, 10, 6, 12, 0), "Boa tarde"],
    [new Date(2026, 10, 6, 18, 0), "Boa noite"],
    [new Date(2026, 10, 6, 2, 0), "Boa noite"],
  ])("%s → %s", (data, esperado) => {
    expect(saudacao(data)).toBe(esperado);
  });
});

describe("dataPorExtenso", () => {
  it("formata como no protótipo", () => {
    expect(dataPorExtenso(AGORA)).toBe("sexta-feira, 06 de novembro");
  });
});

describe("tempoRelativo", () => {
  it.each([
    ["2026-11-06T14:29:40", "Agora"],
    ["2026-11-06T14:10:00", "Há 20 min"],
    ["2026-11-06T13:30:00", "Há 1 hora"],
    ["2026-11-06T09:00:00", "Há 5 horas"],
    ["2026-11-05T23:00:00", "Ontem"],
    ["2026-11-03T10:00:00", "Há 3 dias"],
    ["2026-10-20T10:00:00", "20/10/2026"],
  ])("%s → %s", (iso, esperado) => {
    expect(tempoRelativo(iso, AGORA)).toBe(esperado);
  });
});
