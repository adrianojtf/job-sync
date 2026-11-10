import type { Usuario } from "../api/tipos";

/** Usuário simulado cujo perfil é o identificador informado (nome igual, para aparecer no menu). */
export function usuarioDeTeste(perfil: string): Usuario {
  return {
    id: `id-${perfil}`,
    email: `${perfil}@exemplo.com`,
    nome: perfil,
    perfil_identificador: perfil,
  };
}
