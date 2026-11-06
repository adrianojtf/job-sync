import { useMutation } from "@tanstack/react-query";
import { useApiClient } from "../../api/api-client-context";
import type { CandidatarVagaExternaEntrada, VagaDescoberta } from "../../api/tipos";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";

export interface Busca {
  termo: string;
  curriculoId: string;
  diasMaximo: number | null;
}

export interface ResultadoBusca {
  vagas: VagaDescoberta[];
  /** PDF usado no cálculo da nota; reaproveitado em "Candidatar" quando não há currículo mestre. */
  pdfReferencia: string;
}

/** RF9.1–RF9.2 — busca nas fontes externas e ordena pela nota de compatibilidade. */
export function useDescobrirVagas() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  return useMutation({
    mutationFn: async ({ termo, curriculoId, diasMaximo }: Busca): Promise<ResultadoBusca> => {
      const { pdf_base64 } = await api.baixarCurriculo(curriculoId, perfil);
      const vagas = await api.descobrirVagas({ termo, pdf_base64, dias_maximo: diasMaximo });
      return { vagas: [...vagas].sort((a, b) => b.nota - a.nota), pdfReferencia: pdf_base64 };
    },
  });
}

/** RF9.3 — gera PDF adaptado, nota e carta para a vaga; não preenche formulários de terceiros. */
export function useCandidatarVagaExterna() {
  const api = useApiClient();
  return useMutation({
    mutationFn: (dados: CandidatarVagaExternaEntrada) => api.candidatarVagaExterna(dados),
  });
}
