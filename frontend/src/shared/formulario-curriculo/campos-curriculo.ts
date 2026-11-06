/** Campos de formulário de currículo compartilhados entre o cadastro e a revisão. */

export interface CampoItem {
  chave: string;
  rotulo: string;
  obrigatorio?: string;
  tipoCampo?: "textarea" | "select";
  opcoes?: { valor: string; rotulo: string }[];
  larguraTotal?: boolean;
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

export const CAMPOS_EXPERIENCIA: CampoItem[] = [
  { chave: "empresa", rotulo: "Empresa", obrigatorio: "Informe a empresa." },
  { chave: "cargo", rotulo: "Cargo", obrigatorio: "Informe o cargo." },
  { chave: "periodo", rotulo: "Período", larguraTotal: true },
  { chave: "descricao", rotulo: "Descrição", tipoCampo: "textarea", larguraTotal: true },
];

/** Dados pessoais e resumo, presentes em todo formulário de currículo. */
export interface DadosPessoaisFormulario {
  nome_completo: string;
  email: string;
  linkedin: string;
  resumo_profissional: string;
}
