/** Fonte única das páginas: alimenta o menu lateral, as rotas e a trilha. */
export interface Pagina {
  caminho: string;
  titulo: string;
  /** Tarefa do JOB-0015 que entrega a tela (exibida enquanto ela não existe). */
  tarefa: string;
  icone?: string;
  grupo?: "principal" | "preferencias";
}

export const PAGINAS: Pagina[] = [
  { caminho: "/", titulo: "Visão geral", icone: "▦", grupo: "principal", tarefa: "9.0" },
  {
    caminho: "/curriculos",
    titulo: "Meus currículos",
    icone: "▤",
    grupo: "principal",
    tarefa: "5.0",
  },
  {
    caminho: "/vagas-salvas",
    titulo: "Vagas salvas",
    icone: "☆",
    grupo: "principal",
    tarefa: "7.0",
  },
  {
    caminho: "/descobrir-vagas",
    titulo: "Descobrir vagas",
    icone: "⌕",
    grupo: "principal",
    tarefa: "8.0",
  },
  {
    caminho: "/candidaturas",
    titulo: "Candidaturas",
    icone: "◷",
    grupo: "principal",
    tarefa: "7.0",
  },
  { caminho: "/perfil", titulo: "Meu perfil", icone: "◎", grupo: "preferencias", tarefa: "5.0" },
  {
    caminho: "/configuracoes",
    titulo: "Configurações",
    icone: "⚙",
    grupo: "preferencias",
    tarefa: "8.0",
  },
  { caminho: "/ajustar-vaga", titulo: "Ajustar para uma vaga", tarefa: "6.0" },
  { caminho: "/analisar-ats", titulo: "Analisar ATS", tarefa: "6.0" },
];

export const GRUPOS_MENU = [
  { id: "principal", rotulo: "Menu principal" },
  { id: "preferencias", rotulo: "Preferências" },
] as const;
