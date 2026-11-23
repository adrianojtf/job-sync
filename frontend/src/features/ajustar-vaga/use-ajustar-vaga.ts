import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "../../api/api-client-context";
import type {
  AdaptarCurriculoEntrada,
  AnalisarAtsEntrada,
  ConfirmarCandidaturaEntrada,
  RascunhoCurriculoAdaptado,
  SalvarCurriculoAdaptadoEntrada,
} from "../../api/tipos";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";
import { chaveCandidaturas } from "../candidaturas/use-candidaturas";
import { chaveCurriculos } from "../curriculos/use-curriculos";
import { chaveCurriculosAdaptados } from "../curriculos-adaptados/use-curriculos-adaptados";
import { chaveVagas } from "../vagas-salvas/use-vagas-salvas";

interface ComCurriculo<T> {
  curriculoId: string;
  dados: T;
}

/**
 * Casos de uso da tela Ajustar para uma vaga: avaliar a vaga, gerar o rascunho adaptado,
 * salvar o currículo adaptado revisado e gerar o PDF dele (JOB-0033, JOB-0041), editá-lo depois,
 * ATS e carta (RF6.2–RF6.4) e confirmar a candidatura com o PDF gerado (JOB-0037).
 */
export function useAjustarVaga() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  const queryClient = useQueryClient();
  return {
    avaliar: useMutation({ mutationFn: (descricao: string) => api.avaliarVaga(descricao) }),
    gerarRascunho: useMutation({
      mutationFn: ({ curriculoId, dados }: ComCurriculo<AdaptarCurriculoEntrada>) =>
        api.gerarRascunhoAdaptado(curriculoId, dados),
    }),
    salvarAdaptado: useMutation({
      mutationFn: (dados: Omit<SalvarCurriculoAdaptadoEntrada, "perfil_identificador">) =>
        api.salvarCurriculoAdaptado({ ...dados, perfil_identificador: perfil }),
      onSuccess: () =>
        queryClient.invalidateQueries({ queryKey: chaveCurriculosAdaptados(perfil) }),
    }),
    // A edição também troca o PDF da candidatura já confirmada: a biblioteca de PDFs muda.
    atualizarAdaptado: useMutation({
      mutationFn: ({ id, rascunho }: { id: string; rascunho: RascunhoCurriculoAdaptado }) =>
        api.atualizarCurriculoAdaptado(id, { perfil_identificador: perfil, rascunho }),
      onSuccess: () =>
        Promise.all([
          queryClient.invalidateQueries({ queryKey: chaveCurriculosAdaptados(perfil) }),
          queryClient.invalidateQueries({ queryKey: chaveCurriculos(perfil) }),
        ]),
    }),
    ats: useMutation({
      mutationFn: ({ curriculoId, dados }: ComCurriculo<AnalisarAtsEntrada>) =>
        api.analisarAts(curriculoId, dados),
    }),
    carta: useMutation({ mutationFn: (dados: AdaptarCurriculoEntrada) => api.gerarCarta(dados) }),
    // O PDF vai para a biblioteca e a vaga vira candidatura: as três listas do perfil mudam.
    confirmarCandidatura: useMutation({
      mutationFn: (dados: Omit<ConfirmarCandidaturaEntrada, "perfil_identificador">) =>
        api.confirmarCandidaturaAjustada({ ...dados, perfil_identificador: perfil }),
      onSuccess: () =>
        Promise.all([
          queryClient.invalidateQueries({ queryKey: chaveCandidaturas(perfil) }),
          queryClient.invalidateQueries({ queryKey: chaveCurriculos(perfil) }),
          queryClient.invalidateQueries({ queryKey: chaveVagas(perfil) }),
        ]),
    }),
  };
}
