import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useMemo, type ReactNode } from "react";
import { useApiClient } from "../../api/api-client-context";
import type { Usuario } from "../../api/tipos";
import { CHAVE_QUERY_SESSAO, SessaoContext } from "./sessao-context";

/**
 * Expõe o usuário da sessão. A fonte da verdade é o servidor (cookie HttpOnly): o navegador não
 * guarda identificador nenhum em localStorage.
 */
export function SessaoProvider({ children }: { children: ReactNode }) {
  const api = useApiClient();
  const queryClient = useQueryClient();
  const consulta = useQuery({
    queryKey: CHAVE_QUERY_SESSAO,
    queryFn: () => api.obterUsuarioAtual(),
    staleTime: Infinity,
    retry: false,
    refetchOnWindowFocus: false,
  });
  const usuario = consulta.data ?? null;

  const entrar = useCallback(
    (novo: Usuario) => {
      queryClient.setQueryData(CHAVE_QUERY_SESSAO, novo);
    },
    [queryClient],
  );

  const sair = useCallback(async () => {
    try {
      await api.sair();
    } finally {
      // Dados de quem saiu não podem ficar em memória para a próxima pessoa.
      queryClient.removeQueries({ predicate: (consulta) => consulta.queryKey[0] !== "sessao" });
      queryClient.setQueryData(CHAVE_QUERY_SESSAO, null);
    }
  }, [api, queryClient]);

  const valor = useMemo(
    () => ({
      usuario,
      perfil: usuario?.perfil_identificador ?? null,
      carregando: consulta.isPending,
      entrar,
      sair,
    }),
    [usuario, consulta.isPending, entrar, sair],
  );
  return <SessaoContext.Provider value={valor}>{children}</SessaoContext.Provider>;
}
