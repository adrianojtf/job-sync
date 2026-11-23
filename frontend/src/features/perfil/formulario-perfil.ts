import type { PerfilEstruturado, PerfilEstruturadoEntrada } from "../../api/tipos";
import {
  EXPERIENCIA_VAZIA,
  type DadosPessoaisFormulario,
  type ExperienciaFormulario,
} from "../../shared/formulario-curriculo/campos-curriculo";

export type NivelIdioma = "BASICO" | "INTERMEDIARIO" | "AVANCADO" | "FLUENTE" | "NATIVO";

export const NIVEIS_IDIOMA: { valor: NivelIdioma; rotulo: string }[] = [
  { valor: "BASICO", rotulo: "Básico" },
  { valor: "INTERMEDIARIO", rotulo: "Intermediário" },
  { valor: "AVANCADO", rotulo: "Avançado" },
  { valor: "FLUENTE", rotulo: "Fluente" },
  { valor: "NATIVO", rotulo: "Nativo" },
];

export type OrigemConquista = "MANUAL" | "RESPOSTA_PERGUNTA";

/** Conquista do banco da experiência (JOB-0042); a origem é preservada ao editar o texto. */
export interface ConquistaFormulario {
  texto: string;
  origem: OrigemConquista;
}

/** Experiência do perfil: os campos de sempre mais o banco de conquistas. */
export interface ExperienciaPerfilFormulario extends ExperienciaFormulario {
  conquistas: ConquistaFormulario[];
}

/** Dados da experiência sem o banco de conquistas: o que as sugestões e a avaliação de IA recebem. */
export function experienciaSemConquistas(
  experiencia: ExperienciaPerfilFormulario,
): ExperienciaFormulario {
  return {
    empresa: experiencia.empresa,
    cargo: experiencia.cargo,
    periodo: experiencia.periodo,
    descricao: experiencia.descricao,
  };
}

export const EXPERIENCIA_PERFIL_VAZIA: ExperienciaPerfilFormulario = {
  ...EXPERIENCIA_VAZIA,
  conquistas: [],
};

/** Estado do formulário de Meu perfil: tecnologias ficam como texto separado por vírgula. */
export interface FormularioPerfil extends DadosPessoaisFormulario {
  experiencias: ExperienciaPerfilFormulario[];
  formacoes: { instituicao: string; curso: string; periodo: string }[];
  certificacoes: { nome: string; instituicao: string; ano: string }[];
  idiomas: { idioma: string; nivel: string }[];
  tecnologias: string;
}

export const FORMACAO_VAZIA = { instituicao: "", curso: "", periodo: "" };
export const CERTIFICACAO_VAZIA = { nome: "", instituicao: "", ano: "" };
export const IDIOMA_VAZIO = { idioma: "", nivel: "INTERMEDIARIO" };

export function perfilParaFormulario(perfil: PerfilEstruturado | null): FormularioPerfil {
  return {
    nome_completo: perfil?.nome_completo ?? "",
    email: perfil?.email ?? "",
    linkedin: perfil?.linkedin ?? "",
    resumo_profissional: perfil?.resumo_profissional ?? "",
    experiencias: (perfil?.experiencias ?? []).map((item) => ({
      ...item,
      conquistas: (item.conquistas ?? []).map((conquista) => ({
        texto: conquista.texto,
        origem: conquista.origem ?? "MANUAL",
      })),
    })),
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
    experiencias: formulario.experiencias.map((experiencia) => ({
      ...aparar(experiencia),
      conquistas: experiencia.conquistas
        .map((conquista) => ({ texto: conquista.texto.trim(), origem: conquista.origem }))
        .filter((conquista) => conquista.texto !== ""),
    })),
    formacoes: formulario.formacoes.map(aparar),
    certificacoes: formulario.certificacoes.map(aparar),
    idiomas: formulario.idiomas.map(aparar),
    tecnologias: formulario.tecnologias
      .split(",")
      .map((tecnologia) => tecnologia.trim())
      .filter(Boolean),
  };
}
