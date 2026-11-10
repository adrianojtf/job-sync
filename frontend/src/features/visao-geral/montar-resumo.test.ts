import type {
  CandidaturasPorStatus,
  CurriculoSalvo,
  PerfilEstruturado,
  Vaga,
} from "../../api/tipos";
import { calcularCompletude, montarResumo } from "./montar-resumo";

const curriculo = (id: string, data: string): CurriculoSalvo => ({
  id,
  perfil_identificador: "adriano",
  nome_referencia: `CV ${id}`,
  data_upload: data,
});

const vaga = (id: string, texto: string, data: string, url: string | null = null): Vaga => ({
  id,
  perfil_identificador: "adriano",
  texto_descricao: texto,
  url_origem: url,
  data_captura: data,
});

const candidatura = (
  id: string,
  status: string,
  historico: { status: string; data: string }[],
) => ({
  id,
  perfil_identificador: "adriano",
  vaga_id: `vaga-${id}`,
  curriculo_salvo_id: "c1",
  empresa: `Empresa ${id}`,
  cargo: `Cargo ${id}`,
  status,
  data_aplicacao: "2026-11-01T09:00:00",
  historico_status: historico,
  posicao: 0,
});

function porStatus(...lista: ReturnType<typeof candidatura>[]): CandidaturasPorStatus {
  const grupos: Record<string, ReturnType<typeof candidatura>[]> = {
    APLICADO: [],
    ENTREVISTA: [],
    OFERTA: [],
    REJEITADO: [],
  };
  lista.forEach((item) => grupos[item.status]!.push(item));
  return { por_status: grupos, total: lista.length };
}

describe("montarResumo", () => {
  it("devolve zeros e listas vazias sem dados", () => {
    const resumo = montarResumo({ curriculos: [], vagas: [], candidaturas: porStatus() });

    expect(resumo).toEqual({
      curriculos: 0,
      vagasSalvas: 0,
      candidaturasAtivas: 0,
      aguardandoRetorno: 0,
      emEntrevistaOuOferta: 0,
      comOferta: 0,
      itensRecentes: [],
      atividades: [],
    });
  });

  it("conta ativas (Aplicado + Entrevista) e entrevista/oferta", () => {
    const resumo = montarResumo({
      curriculos: [curriculo("c1", "2026-11-01T10:00:00")],
      vagas: [vaga("v1", "Dev", "2026-11-02T10:00:00")],
      candidaturas: porStatus(
        candidatura("a", "APLICADO", []),
        candidatura("b", "APLICADO", []),
        candidatura("c", "ENTREVISTA", []),
        candidatura("d", "OFERTA", []),
        candidatura("e", "REJEITADO", []),
      ),
    });

    expect(resumo.curriculos).toBe(1);
    expect(resumo.vagasSalvas).toBe(1);
    expect(resumo.candidaturasAtivas).toBe(3);
    expect(resumo.aguardandoRetorno).toBe(2);
    expect(resumo.emEntrevistaOuOferta).toBe(2);
    expect(resumo.comOferta).toBe(1);
  });

  it("lista atividades da mais recente para a mais antiga", () => {
    const resumo = montarResumo({
      curriculos: [curriculo("c1", "2026-11-01T10:00:00")],
      vagas: [vaga("v1", "Senior Java\nNeoway", "2026-11-03T10:00:00")],
      candidaturas: porStatus(
        candidatura("a", "ENTREVISTA", [{ status: "ENTREVISTA", data: "2026-11-05T15:00:00" }]),
        candidatura("b", "APLICADO", [{ status: "APLICADO", data: "2026-11-04T09:00:00" }]),
      ),
    });

    expect(resumo.atividades.map((atividade) => atividade.descricao)).toEqual([
      "Cargo a movida para Entrevista",
      "Candidatura criada: Cargo b",
      "Vaga salva: Senior Java",
      "Currículo enviado: CV c1",
    ]);
    expect(resumo.atividades[0]).toMatchObject({
      tipo: "status_candidatura",
      data: "2026-11-05T15:00:00",
    });
  });

  it("limita as atividades às 6 mais recentes", () => {
    const vagas = Array.from({ length: 9 }, (_, indice) =>
      vaga(`v${indice}`, `Vaga ${indice}`, `2026-11-0${indice + 1}T10:00:00`),
    );

    const resumo = montarResumo({ curriculos: [], vagas, candidaturas: porStatus() });

    expect(resumo.atividades).toHaveLength(6);
    expect(resumo.atividades[0]?.descricao).toBe("Vaga salva: Vaga 8");
  });

  it("monta os itens recentes com candidaturas e vagas, do mais novo ao mais antigo, até 5", () => {
    const resumo = montarResumo({
      curriculos: [],
      vagas: [
        vaga(
          "v1",
          "Platform Engineer\nThoughtworks",
          "2026-11-04T10:00:00",
          "https://www.linkedin.com/jobs/1",
        ),
        vaga("v2", "Antiga", "2026-10-01T10:00:00"),
      ],
      candidaturas: porStatus(
        candidatura("a", "ENTREVISTA", [{ status: "ENTREVISTA", data: "2026-11-05T15:00:00" }]),
        candidatura("b", "APLICADO", []),
        candidatura("c", "OFERTA", []),
        candidatura("d", "REJEITADO", []),
        candidatura("e", "APLICADO", []),
      ),
    });

    expect(resumo.itensRecentes).toHaveLength(5);
    expect(resumo.itensRecentes[0]).toEqual({
      id: "a",
      tipo: "candidatura",
      titulo: "Cargo a",
      subtitulo: "Empresa a",
      data: "2026-11-05T15:00:00",
      status: "ENTREVISTA",
      destino: "/candidaturas",
    });
    expect(resumo.itensRecentes[1]).toEqual({
      id: "v1",
      tipo: "vaga",
      titulo: "Platform Engineer",
      subtitulo: "linkedin.com",
      data: "2026-11-04T10:00:00",
      destino: "/vagas-salvas",
    });
    expect(resumo.itensRecentes.map((item) => item.id)).not.toContain("v2");
  });
});

describe("calcularCompletude", () => {
  const vazio: PerfilEstruturado = {
    perfil_identificador: "adriano",
    nome_completo: "",
    email: "",
    linkedin: "",
    resumo_profissional: "",
    experiencias: [],
    formacoes: [],
    certificacoes: [],
    idiomas: [],
    tecnologias: [],
  };

  it("é 0 sem perfil", () => {
    expect(calcularCompletude(null)).toBe(0);
  });

  it("conta as 7 seções preenchidas", () => {
    const parcial = {
      ...vazio,
      nome_completo: "Adriano",
      email: "a@b.com",
      experiencias: [{ empresa: "X", cargo: "Y", periodo: "", descricao: "" }],
      tecnologias: ["Java"],
    };

    expect(calcularCompletude(parcial)).toBe(43);
  });

  it("dados pessoais exigem nome e e-mail", () => {
    expect(calcularCompletude({ ...vazio, nome_completo: "Adriano" })).toBe(0);
  });

  it("é 100 com todas as seções", () => {
    const completo: PerfilEstruturado = {
      ...vazio,
      nome_completo: "Adriano",
      email: "a@b.com",
      resumo_profissional: "Backend.",
      experiencias: [{ empresa: "X", cargo: "Y", periodo: "", descricao: "" }],
      formacoes: [{ instituicao: "U", curso: "C", periodo: "" }],
      certificacoes: [{ nome: "AWS", instituicao: "", ano: "" }],
      idiomas: [{ idioma: "Inglês", nivel: "FLUENTE" }],
      tecnologias: ["Java"],
    };

    expect(calcularCompletude(completo)).toBe(100);
  });
});
