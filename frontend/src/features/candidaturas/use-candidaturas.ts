import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "../../api/api-client-context";
import type { CandidaturasPorStatus, StatusCandidatura } from "../../api/tipos";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";
import { aplicarMovimento } from "./movimento";

export const chaveCandidaturas = (perfil: string) => ["candidaturas", perfil] as const;

const CHAVE_MOVER = ["candidaturas", "mover"] as const;

export function useCandidaturas() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  return useQuery({
    queryKey: chaveCandidaturas(perfil),
    queryFn: () => api.listarCandidaturas(perfil),
  });
}

interface EntradaMover {
  id: string;
  novoStatus: StatusCandidatura;
  /** Índice na coluna de destino; ausente = topo. */
  posicao?: number;
}

/**
 * RF10.2, RF3 — move a candidatura de coluna e/ou posição.
 *
 * Atualização otimista: o quadro muda no cache na hora e volta ao estado anterior se a API falhar.
 * Os movimentos rodam um de cada vez (mesmo `scope`), para a ordem gravada ser a ordem feita.
 */
export function useMoverCandidatura() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  const queryClient = useQueryClient();
  const chave = chaveCandidaturas(perfil);

  return useMutation({
    mutationKey: CHAVE_MOVER,
    scope: { id: "mover-candidatura" },
    mutationFn: ({ id, novoStatus, posicao }: EntradaMover) =>
      api.moverCandidatura(id, novoStatus, posicao),
    onMutate: async ({ id, novoStatus, posicao }) => {
      await queryClient.cancelQueries({ queryKey: chave });
      const anterior = queryClient.getQueryData<CandidaturasPorStatus>(chave);
      if (anterior) {
        queryClient.setQueryData(
          chave,
          aplicarMovimento(anterior, id, { status: novoStatus, posicao: posicao ?? 0 }),
        );
      }
      return { anterior };
    },
    onError: (_erro, _entrada, contexto) => {
      if (contexto?.anterior) queryClient.setQueryData(chave, contexto.anterior);
    },
    onSettled: () => {
      if (queryClient.isMutating({ mutationKey: CHAVE_MOVER }) <= 1) {
        return queryClient.invalidateQueries({ queryKey: chave });
      }
    },
  });
}
