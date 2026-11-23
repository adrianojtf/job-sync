import { useApiClient } from "../../api/api-client-context";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";
import { useCurriculos } from "../curriculos/use-curriculos";
import { useCurriculosAdaptados } from "../curriculos-adaptados/use-curriculos-adaptados";
import { usePerfilEstruturado } from "../perfil/use-perfil-estruturado";

export const FONTE_PERFIL = "perfil";
const PREFIXO_ADAPTADO = "adaptado:";
/** O backend ignora o id do caminho quando a fonte é o perfil estruturado ou um adaptado. */
const ID_CAMINHO_PERFIL = "perfil-estruturado";
const ID_CAMINHO_ADAPTADO = "adaptado-base";

export interface FonteResolvida {
  curriculoId: string;
  perfil_identificador?: string;
  pdf_base64?: string;
  curriculo_adaptado_id?: string;
}

/**
 * Fontes de currículo para adaptar e analisar: o perfil estruturado (preferido, JOB-0009), um
 * currículo adaptado salvo (JOB-0041, sem alterar o original) ou um PDF da biblioteca.
 */
export function useFontesCurriculo() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  const perfilEstruturado = usePerfilEstruturado();
  const curriculos = useCurriculos();
  const adaptados = useCurriculosAdaptados();

  const opcoes = [
    ...(perfilEstruturado.data
      ? [{ valor: FONTE_PERFIL, rotulo: "Meu perfil (currículo mestre)" }]
      : []),
    ...(adaptados.data ?? []).map((adaptado) => ({
      valor: `${PREFIXO_ADAPTADO}${adaptado.id}`,
      rotulo: `Adaptado: ${adaptado.nome_referencia}`,
    })),
    ...(curriculos.data ?? []).map((curriculo) => ({
      valor: curriculo.id,
      rotulo: curriculo.nome_referencia,
    })),
  ];

  const resolver = async (fonte: string): Promise<FonteResolvida> => {
    if (fonte === FONTE_PERFIL)
      return { curriculoId: ID_CAMINHO_PERFIL, perfil_identificador: perfil };
    if (fonte.startsWith(PREFIXO_ADAPTADO)) {
      return {
        curriculoId: ID_CAMINHO_ADAPTADO,
        perfil_identificador: perfil,
        curriculo_adaptado_id: fonte.slice(PREFIXO_ADAPTADO.length),
      };
    }
    const conteudo = await api.baixarCurriculo(fonte, perfil);
    return { curriculoId: fonte, pdf_base64: conteudo.pdf_base64 };
  };

  const carregando = perfilEstruturado.isPending || curriculos.isPending || adaptados.isPending;
  return {
    opcoes,
    carregando,
    // O padrão só existe com as duas consultas prontas: se a lista de PDFs chegasse primeiro, o
    // formulário travaria num PDF e nunca voltaria ao perfil mestre, que é a fonte preferida.
    padrao: carregando ? "" : (opcoes[0]?.valor ?? ""),
    resolver,
  };
}
