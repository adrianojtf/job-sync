import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "../../api/api-client-context";
import type { SalvarCurriculoEntrada } from "../../api/tipos";
import { base64ParaBlob, baixarArquivo } from "../../shared/arquivos/arquivos";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";

/** Limite de currículos por perfil definido no backend (JOB-0004). */
export const LIMITE_CURRICULOS = 10;

export const chaveCurriculos = (perfil: string) => ["curriculos", perfil] as const;

export function useCurriculos() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  return useQuery({
    queryKey: chaveCurriculos(perfil),
    queryFn: () => api.listarCurriculos(perfil),
  });
}

export function useEnviarCurriculo() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (dados: Omit<SalvarCurriculoEntrada, "perfil_identificador">) =>
      api.salvarCurriculo({ ...dados, perfil_identificador: perfil }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: chaveCurriculos(perfil) }),
  });
}

export function useRemoverCurriculo() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.removerCurriculo(id, perfil),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: chaveCurriculos(perfil) }),
  });
}

export function useBaixarCurriculo() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  return useMutation({
    mutationFn: (id: string) => api.baixarCurriculo(id, perfil),
    onSuccess: (conteudo) => {
      const nome = conteudo.nome_referencia.toLowerCase().endsWith(".pdf")
        ? conteudo.nome_referencia
        : `${conteudo.nome_referencia}.pdf`;
      baixarArquivo(base64ParaBlob(conteudo.pdf_base64), nome);
    },
  });
}
