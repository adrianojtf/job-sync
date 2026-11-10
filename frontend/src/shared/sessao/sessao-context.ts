import { createContext } from "react";
import type { Usuario } from "../../api/tipos";

/** Chave da consulta que guarda o usuário da sessão; `null` significa "sem sessão". */
export const CHAVE_QUERY_SESSAO = ["sessao"] as const;

export interface Sessao {
  usuario: Usuario | null;
  /** Identificador do perfil dono dos dados; `null` sem sessão. */
  perfil: string | null;
  /** Verdadeiro enquanto o servidor ainda não respondeu se há sessão. */
  carregando: boolean;
  /** Registra o usuário que acabou de entrar. */
  entrar: (usuario: Usuario) => void;
  /** Encerra a sessão no servidor e descarta os dados em memória. */
  sair: () => Promise<void>;
}

export const SessaoContext = createContext<Sessao | null>(null);
