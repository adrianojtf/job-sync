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
 * Experiência da revisão do currículo adaptado (JOB-0035 e JOB-0045): os quatro blocos. As
 * responsabilidades e as conquistas (as principais realizações) ficam em um texto, um item por
 * linha; as skills ficam em tags.
 */
export interface ExperienciaAdaptadaFormulario {
  empresa: string;
  cargo: string;
  periodo: string;
  contexto: string;
  responsabilidades: string;
  conquistas: string;
  skills: string[];
}

export const EXPERIENCIA_ADAPTADA_VAZIA: ExperienciaAdaptadaFormulario = {
  empresa: "",
  cargo: "",
  periodo: "",
  contexto: "",
  responsabilidades: "",
  conquistas: "",
  skills: [],
};

export const CAMPOS_EXPERIENCIA_ADAPTADA: CampoItem[] = [
  ...CAMPOS_IDENTIFICACAO_EXPERIENCIA,
  {
    chave: "contexto",
    rotulo: "Contexto",
    tipoCampo: "textarea",
    larguraTotal: true,
    ajuda: "Empresa, área e seu papel, em poucas frases.",
  },
  {
    chave: "responsabilidades",
    rotulo: "Principais responsabilidades",
    tipoCampo: "textarea",
    larguraTotal: true,
    ajuda: "Uma responsabilidade por linha.",
  },
  {
    chave: "conquistas",
    rotulo: "Principais realizações",
    tipoCampo: "textarea",
    larguraTotal: true,
    ajuda: "Uma realização por linha.",
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
