import type { ExperienciaAdaptada, RascunhoCurriculoAdaptado } from "../../api/tipos";
import type {
  DadosPessoaisFormulario,
  ExperienciaAdaptadaFormulario,
  ExperienciaFormulario,
} from "../../shared/formulario-curriculo/campos-curriculo";

type SecaoRascunho = RascunhoCurriculoAdaptado["secoes"][number];
export type TipoSecao = SecaoRascunho["tipo"];

/** Seções de texto editáveis na revisão, na ordem de exibição do cadastro. */
export const ORDEM_SECOES_TEXTO: TipoSecao[] = [
  "EXPERIENCIAS",
  "TECNOLOGIAS",
  "FORMACAO",
  "CERTIFICACOES",
  "IDIOMAS",
];

const TITULO_PERFIL_PADRAO = "Perfil";

/**
 * Estado do formulário de revisão: o resumo (seção PERFIL) fica nos dados pessoais, como no
 * cadastro; as experiências ficam estruturadas quando a fonte é o perfil; o resto é texto.
 */
export interface FormularioRevisao extends DadosPessoaisFormulario {
  experiencias: ExperienciaAdaptadaFormulario[];
  secoes: SecaoRascunho[];
}

export function rascunhoParaFormulario(rascunho: RascunhoCurriculoAdaptado): FormularioRevisao {
  return {
    nome_completo: rascunho.nome_completo,
    email: rascunho.email ?? "",
    linkedin: rascunho.linkedin ?? "",
    resumo_profissional: secaoPerfil(rascunho)?.conteudo ?? "",
    experiencias: (rascunho.experiencias ?? []).map(experienciaAdaptadaParaFormulario),
    secoes: ORDEM_SECOES_TEXTO.flatMap((tipo) =>
      rascunho.secoes.filter((secao) => secao.tipo === tipo).map((secao) => ({ ...secao })),
    ),
  };
}

/** Monta o rascunho revisado; seções em branco seguem vazias e o backend as descarta. */
export function formularioParaRascunho(
  formulario: FormularioRevisao,
  original: RascunhoCurriculoAdaptado,
): RascunhoCurriculoAdaptado {
  return {
    ...original,
    nome_completo: formulario.nome_completo.trim(),
    email: formulario.email.trim(),
    linkedin: formulario.linkedin.trim(),
    secoes: [
      {
        tipo: "PERFIL",
        titulo: tituloSecaoPerfil(original),
        conteudo: formulario.resumo_profissional.trim(),
      },
      ...formulario.secoes.map((secao) => ({ ...secao, conteudo: secao.conteudo.trim() })),
    ],
    experiencias:
      original.experiencias == null
        ? null
        : formulario.experiencias.map(formularioParaExperienciaAdaptada),
  };
}

/** Título da seção de resumo do rascunho; o padrão vale quando a IA não devolveu o resumo. */
export function tituloSecaoPerfil(rascunho: RascunhoCurriculoAdaptado): string {
  return secaoPerfil(rascunho)?.titulo ?? TITULO_PERFIL_PADRAO;
}

function secaoPerfil(rascunho: RascunhoCurriculoAdaptado): SecaoRascunho | undefined {
  return rascunho.secoes.find((secao) => secao.tipo === "PERFIL");
}

/** Cada linha do texto é uma conquista; linhas em branco e espaços nas pontas são ignorados. */
export function linhasParaConquistas(texto: string): string[] {
  return texto
    .split("\n")
    .map((linha) => linha.trim())
    .filter((linha) => linha !== "");
}

export function conquistasParaLinhas(conquistas: string[]): string {
  return conquistas.join("\n");
}

/** Leva uma experiência da API para o formulário, com as conquistas em linhas de texto. */
export function experienciaAdaptadaParaFormulario(
  experiencia: ExperienciaAdaptada,
): ExperienciaAdaptadaFormulario {
  return {
    cargo: experiencia.cargo ?? "",
    empresa: experiencia.empresa ?? "",
    periodo: experiencia.periodo ?? "",
    conquistas: conquistasParaLinhas(experiencia.conquistas ?? []),
    contexto: experiencia.contexto ?? "",
  };
}

/** Devolve a experiência editada ao formato da API, com textos aparados e conquistas em lista. */
export function formularioParaExperienciaAdaptada(
  formulario: ExperienciaAdaptadaFormulario,
): ExperienciaAdaptada {
  return {
    cargo: formulario.cargo.trim(),
    empresa: formulario.empresa.trim(),
    periodo: formulario.periodo.trim(),
    conquistas: linhasParaConquistas(formulario.conquistas),
    contexto: formulario.contexto.trim(),
  };
}

/**
 * Texto que o avaliador recebe: conquistas em bullets e o contexto, sem cabeçalho nem rótulo.
 * Espelha `ExperienciaAdaptada.para_avaliacao` do backend; os testes dos dois lados usam os
 * mesmos exemplos para não divergirem.
 */
export function descricaoParaAvaliacao(formulario: ExperienciaAdaptadaFormulario): string {
  const linhas = linhasParaConquistas(formulario.conquistas).map((conquista) => `- ${conquista}`);
  if (formulario.contexto.trim() !== "") linhas.push(formulario.contexto.trim());
  return linhas.join("\n");
}

/** Experiência no formato do modal "Avaliar", com a descrição composta. */
export function experienciaAdaptadaParaAvaliacao(
  formulario: ExperienciaAdaptadaFormulario,
): ExperienciaFormulario {
  return {
    empresa: formulario.empresa,
    cargo: formulario.cargo,
    periodo: formulario.periodo,
    descricao: descricaoParaAvaliacao(formulario),
  };
}
