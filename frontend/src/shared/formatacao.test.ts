import { formatarData } from "./formatacao";

describe("formatarData", () => {
  it("formata datas ISO da API no padrão brasileiro", () => {
    expect(formatarData("2026-11-06T10:30:00")).toBe("06/11/2026");
  });
});
