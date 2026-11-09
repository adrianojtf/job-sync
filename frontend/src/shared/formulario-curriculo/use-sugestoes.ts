import { useApiClient } from "../../api/api-client-context";
import type { ContextoVaga, SugerirAjusteSecaoEntrada } from "../../api/tipos";
import type { ExperienciaFormulario } from "./campos-curriculo";
import type { SugerirComRefino } from "./SugestaoIA";

type SecaoSugestao = SugerirAjusteSecaoEntrada["secao"];

/**
 * Funções de sugestão de IA para os blocos de texto do formulário de currículo (JOB-0034). Com
 * `contexto` a IA adapta a seção à vaga (revisão do currículo adaptado); sem ele, só melhora a
 * escrita (tela Meu perfil). Quem usa só decide o contexto: o encaixe no formulário é o mesmo.
 * Cada pedido leva o refino do bloco (tentativa e sugestões anteriores) e devolve o foco usado.
 */
export function useSugestoes(contexto?: ContextoVaga) {
  const api = useApiClient();
  return {
    /** Sugestão para uma seção de texto (resumo, tecnologias, experiências em texto). */
    secao:
      (tipo: SecaoSugestao["tipo"], titulo: string): SugerirComRefino<string> =>
      async (conteudo, refino) => {
        const resposta = await api.sugerirAjusteSecao({
          secao: { tipo, titulo, conteudo },
          contexto_vaga: contexto,
          refino,
        });
        return { valor: resposta.conteudo_sugerido, foco: resposta.foco };
      },
    /**
     * Sugestão para a descrição de uma experiência do perfil, sempre sem vaga; cargo, empresa e
     * período são lidos na hora do pedido. Na revisão, as experiências usam conquistas e contexto.
     */
    experiencia:
      (obterExperiencia: () => ExperienciaFormulario): SugerirComRefino<string> =>
      async (descricao, refino) => {
        const resposta = await api.sugerirAjusteExperiencia({
          experiencia: { ...obterExperiencia(), descricao },
          refino,
        });
        return { valor: resposta.descricao_sugerida, foco: resposta.foco };
      },
  };
}
