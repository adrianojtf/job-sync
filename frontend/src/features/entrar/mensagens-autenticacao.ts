import { ApiError } from "../../api/api-error";

/** Códigos fixos que o backend devolve em /entrar?erro=<codigo> após o login com um provedor. */
const ERROS_DE_PROVEDOR: Record<string, string> = {
  acesso_negado: "Você cancelou o login com o Google. Tente de novo quando quiser.",
  estado_invalido: "Não foi possível concluir o login. Tente novamente.",
  email_nao_verificado:
    "O Google não confirmou o e-mail dessa conta. Use uma conta com e-mail verificado.",
  provedor_indisponivel: "O Google está indisponível agora. Tente novamente em instantes.",
};

const ERRO_DE_PROVEDOR_DESCONHECIDO = "Não foi possível entrar. Tente novamente.";

export function mensagemDoErroDeProvedor(codigo: string | null): string | undefined {
  if (!codigo) return undefined;
  return ERROS_DE_PROVEDOR[codigo] ?? ERRO_DE_PROVEDOR_DESCONHECIDO;
}

export function mensagemDoErroDeLogin(erro: unknown): string {
  if (erro instanceof ApiError) {
    if (erro.status === 401) {
      return "E-mail ou senha incorretos. Se você acabou de se cadastrar, confirme o e-mail pelo link que enviamos.";
    }
    if (erro.status === 429) return "Muitas tentativas. Tente novamente em alguns minutos.";
    if (erro.status === 0) return erro.message;
  }
  return "Não foi possível entrar agora. Tente novamente.";
}
