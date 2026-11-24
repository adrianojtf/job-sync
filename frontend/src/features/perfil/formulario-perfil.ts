import type {
  ExperienciaParaIA,
  PerfilEstruturado,
  PerfilEstruturadoEntrada,
} from "../../api/tipos";
import {
  EXPERIENCIA_VAZIA,
  type DadosPessoaisFormulario,
  type ExperienciaFormulario,
} from "../../shared/formulario-curriculo/campos-curriculo";
import { linhasParaTexto, textoParaLinhas } from "../../shared/formulario-curriculo/linhas";

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

/**
 * Experiência do perfil (JOB-0045): os quatro blocos e a descrição em texto livre, que só resta
 * nos perfis antigos. `conquistas` é o banco de conquistas, as "Principais realizações".
 * As responsabilidades ficam em um texto, uma por linha; as skills, em tags.
 */
export interface ExperienciaPerfilFormulario extends ExperienciaFormulario {
  contexto: string;
  responsabilidades: string;
  conquistas: ConquistaFormulario[];
  skills: string[];
}

export const EXPERIENCIA_PERFIL_VAZIA: ExperienciaPerfilFormulario = {
  ...EXPERIENCIA_VAZIA,
  contexto: "",
  responsabilidades: "",
  conquistas: [],
  skills: [],
};

/** Indica se a experiência tem algum dos quatro blocos preenchido. */
export function temBlocos(experiencia: ExperienciaPerfilFormulario): boolean {
  return (
    experiencia.contexto.trim() !== "" ||
    textoParaLinhas(experiencia.responsabilidades).length > 0 ||
    experiencia.conquistas.some((conquista) => conquista.texto.trim() !== "") ||
    experiencia.skills.length > 0
  );
}

/** Experiência no formato antigo: só a descrição em texto livre, sem nenhum bloco. */
export function ehLegada(experiencia: ExperienciaPerfilFormulario): boolean {
  return experiencia.descricao.trim() !== "" && !temBlocos(experiencia);
}

/** Dados da experiência no formato antigo (sem blocos): o que a sugestão da descrição recebe. */
export function experienciaDaDescricao(
  experiencia: ExperienciaPerfilFormulario,
): ExperienciaFormulario {
  return {
    empresa: experiencia.empresa,
    cargo: experiencia.cargo,
    periodo: experiencia.periodo,
    descricao: experiencia.descricao,
  };
}

/** Experiência com a descrição e os quatro blocos: o que as sugestões e a avaliação de IA recebem. */
export function experienciaParaIA(experiencia: ExperienciaPerfilFormulario): ExperienciaParaIA {
  return {
    empresa: experiencia.empresa,
    cargo: experiencia.cargo,
    periodo: experiencia.periodo,
    descricao: experiencia.descricao,
    contexto: experiencia.contexto.trim(),
    responsabilidades: textoParaLinhas(experiencia.responsabilidades),
    conquistas: experiencia.conquistas.map((conquista) => conquista.texto.trim()).filter(Boolean),
    skills: experiencia.skills,
  };
}

/** Texto dos quatro blocos, um item por linha: o que o painel da sugestão compara e mostra. */
export function textoDosBlocos(experiencia: ExperienciaPerfilFormulario): string {
  const ia = experienciaParaIA(experiencia);
  return [
    ...(ia.responsabilidades ?? []),
    ...(ia.conquistas ?? []),
    ia.contexto ?? "",
    (ia.skills ?? []).join(", "),
  ]
    .filter((linha) => linha !== "")
    .join("\n");
}

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
      empresa: item.empresa,
      cargo: item.cargo,
      periodo: item.periodo,
      descricao: item.descricao,
      contexto: item.contexto ?? "",
      responsabilidades: linhasParaTexto(item.responsabilidades ?? []),
      conquistas: (item.conquistas ?? []).map((conquista) => ({
        texto: conquista.texto,
        origem: conquista.origem ?? "MANUAL",
      })),
      skills: [...(item.skills ?? [])],
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
      empresa: experiencia.empresa.trim(),
      cargo: experiencia.cargo.trim(),
      periodo: experiencia.periodo.trim(),
      descricao: experiencia.descricao.trim(),
      contexto: experiencia.contexto.trim(),
      responsabilidades: textoParaLinhas(experiencia.responsabilidades),
      conquistas: experiencia.conquistas
        .map((conquista) => ({ texto: conquista.texto.trim(), origem: conquista.origem }))
        .filter((conquista) => conquista.texto !== ""),
      skills: experiencia.skills,
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
