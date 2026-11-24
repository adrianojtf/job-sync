import { useState } from "react";
import { Controller, useWatch, type UseFormReturn } from "react-hook-form";
import { EditorTags } from "../../shared/formulario-curriculo/EditorTags";
import { SugestaoCampo } from "../../shared/formulario-curriculo/SugestaoCampo";
import { useSugestoes } from "../../shared/formulario-curriculo/use-sugestoes";
import { Aviso } from "../../shared/ui/Aviso";
import { Field } from "../../shared/ui/Field";
import { ConquistasDaExperiencia } from "./ConquistasDaExperiencia";
import estilos from "./ConquistasDaExperiencia.module.css";
import {
  EXPERIENCIA_PERFIL_VAZIA,
  ehLegada,
  experienciaDaDescricao,
  type FormularioPerfil,
} from "./formulario-perfil";
import { SugestaoBlocosDaExperiencia } from "./SugestaoBlocosDaExperiencia";

interface Props {
  form: UseFormReturn<FormularioPerfil>;
  indice: number;
}

/**
 * Os quatro blocos de uma experiência do perfil (JOB-0045): contexto, responsabilidades,
 * principais realizações (o banco de conquistas) e skills em tags. A descrição em texto livre só
 * aparece nos perfis antigos, até o usuário estruturá-los.
 */
export function BlocosDaExperiencia({ form, indice }: Props) {
  const [anuncio, setAnuncio] = useState("");
  // Sem vaga-alvo aqui: a IA só melhora a escrita do texto (JOB-0034).
  const sugestoes = useSugestoes();
  const base = `experiencias.${indice}` as const;
  const experiencia = useWatch({ control: form.control, name: base }) ?? EXPERIENCIA_PERFIL_VAZIA;
  const numero = indice + 1;
  const legada = ehLegada(experiencia);
  const temDescricao = experiencia.descricao.trim() !== "";

  return (
    <>
      {temDescricao && (
        <>
          {legada && (
            <Aviso>
              Esta experiência ainda usa a descrição em texto livre. Use “Estruturar experiências”
              para separá-la em contexto, responsabilidades, realizações e skills (salve antes as
              alterações pendentes).
            </Aviso>
          )}
          <Field tipoCampo="textarea" rotulo="Descrição" {...form.register(`${base}.descricao`)} />
          {legada && (
            <SugestaoCampo
              form={form}
              campo={`${base}.descricao`}
              rotuloBloco={`experiência ${numero}`}
              sugerir={sugestoes.experiencia(() => experienciaDaDescricao(form.getValues(base)))}
            />
          )}
        </>
      )}
      <Field
        tipoCampo="textarea"
        rotulo="Contexto"
        ajuda="Empresa, área e seu papel, em poucas frases."
        {...form.register(`${base}.contexto`)}
      />
      <Field
        tipoCampo="textarea"
        rotulo="Principais responsabilidades"
        ajuda="Uma responsabilidade por linha."
        {...form.register(`${base}.responsabilidades`)}
      />
      <ConquistasDaExperiencia form={form} indice={indice} />
      <div
        role="group"
        aria-label={`Skills da experiência ${numero}`}
        className={estilos.conquistas}
      >
        <h4 className={estilos.titulo}>Skills</h4>
        <p className={estilos.descricao}>
          Tecnologias e competências usadas nesta experiência. As que faltarem nas tecnologias
          gerais entram nelas ao salvar.
        </p>
        <Controller
          control={form.control}
          name={`${base}.skills`}
          render={({ field }) => (
            <EditorTags
              tags={field.value ?? []}
              aoMudar={field.onChange}
              nome={`skills da experiência ${numero}`}
              aoAnunciar={setAnuncio}
              rotuloNovaTag="Nova skill"
            />
          )}
        />
        <p aria-live="polite" className="sr-only">
          {anuncio}
        </p>
      </div>
      {!legada && <SugestaoBlocosDaExperiencia form={form} indice={indice} />}
    </>
  );
}
