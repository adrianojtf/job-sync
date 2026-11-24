/** Campos de formulário de currículo compartilhados entre o cadastro e a revisão. */

export interface CampoItem {
  chave: string;
  rotulo: string;
  obrigatorio?: string;
  tipoCampo?: "textarea" | "select";
  opcoes?: { valor: string; rotulo: string }[];
  larguraTotal?: boolean;
  /** Texto de apoio associado ao campo (aria-describedby). */
  ajuda?: string;
}

export interface ExperienciaFormulario {
  empresa: string;
  cargo: string;
  periodo: string;
  descricao: string;
}

export const EXPERIENCIA_VAZIA: ExperienciaFormulario = {
  empresa: "",
  cargo: "",
  periodo: "",
  descricao: "",
};

const CAMPO_EMPRESA: CampoItem = {
  chave: "empresa",
  rotulo: "Empresa",
  obrigatorio: "Informe a empresa.",
};
const CAMPO_CARGO: CampoItem = { chave: "cargo", rotulo: "Cargo", obrigatorio: "Informe o cargo." };
const CAMPO_PERIODO: CampoItem = { chave: "periodo", rotulo: "Período", larguraTotal: true };

/** Identificação da experiência; os blocos de conteúdo ficam por conta de quem usa. */
export const CAMPOS_IDENTIFICACAO_EXPERIENCIA: CampoItem[] = [
  CAMPO_EMPRESA,
  CAMPO_CARGO,
  CAMPO_PERIODO,
];

/**
 * Experiência da revisão do currículo adaptado (JOB-0035): conquistas e contexto no lugar da
 * descrição. As conquistas ficam em um texto, uma por linha.
 */
export interface ExperienciaAdaptadaFormulario {
  empresa: string;
  cargo: string;
  periodo: string;
  conquistas: string;
  contexto: string;
}

export const EXPERIENCIA_ADAPTADA_VAZIA: ExperienciaAdaptadaFormulario = {
  empresa: "",
  cargo: "",
  periodo: "",
  conquistas: "",
  contexto: "",
};

export const CAMPOS_EXPERIENCIA_ADAPTADA: CampoItem[] = [
  CAMPO_EMPRESA,
  CAMPO_CARGO,
  CAMPO_PERIODO,
  {
    chave: "conquistas",
    rotulo: "Conquistas",
    tipoCampo: "textarea",
    larguraTotal: true,
    ajuda: "Uma conquista por linha.",
  },
  {
    chave: "contexto",
    rotulo: "Contexto",
    tipoCampo: "textarea",
    larguraTotal: true,
    ajuda: "Empresa, área e seu papel, em poucas frases.",
  },
];

/** Dados pessoais e resumo, presentes em todo formulário de currículo. */
export interface DadosPessoaisFormulario {
  nome_completo: string;
  email: string;
  linkedin: string;
  resumo_profissional: string;
}

/** Categoria de competências da revisão (JOB-0041): um nome e as suas tags. */
export interface CategoriaFormulario {
  nome: string;
  tags: string[];
}

export const CATEGORIA_VAZIA: CategoriaFormulario = { nome: "", tags: [] };
