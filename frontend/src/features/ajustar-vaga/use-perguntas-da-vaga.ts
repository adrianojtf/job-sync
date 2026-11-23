import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "../../api/api-client-context";
import type { ConquistaRascunhoEntrada } from "../../api/tipos";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";
import { chavePerfilEstruturado } from "../perfil/use-perfil-estruturado";

/** Casos de uso da etapa "Perguntas sobre a vaga" (JOB-0043). */
export function usePerguntasDaVaga() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  const queryClient = useQueryClient();
  return {
    // A IA escreve a conquista a partir do caso; nada é salvo até o candidato aprovar.
    redigirConquista: useMutation({
      mutationFn: (dados: Omit<ConquistaRascunhoEntrada, "perfil_identificador">) =>
        api.redigirConquistaDeLacuna({ ...dados, perfil_identificador: perfil }),
    }),
    // A conquista aprovada entra no banco da experiência: o perfil em cache deixa de valer.
    aprovarConquista: useMutation({
      mutationFn: ({ experienciaIndice, texto }: { experienciaIndice: number; texto: string }) =>
        api.adicionarConquistaAExperiencia(perfil, experienciaIndice, texto),
      onSuccess: () => queryClient.invalidateQueries({ queryKey: chavePerfilEstruturado(perfil) }),
    }),
  };
}
