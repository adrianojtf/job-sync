import { useId } from "react";
import { Aviso } from "../../shared/ui/Aviso";

interface Props {
  lacunas: string[];
}

/**
 * Tecnologias que a vaga pede e o perfil não mostra (JOB-0044): não entraram em Competências.
 * Se o candidato as usa, adiciona a tag no editor; a JOB-0043 poderá perguntar por elas.
 */
export function LacunasTecnologiaAviso({ lacunas }: Props) {
  const idTitulo = useId();
  if (lacunas.length === 0) return null;

  return (
    <section aria-labelledby={idTitulo}>
      <h3 id={idTitulo} className="sr-only">
        Tecnologias da vaga fora das competências
      </h3>
      <Aviso>
        Tecnologias da vaga que seu perfil não mostra: {lacunas.join(", ")}. Se você as usa,
        adicione a tag em Competências.
      </Aviso>
    </section>
  );
}
