import { useState } from "react";
import { Controller, type UseFormReturn } from "react-hook-form";
import { EditorTags } from "../../shared/formulario-curriculo/EditorTags";
import estilos from "../perfil/ConquistasDaExperiencia.module.css";
import type { FormularioRevisao } from "./formulario-revisao";

interface Props {
  form: UseFormReturn<FormularioRevisao>;
  indice: number;
}

/** Skills de uma experiência da revisão (JOB-0045): tags que se criam e se excluem. */
export function SkillsDaExperiencia({ form, indice }: Props) {
  const [anuncio, setAnuncio] = useState("");
  const numero = indice + 1;
  return (
    <div role="group" aria-label={`Skills da experiência ${numero}`} className={estilos.conquistas}>
      <h4 className={estilos.titulo}>Skills</h4>
      <Controller
        control={form.control}
        name={`experiencias.${indice}.skills`}
        render={({ field }) => (
          <EditorTags
            tags={field.value ?? []}
            aoMudar={field.onChange}
            nome={`skills da experiência ${numero}`}
            aoAnunciar={setAnuncio}
            rotuloNovaTag="Nova skill"
            ajuda="Tecnologias e competências usadas. Digite e tecle Enter ou vírgula."
          />
        )}
      />
      <p aria-live="polite" className="sr-only">
        {anuncio}
      </p>
    </div>
  );
}
