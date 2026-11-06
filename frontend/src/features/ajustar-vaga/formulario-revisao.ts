import type { RascunhoCurriculoAdaptado } from "../../api/tipos";
import type {
  DadosPessoaisFormulario,
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
  experiencias: ExperienciaFormulario[];
  secoes: SecaoRascunho[];
}

export function rascunhoParaFormulario(rascunho: RascunhoCurriculoAdaptado): FormularioRevisao {
  return {
    nome_completo: rascunho.nome_completo,
    email: rascunho.email ?? "",
    linkedin: rascunho.linkedin ?? "",
    resumo_profissional: secaoPerfil(rascunho)?.conteudo ?? "",
    experiencias: (rascunho.experiencias ?? []).map((experiencia) => ({
      cargo: experiencia.cargo ?? "",
      empresa: experiencia.empresa ?? "",
      periodo: experiencia.periodo ?? "",
      descricao: experiencia.descricao ?? "",
    })),
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
        : formulario.experiencias.map((experiencia) => ({
            cargo: experiencia.cargo.trim(),
            empresa: experiencia.empresa.trim(),
            periodo: experiencia.periodo.trim(),
            descricao: experiencia.descricao.trim(),
          })),
  };
}

/** Título da seção de resumo do rascunho; o padrão vale quando a IA não devolveu o resumo. */
export function tituloSecaoPerfil(rascunho: RascunhoCurriculoAdaptado): string {
  return secaoPerfil(rascunho)?.titulo ?? TITULO_PERFIL_PADRAO;
}

function secaoPerfil(rascunho: RascunhoCurriculoAdaptado): SecaoRascunho | undefined {
  return rascunho.secoes.find((secao) => secao.tipo === "PERFIL");
}
