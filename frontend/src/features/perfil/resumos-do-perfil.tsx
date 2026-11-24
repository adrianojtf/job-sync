import type { ResumoDoItem } from "../../shared/formulario-curriculo/CartaoDaLista";
import { ChipsDaExperiencia } from "./ChipsDaExperiencia";
import { ehLegada, type ExperienciaPerfilFormulario } from "./formulario-perfil";

const junta = (partes: string[], separador: string) =>
  partes
    .map((parte) => parte.trim())
    .filter(Boolean)
    .join(separador);

/** Chave do item para lembrar o cartão aberto: o conteúdo que o identifica; vazia se ainda não há nenhum. */
const chaveDe = (...partes: string[]) =>
  partes.every((parte) => parte.trim() === "") ? "" : partes.map((p) => p.trim()).join("|");

const primeiraLinha = (texto: string) =>
  texto
    .split("\n")
    .map((linha) => linha.trim())
    .find(Boolean) ?? "";

export function resumoDaExperiencia(experiencia: ExperienciaPerfilFormulario): ResumoDoItem {
  const legada = ehLegada(experiencia);
  return {
    titulo: junta([experiencia.cargo, experiencia.empresa], " · "),
    subtitulo:
      primeiraLinha(legada ? experiencia.descricao : experiencia.contexto) || "Sem contexto ainda",
    meta: experiencia.periodo,
    inicial: experiencia.empresa,
    chips: <ChipsDaExperiencia experiencia={experiencia} />,
  };
}
export const chaveDaExperiencia = (e: { empresa: string; cargo: string; periodo: string }) =>
  chaveDe(e.empresa, e.cargo, e.periodo);

export interface FormacaoDoFormulario {
  instituicao: string;
  curso: string;
  periodo: string;
}
export const resumoDaFormacao = (f: FormacaoDoFormulario): ResumoDoItem => ({
  titulo: f.curso,
  subtitulo: f.instituicao || "Instituição",
  meta: f.periodo,
  inicial: f.instituicao,
});
export const chaveDaFormacao = (f: FormacaoDoFormulario) =>
  chaveDe(f.instituicao, f.curso, f.periodo);

export interface CertificacaoDoFormulario {
  nome: string;
  instituicao: string;
  ano: string;
}
export const resumoDaCertificacao = (c: CertificacaoDoFormulario): ResumoDoItem => ({
  titulo: c.nome,
  subtitulo: c.instituicao || "Instituição",
  meta: c.ano,
  inicial: c.instituicao || c.nome,
});
export const chaveDaCertificacao = (c: CertificacaoDoFormulario) =>
  chaveDe(c.nome, c.instituicao, c.ano);
