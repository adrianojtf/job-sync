import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "../../api/api-client-context";
import type { CriarCandidaturaEntrada } from "../../api/tipos";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";
import { chaveCandidaturas } from "../candidaturas/use-candidaturas";

export const chaveVagas = (perfil: string) => ["vagas", perfil] as const;

/** Vagas capturadas (extensão ou coladas) ainda não convertidas em candidatura. */
export function useVagasSalvas() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  return useQuery({ queryKey: chaveVagas(perfil), queryFn: () => api.listarVagas(perfil) });
}

/** RF8.2 — registra uma vaga colada manualmente, ou lida de um link (JOB-0047). */
export function useColarVaga() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (dados: {
      texto_descricao: string;
      url_origem: string | null;
      cargo?: string;
      empresa?: string;
      local?: string;
    }) => api.capturarVaga({ perfil_identificador: perfil, ...dados }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: chaveVagas(perfil) }),
  });
}

export function useAvaliarDescricaoVaga() {
  const api = useApiClient();
  return useMutation({ mutationFn: (descricao: string) => api.avaliarVaga(descricao) });
}

/** RF8.4 — a vaga vira candidatura em Aplicado e sai da lista de vagas salvas. */
export function useCriarCandidatura() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (dados: Omit<CriarCandidaturaEntrada, "perfil_identificador">) =>
      api.criarCandidatura({ perfil_identificador: perfil, ...dados }),
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: chaveVagas(perfil) }),
        queryClient.invalidateQueries({ queryKey: chaveCandidaturas(perfil) }),
      ]),
  });
}
