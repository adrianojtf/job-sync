import { useWatch, type UseFormReturn } from "react-hook-form";
import { useApiClient } from "../../api/api-client-context";
import type { ContextoVaga, SugestaoExperienciaAdaptada as Sugestao } from "../../api/tipos";
import { EXPERIENCIA_ADAPTADA_VAZIA } from "../../shared/formulario-curriculo/campos-curriculo";
import { SugestaoIA } from "../../shared/formulario-curriculo/SugestaoIA";
import {
  conquistasParaLinhas,
  descricaoParaAvaliacao,
  formularioParaExperienciaAdaptada,
  type FormularioRevisao,
} from "./formulario-revisao";

interface Props {
  form: UseFormReturn<FormularioRevisao>;
  indice: number;
  /** Vaga usada na adaptação: orienta a sugestão. */
  contextoVaga: ContextoVaga;
}

const descreverSugestao = (sugestao: Sugestao) =>
  [
    ...sugestao.conquistas.map((conquista) => `- ${conquista}`),
    ...(sugestao.contexto.trim() === "" ? [] : [`Contexto: ${sugestao.contexto.trim()}`]),
  ].join("\n");

/**
 * "Sugestões de IA" de uma experiência da revisão (JOB-0035): a IA refina as conquistas e o
 * contexto atuais do usuário para a vaga, e aplicar atualiza os dois campos de uma vez.
 */
export function SugestaoExperienciaAdaptada({ form, indice, contextoVaga }: Props) {
  const api = useApiClient();
  const experiencia =
    useWatch({ control: form.control, name: `experiencias.${indice}` }) ??
    EXPERIENCIA_ADAPTADA_VAZIA;
  const campoConquistas = `experiencias.${indice}.conquistas` as const;
  const campoContexto = `experiencias.${indice}.contexto` as const;

  return (
    <SugestaoIA<Sugestao>
      rotuloBloco={`experiência ${indice + 1}`}
      textoAtual={descricaoParaAvaliacao(experiencia)}
      sugerir={async (_texto, refino) => {
        const sugestao = await api.sugerirAjusteExperienciaAdaptada({
          experiencia: formularioParaExperienciaAdaptada(form.getValues(`experiencias.${indice}`)),
          contexto_vaga: contextoVaga,
          refino,
        });
        return { valor: sugestao, foco: sugestao.foco };
      }}
      descrever={descreverSugestao}
      aplicar={(sugestao) => {
        const opcoes = { shouldDirty: true, shouldTouch: true };
        form.setValue(campoConquistas, conquistasParaLinhas(sugestao.conquistas), opcoes);
        form.setValue(campoContexto, sugestao.contexto, opcoes);
      }}
      focarCampo={() => form.setFocus(campoConquistas)}
    />
  );
}
