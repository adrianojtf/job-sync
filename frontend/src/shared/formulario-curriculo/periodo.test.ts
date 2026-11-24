import casos from "./periodo.casos.json";
import {
  chaveDeAno,
  chaveDePeriodo,
  lerPeriodo,
  ordenarPorChave,
  validarAno,
  validarPeriodo,
} from "./periodo";

type CasoDePeriodo = {
  texto: string;
  valido: boolean;
  inicio?: [number, number | null];
  fim?: [number, number | null] | null;
};
const periodos = casos.periodos as CasoDePeriodo[];

describe("lerPeriodo (tabela compartilhada com o backend)", () => {
  it.each(periodos.filter((caso) => caso.valido))("lê $texto", (caso) => {
    expect(lerPeriodo(caso.texto)).toEqual({ inicio: caso.inicio, fim: caso.fim });
  });

  it.each(periodos.filter((caso) => !caso.valido))("recusa $texto", (caso) => {
    expect(lerPeriodo(caso.texto)).toBeNull();
  });
});

describe("validarPeriodo", () => {
  it("devolve a mensagem com o exemplo do formato para um período inválido", () => {
    expect(validarPeriodo("ontem")).toBe("Use o formato Mar 2024 - Atual ou 2020 - 2022.");
  });

  it("explica quando o início é depois do fim", () => {
    expect(validarPeriodo("2024 - 2020")).toContain("O início não pode ser depois do fim");
  });

  it.each(["", "   ", "2020 - 2022", "Mar 2024 - Atual"])("aceita %j", (texto) => {
    expect(validarPeriodo(texto)).toBeUndefined();
  });
});

describe("validarAno (tabela compartilhada com o backend)", () => {
  it.each(casos.anos)("$texto", (caso) => {
    expect(validarAno(caso.texto) === undefined).toBe(caso.valido);
  });

  it("aceita o ano vazio", () => {
    expect(validarAno("")).toBeUndefined();
  });
});

describe("ordenarPorChave", () => {
  const ordenar = (textos: string[]) => ordenarPorChave(textos, chaveDePeriodo);

  it("põe o mais recente primeiro", () => {
    expect(ordenar(["2018 - 2020", "2022 - 2024", "2020 - 2022"])).toEqual([
      "2022 - 2024",
      "2020 - 2022",
      "2018 - 2020",
    ]);
  });

  it("período em andamento vem antes de todos, e entre eles vale o início mais recente", () => {
    expect(ordenar(["2024 - 2025", "2020 - Atual", "Mar 2026 - Atual"])).toEqual([
      "Mar 2026 - Atual",
      "2020 - Atual",
      "2024 - 2025",
    ]);
  });

  it("usa o mês para desempatar o mesmo ano", () => {
    expect(ordenar(["Jan 2022 - Jun 2022", "Nov 2022 - Dez 2022"])).toEqual([
      "Nov 2022 - Dez 2022",
      "Jan 2022 - Jun 2022",
    ]);
  });

  it("vazio fica no fim, mantendo a ordem relativa", () => {
    expect(ordenar(["", "2018 - 2020", "  ", "2022 - 2024"])).toEqual([
      "2022 - 2024",
      "2018 - 2020",
      "",
      "  ",
    ]);
  });

  it("empate mantém a ordem original", () => {
    const itens = [
      { id: "a", periodo: "2020 - 2022" },
      { id: "b", periodo: "2020 - 2022" },
    ];

    expect(ordenarPorChave(itens, (item) => chaveDePeriodo(item.periodo)).map((i) => i.id)).toEqual(
      ["a", "b"],
    );
  });

  it("não altera a lista original", () => {
    const original = ["2018 - 2020", "2022 - 2024"];

    ordenar(original);

    expect(original).toEqual(["2018 - 2020", "2022 - 2024"]);
  });

  it("ordena certificações pelo ano, com vazio no fim", () => {
    expect(ordenarPorChave(["2021", "", "2023", "2022"], chaveDeAno)).toEqual([
      "2023",
      "2022",
      "2021",
      "",
    ]);
  });
});
