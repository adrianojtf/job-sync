import type { Candidatura, CandidaturasPorStatus } from "../../api/tipos";
import { aplicarMovimento, calcularDestino } from "./movimento";

const cartao = (id: string, status: string, posicao: number): Candidatura => ({
  id,
  perfil_identificador: "adriano",
  vaga_id: `vaga-${id}`,
  curriculo_salvo_id: "c1",
  empresa: `Empresa ${id}`,
  cargo: `Cargo ${id}`,
  status,
  data_aplicacao: "2026-11-02T09:00:00",
  historico_status: [],
  posicao,
});

const quadro = (): CandidaturasPorStatus => ({
  por_status: {
    APLICADO: [cartao("a", "APLICADO", 0), cartao("b", "APLICADO", 1), cartao("c", "APLICADO", 2)],
    ENTREVISTA: [cartao("x", "ENTREVISTA", 0), cartao("y", "ENTREVISTA", 1)],
    OFERTA: [],
    REJEITADO: [],
  },
  total: 5,
});

const ids = (q: CandidaturasPorStatus, status: string) =>
  (q.por_status?.[status] ?? []).map((c) => c.id);

describe("calcularDestino", () => {
  it("move sobre um cartão de outra coluna para a posição desse cartão", () => {
    expect(calcularDestino(quadro(), "a", "y")).toEqual({ status: "ENTREVISTA", posicao: 1 });
  });

  it("reordena na mesma coluna para a posição do cartão alvo", () => {
    expect(calcularDestino(quadro(), "a", "c")).toEqual({ status: "APLICADO", posicao: 2 });
    expect(calcularDestino(quadro(), "c", "a")).toEqual({ status: "APLICADO", posicao: 0 });
  });

  it("soltar sobre uma coluna vazia coloca o cartão na posição zero", () => {
    expect(calcularDestino(quadro(), "a", "coluna:OFERTA")).toEqual({
      status: "OFERTA",
      posicao: 0,
    });
  });

  it("soltar sobre outra coluna com cartões coloca o cartão no fim", () => {
    expect(calcularDestino(quadro(), "a", "coluna:ENTREVISTA")).toEqual({
      status: "ENTREVISTA",
      posicao: 2,
    });
  });

  it("soltar sobre a própria coluna move o cartão para o fim dela", () => {
    expect(calcularDestino(quadro(), "a", "coluna:APLICADO")).toEqual({
      status: "APLICADO",
      posicao: 2,
    });
  });

  it("devolve null ao soltar sobre o próprio cartão", () => {
    expect(calcularDestino(quadro(), "b", "b")).toBeNull();
  });

  it("devolve null quando o cartão já está na posição de destino", () => {
    expect(calcularDestino(quadro(), "c", "coluna:APLICADO")).toBeNull();
  });

  it("devolve null para ids desconhecidos", () => {
    expect(calcularDestino(quadro(), "nao-existe", "a")).toBeNull();
    expect(calcularDestino(quadro(), "a", "nao-existe")).toBeNull();
    expect(calcularDestino(quadro(), "a", "coluna:INEXISTENTE")).toBeNull();
  });
});

describe("aplicarMovimento", () => {
  it("move para outra coluna na posição informada e renumera as duas colunas", () => {
    const novo = aplicarMovimento(quadro(), "b", { status: "ENTREVISTA", posicao: 1 });

    expect(ids(novo, "APLICADO")).toEqual(["a", "c"]);
    expect(ids(novo, "ENTREVISTA")).toEqual(["x", "b", "y"]);
    expect(novo.por_status!.APLICADO!.map((c) => c.posicao)).toEqual([0, 1]);
    expect(novo.por_status!.ENTREVISTA!.map((c) => c.posicao)).toEqual([0, 1, 2]);
  });

  it("atualiza o status do cartão movido", () => {
    const novo = aplicarMovimento(quadro(), "a", { status: "OFERTA", posicao: 0 });

    expect(novo.por_status!.OFERTA![0]).toMatchObject({ id: "a", status: "OFERTA", posicao: 0 });
  });

  it("reordena dentro da mesma coluna", () => {
    const novo = aplicarMovimento(quadro(), "a", { status: "APLICADO", posicao: 2 });

    expect(ids(novo, "APLICADO")).toEqual(["b", "c", "a"]);
    expect(novo.por_status!.APLICADO!.map((c) => c.posicao)).toEqual([0, 1, 2]);
  });

  it("limita a posição ao fim da coluna", () => {
    const novo = aplicarMovimento(quadro(), "a", { status: "ENTREVISTA", posicao: 99 });

    expect(ids(novo, "ENTREVISTA")).toEqual(["x", "y", "a"]);
  });

  it("mantém o total e não altera o quadro original", () => {
    const original = quadro();

    const novo = aplicarMovimento(original, "a", { status: "OFERTA", posicao: 0 });

    expect(novo.total).toBe(5);
    expect(ids(original, "APLICADO")).toEqual(["a", "b", "c"]);
  });

  it("devolve o quadro igual quando o cartão não existe", () => {
    const original = quadro();

    expect(aplicarMovimento(original, "nao-existe", { status: "OFERTA", posicao: 0 })).toBe(
      original,
    );
  });

  it("aceita um quadro com coluna ausente", () => {
    const original: CandidaturasPorStatus = {
      por_status: { APLICADO: [cartao("a", "APLICADO", 0)] },
      total: 1,
    };

    const novo = aplicarMovimento(original, "a", { status: "OFERTA", posicao: 0 });

    expect(ids(novo, "OFERTA")).toEqual(["a"]);
  });
});
