import { useApiClient } from "../../api/api-client-context";
import type { ContextoVaga, SugerirAjusteSecaoEntrada } from "../../api/tipos";
import type { ExperienciaFormulario } from "./campos-curriculo";

type SecaoSugestao = SugerirAjusteSecaoEntrada["secao"];

/**
 * Funções de sugestão de IA para os blocos do formulário de currículo (JOB-0034). Com `contexto`
 * a IA adapta o texto à vaga (revisão do currículo adaptado); sem ele, só melhora a escrita
 * (tela Meu perfil). Quem usa só decide o contexto: o encaixe no formulário é o mesmo.
 */
export function useSugestoes(contexto?: ContextoVaga) {
  const api = useApiClient();
  const contexto_vaga = contexto ?? undefined;
  return {
    /** Sugestão para uma seção de texto (resumo, tecnologias, experiências em texto). */
    secao:
      (tipo: SecaoSugestao["tipo"], titulo: string) =>
      async (conteudo: string): Promise<string> =>
        (await api.sugerirAjusteSecao({ secao: { tipo, titulo, conteudo }, contexto_vaga }))
          .conteudo_sugerido,
    /** Sugestão para uma experiência; cargo, empresa e período são lidos na hora do pedido. */
    experiencia:
      (obterExperiencia: () => ExperienciaFormulario) =>
      async (descricao: string): Promise<string> =>
        (
          await api.sugerirAjusteExperiencia({
            experiencia: { ...obterExperiencia(), descricao },
            contexto_vaga,
          })
        ).descricao_sugerida,
  };
}
