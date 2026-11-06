import { useSessao } from "./use-sessao";

/** Identificador do perfil logado. Só usar dentro de rotas protegidas. */
export function usePerfilAtivo(): string {
  const { perfil } = useSessao();
  if (!perfil) {
    throw new Error("usePerfilAtivo exige sessão ativa (use dentro de RotaProtegida).");
  }
  return perfil;
}
