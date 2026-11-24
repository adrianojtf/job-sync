import { useWatch, type UseFormReturn } from "react-hook-form";
import { useApiClient } from "../../api/api-client-context";
import type { SugestaoExperiencia } from "../../api/tipos";
import { linhasParaTexto } from "../../shared/formulario-curriculo/linhas";
import { SugestaoIA } from "../../shared/formulario-curriculo/SugestaoIA";
import {
  EXPERIENCIA_PERFIL_VAZIA,
  experienciaParaIA,
  textoDosBlocos,
  type ConquistaFormulario,
  type FormularioPerfil,
} from "./formulario-perfil";

interface Props {
  form: UseFormReturn<FormularioPerfil>;
  indice: number;
}

const descreverSugestao = (sugestao: SugestaoExperiencia) =>
  [
    ...(sugestao.conquistas ?? []).map((conquista) => `- ${conquista}`),
    ...((sugestao.contexto ?? "").trim() === "" ? [] : [`Contexto: ${sugestao.contexto?.trim()}`]),
    ...((sugestao.responsabilidades ?? []).length > 0
      ? [`Responsabilidades: ${(sugestao.responsabilidades ?? []).join("; ")}`]
      : []),
    ...((sugestao.skills ?? []).length > 0
      ? [`Skills: ${(sugestao.skills ?? []).join(", ")}`]
      : []),
  ].join("\n");

/** Mantém a origem das conquistas que a IA devolveu iguais às cadastradas; as novas são manuais. */
function conquistasSugeridas(
  sugeridas: string[],
  atuais: ConquistaFormulario[],
): ConquistaFormulario[] {
  return sugeridas.map((texto) => ({
    texto,
    origem: atuais.find((atual) => atual.texto.trim() === texto)?.origem ?? "MANUAL",
  }));
}

/**
 * "Sugestões de IA" dos quatro blocos de uma experiência do perfil (JOB-0045), sem vaga-alvo:
 * a IA melhora a escrita do que o usuário já tem, e aplicar atualiza os quatro campos de uma vez.
 */
export function SugestaoBlocosDaExperiencia({ form, indice }: Props) {
  const api = useApiClient();
  const experiencia =
    useWatch({ control: form.control, name: `experiencias.${indice}` }) ?? EXPERIENCIA_PERFIL_VAZIA;
  const base = `experiencias.${indice}` as const;

  return (
    <SugestaoIA<SugestaoExperiencia>
      rotuloBloco={`experiência ${indice + 1}`}
      textoAtual={textoDosBlocos(experiencia)}
      sugerir={async (_texto, refino) => {
        const sugestao = await api.sugerirAjusteExperiencia({
          experiencia: experienciaParaIA(form.getValues(base)),
          refino,
        });
        return { valor: sugestao, foco: sugestao.foco };
      }}
      descrever={descreverSugestao}
      aplicar={(sugestao) => {
        const opcoes = { shouldDirty: true, shouldTouch: true };
        form.setValue(`${base}.contexto`, sugestao.contexto ?? "", opcoes);
        form.setValue(
          `${base}.responsabilidades`,
          linhasParaTexto(sugestao.responsabilidades ?? []),
          opcoes,
        );
        form.setValue(
          `${base}.conquistas`,
          conquistasSugeridas(
            sugestao.conquistas ?? [],
            form.getValues(`${base}.conquistas`) ?? [],
          ),
          opcoes,
        );
        form.setValue(`${base}.skills`, sugestao.skills ?? [], opcoes);
      }}
      focarCampo={() => form.setFocus(`${base}.contexto`)}
    />
  );
}
