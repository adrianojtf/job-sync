import type { Candidatura, CandidaturasPorStatus } from "../../api/tipos";
import { criarAnuncios } from "./anuncios";

const cartao = (id: string, cargo: string, status: string, posicao: number): Candidatura => ({
  id,
  perfil_identificador: "adriano",
  vaga_id: "v",
  curriculo_salvo_id: "c",
  empresa: "Empresa",
  cargo,
  status,
  data_aplicacao: "2026-11-02T09:00:00",
  historico_status: [],
  posicao,
});

const quadro: CandidaturasPorStatus = {
  por_status: {
    APLICADO: [cartao("a", "Vaga A", "APLICADO", 0), cartao("b", "Vaga B", "APLICADO", 1)],
    ENTREVISTA: [cartao("x", "Vaga X", "ENTREVISTA", 0)],
    OFERTA: [],
    REJEITADO: [],
  },
  total: 3,
};

const anuncios = criarAnuncios(() => quadro);
const ativo = (id: string) => ({ id }) as never;
const sobre = (id: string | null) => (id ? { id } : null) as never;

describe("criarAnuncios", () => {
  it("anuncia ao pegar o cartão com a posição e a coluna", () => {
    expect(anuncios.onDragStart!({ active: ativo("b") } as never)).toBe(
      "Candidatura Vaga B pega. Posição 2 de 2 em Aplicado.",
    );
  });

  it("anuncia a posição de destino em outra coluna", () => {
    expect(anuncios.onDragOver!({ active: ativo("a"), over: sobre("x") } as never)).toBe(
      "Candidatura Vaga A sobre Entrevista, posição 1 de 2.",
    );
  });

  it("anuncia a coluna vazia como destino", () => {
    expect(
      anuncios.onDragOver!({ active: ativo("a"), over: sobre("coluna:OFERTA") } as never),
    ).toBe("Candidatura Vaga A sobre Oferta, posição 1 de 1.");
  });

  it("anuncia a nova posição ao reordenar na mesma coluna", () => {
    expect(anuncios.onDragOver!({ active: ativo("a"), over: sobre("b") } as never)).toBe(
      "Candidatura Vaga A sobre Aplicado, posição 2 de 2.",
    );
  });

  it("anuncia a posição original quando nada muda", () => {
    expect(anuncios.onDragOver!({ active: ativo("a"), over: sobre("a") } as never)).toBe(
      "Candidatura Vaga A na posição original.",
    );
  });

  it("anuncia quando o cartão está fora das colunas", () => {
    expect(anuncios.onDragOver!({ active: ativo("a"), over: sobre(null) } as never)).toBe(
      "Candidatura Vaga A fora das colunas.",
    );
  });

  it("anuncia o destino ao soltar", () => {
    expect(anuncios.onDragEnd!({ active: ativo("a"), over: sobre("x") } as never)).toBe(
      "Candidatura Vaga A solta em Entrevista, posição 1 de 2.",
    );
  });

  it("anuncia que nada foi alterado ao soltar fora", () => {
    expect(anuncios.onDragEnd!({ active: ativo("a"), over: sobre(null) } as never)).toBe(
      "Candidatura Vaga A solta fora das colunas. Nada foi alterado.",
    );
  });

  it("anuncia o cancelamento", () => {
    expect(anuncios.onDragCancel!({ active: ativo("a"), over: sobre(null) } as never)).toBe(
      "Movimento cancelado. Candidatura Vaga A voltou à posição original.",
    );
  });
});
