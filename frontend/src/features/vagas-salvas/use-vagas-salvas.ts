import { useQuery } from "@tanstack/react-query";
import { useApiClient } from "../../api/api-client-context";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";

export const chaveVagas = (perfil: string) => ["vagas", perfil] as const;

/** Vagas capturadas (extensão ou coladas) ainda não convertidas em candidatura. */
export function useVagasSalvas() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  return useQuery({ queryKey: chaveVagas(perfil), queryFn: () => api.listarVagas(perfil) });
}
