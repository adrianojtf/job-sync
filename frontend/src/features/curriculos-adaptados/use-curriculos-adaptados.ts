import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "../../api/api-client-context";
import type { RascunhoCurriculoAdaptado } from "../../api/tipos";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";
import { chaveCurriculos } from "../curriculos/use-curriculos";

/** Chaves das consultas de currículos adaptados do perfil (JOB-0041). */
export const chaveCurriculosAdaptados = (perfil: string) =>
  ["curriculos-adaptados", perfil] as const;
const chaveCurriculoAdaptado = (perfil: string, id: string) =>
  ["curriculo-adaptado", perfil, id] as const;

export function useCurriculosAdaptados() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  return useQuery({
    queryKey: chaveCurriculosAdaptados(perfil),
    queryFn: () => api.listarCurriculosAdaptados(perfil),
  });
}

export function useCurriculoAdaptado(id: string) {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  return useQuery({
    queryKey: chaveCurriculoAdaptado(perfil, id),
    queryFn: () => api.obterCurriculoAdaptado(id, perfil),
  });
}

/** Salva a edição: o PDF regenerado também troca o da candidatura, então a biblioteca muda. */
export function useAtualizarCurriculoAdaptado(id: string) {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (rascunho: RascunhoCurriculoAdaptado) =>
      api.atualizarCurriculoAdaptado(id, { perfil_identificador: perfil, rascunho }),
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: chaveCurriculosAdaptados(perfil) }),
        queryClient.invalidateQueries({ queryKey: chaveCurriculoAdaptado(perfil, id) }),
        queryClient.invalidateQueries({ queryKey: chaveCurriculos(perfil) }),
      ]),
  });
}
