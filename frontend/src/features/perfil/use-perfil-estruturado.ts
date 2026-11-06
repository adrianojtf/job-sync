import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "../../api/api-client-context";
import type { AvaliarExperienciaEntrada, PerfilEstruturadoEntrada } from "../../api/tipos";
import { arquivoParaBase64 } from "../../shared/arquivos/arquivos";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";

export const chavePerfilEstruturado = (perfil: string) => ["perfil-estruturado", perfil] as const;

export function usePerfilEstruturado() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  return useQuery({
    queryKey: chavePerfilEstruturado(perfil),
    queryFn: () => api.buscarPerfilEstruturado(perfil),
  });
}

/** Cria com POST quando o perfil ainda não existe e atualiza com PUT quando já existe (RF4.3). */
export function useSalvarPerfilEstruturado(existe: boolean) {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (entrada: PerfilEstruturadoEntrada) =>
      existe ? api.atualizarPerfilEstruturado(entrada) : api.salvarPerfilEstruturado(entrada),
    onSuccess: (salvo) => queryClient.setQueryData(chavePerfilEstruturado(perfil), salvo),
  });
}

export type OrigemImportacao =
  | { tipo: "arquivo"; arquivo: File }
  | { tipo: "biblioteca"; curriculoId: string };

/** Extrai um rascunho de perfil de um PDF (novo ou da biblioteca) sem salvar nada (RF4.2). */
export function useImportarPerfil() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  return useMutation({
    mutationFn: async (origem: OrigemImportacao) => {
      const pdfBase64 =
        origem.tipo === "arquivo"
          ? await arquivoParaBase64(origem.arquivo)
          : (await api.baixarCurriculo(origem.curriculoId, perfil)).pdf_base64;
      return api.importarPerfilDePdf(pdfBase64);
    },
  });
}

export function useAvaliarExperiencia() {
  const api = useApiClient();
  return useMutation({
    mutationFn: (dados: AvaliarExperienciaEntrada) => api.avaliarExperiencia(dados),
  });
}
