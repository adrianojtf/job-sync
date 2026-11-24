import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useApiClient } from "../../api/api-client-context";
import type { ApiError } from "../../api/api-error";
import type { DadosVaga, ExtracaoVagaEntrada } from "../../api/tipos";
import { resumirLeitura, type CampoIdentificacao, type ResumoDaLeitura } from "./resumo-da-leitura";

/**
 * Lê os dados de uma vaga a partir de um link ou de um texto (JOB-0047).
 * O resultado é um rascunho: quem usa o hook decide o que preencher em `aoLer`.
 */
export function useLeituraDeVaga(aoLer: (dados: DadosVaga) => void, campos?: CampoIdentificacao[]) {
  const api = useApiClient();
  const mutacao = useMutation<DadosVaga, ApiError, ExtracaoVagaEntrada>({
    mutationFn: (entrada) => api.extrairDadosVaga(entrada),
  });
  const [resumo, setResumo] = useState<ResumoDaLeitura | null>(null);

  const ler = (entrada: ExtracaoVagaEntrada) => {
    setResumo(null);
    mutacao.mutate(entrada, {
      onSuccess: (dados) => {
        setResumo(resumirLeitura(dados, campos));
        aoLer(dados);
      },
    });
  };

  // A API não interrompe a leitura em andamento, mas depois de cancelar o resultado é descartado.
  const cancelar = () => {
    mutacao.reset();
    setResumo(null);
  };

  return { ler, cancelar, lendo: mutacao.isPending, erro: mutacao.error?.message, resumo };
}
