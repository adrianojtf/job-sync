import type { PerfilEstruturado, PerfilEstruturadoEntrada } from "../../api/tipos";

export type NivelIdioma = "BASICO" | "INTERMEDIARIO" | "AVANCADO" | "FLUENTE" | "NATIVO";

export const NIVEIS_IDIOMA: { valor: NivelIdioma; rotulo: string }[] = [
  { valor: "BASICO", rotulo: "Básico" },
  { valor: "INTERMEDIARIO", rotulo: "Intermediário" },
  { valor: "AVANCADO", rotulo: "Avançado" },
  { valor: "FLUENTE", rotulo: "Fluente" },
  { valor: "NATIVO", rotulo: "Nativo" },
];

export interface ExperienciaFormulario {
  empresa: string;
  cargo: string;
  periodo: string;
  descricao: string;
}

/** Estado do formulário de Meu perfil: tecnologias ficam como texto separado por vírgula. */
export interface FormularioPerfil {
  nome_completo: string;
  email: string;
  linkedin: string;
  resumo_profissional: string;
  experiencias: ExperienciaFormulario[];
  formacoes: { instituicao: string; curso: string; periodo: string }[];
  certificacoes: { nome: string; instituicao: string; ano: string }[];
  idiomas: { idioma: string; nivel: string }[];
  tecnologias: string;
}

export const EXPERIENCIA_VAZIA: ExperienciaFormulario = {
  empresa: "",
  cargo: "",
  periodo: "",
  descricao: "",
};
export const FORMACAO_VAZIA = { instituicao: "", curso: "", periodo: "" };
export const CERTIFICACAO_VAZIA = { nome: "", instituicao: "", ano: "" };
export const IDIOMA_VAZIO = { idioma: "", nivel: "INTERMEDIARIO" };

export function perfilParaFormulario(perfil: PerfilEstruturado | null): FormularioPerfil {
  return {
    nome_completo: perfil?.nome_completo ?? "",
    email: perfil?.email ?? "",
    linkedin: perfil?.linkedin ?? "",
    resumo_profissional: perfil?.resumo_profissional ?? "",
    experiencias: (perfil?.experiencias ?? []).map((item) => ({ ...item })),
    formacoes: (perfil?.formacoes ?? []).map((item) => ({ ...item })),
    certificacoes: (perfil?.certificacoes ?? []).map((item) => ({ ...item })),
    idiomas: (perfil?.idiomas ?? []).map((item) => ({ ...item })),
    tecnologias: (perfil?.tecnologias ?? []).join(", "),
  };
}

function aparar<T extends object>(item: T): T {
  return Object.fromEntries(
    Object.entries(item).map(([chave, valor]) => [
      chave,
      typeof valor === "string" ? valor.trim() : valor,
    ]),
  ) as T;
}

export function formularioParaEntrada(
  formulario: FormularioPerfil,
  perfilIdentificador: string,
): PerfilEstruturadoEntrada {
  return {
    perfil_identificador: perfilIdentificador,
    nome_completo: formulario.nome_completo.trim(),
    email: formulario.email.trim(),
    linkedin: formulario.linkedin.trim(),
    resumo_profissional: formulario.resumo_profissional.trim(),
    experiencias: formulario.experiencias.map(aparar),
    formacoes: formulario.formacoes.map(aparar),
    certificacoes: formulario.certificacoes.map(aparar),
    idiomas: formulario.idiomas.map(aparar),
    tecnologias: formulario.tecnologias
      .split(",")
      .map((tecnologia) => tecnologia.trim())
      .filter(Boolean),
  };
}
