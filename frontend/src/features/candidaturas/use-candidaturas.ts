import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "../../api/api-client-context";
import type { StatusCandidatura } from "../../api/tipos";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";

export const chaveCandidaturas = (perfil: string) => ["candidaturas", perfil] as const;

export function useCandidaturas() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  return useQuery({
    queryKey: chaveCandidaturas(perfil),
    queryFn: () => api.listarCandidaturas(perfil),
  });
}

/** RF10.2 — move a candidatura de etapa e recarrega o quadro. */
export function useMoverCandidatura() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, novoStatus }: { id: string; novoStatus: StatusCandidatura }) =>
      api.moverCandidatura(id, novoStatus),
    onSettled: () => queryClient.invalidateQueries({ queryKey: chaveCandidaturas(perfil) }),
  });
}
