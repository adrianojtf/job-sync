import { useMutation } from "@tanstack/react-query";
import { useApiClient } from "../../api/api-client-context";
import type {
  AdaptarCurriculoEntrada,
  AnalisarAtsEntrada,
  GerarPdfCurriculoRevisadoEntrada,
} from "../../api/tipos";

interface ComCurriculo<T> {
  curriculoId: string;
  dados: T;
}

/**
 * Casos de uso da tela Ajustar para uma vaga: avaliar a vaga, gerar o rascunho adaptado,
 * gerar o PDF do rascunho revisado (JOB-0033), ATS e carta (RF6.2–RF6.4).
 */
export function useAjustarVaga() {
  const api = useApiClient();
  return {
    avaliar: useMutation({ mutationFn: (descricao: string) => api.avaliarVaga(descricao) }),
    gerarRascunho: useMutation({
      mutationFn: ({ curriculoId, dados }: ComCurriculo<AdaptarCurriculoEntrada>) =>
        api.gerarRascunhoAdaptado(curriculoId, dados),
    }),
    gerarPdf: useMutation({
      mutationFn: (dados: GerarPdfCurriculoRevisadoEntrada) => api.gerarPdfCurriculoRevisado(dados),
    }),
    ats: useMutation({
      mutationFn: ({ curriculoId, dados }: ComCurriculo<AnalisarAtsEntrada>) =>
        api.analisarAts(curriculoId, dados),
    }),
    carta: useMutation({ mutationFn: (dados: AdaptarCurriculoEntrada) => api.gerarCarta(dados) }),
  };
}
