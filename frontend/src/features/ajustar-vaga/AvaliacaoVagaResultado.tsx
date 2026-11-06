import type { AvaliacaoDescricaoVaga } from "../../api/tipos";
import { ScoreDimensions } from "../../shared/ui/ScoreDimensions";

/** Score da descrição da vaga e as quatro dimensões do Jev (JOB-0013). */
export function AvaliacaoVagaResultado({ avaliacao }: { avaliacao: AvaliacaoDescricaoVaga }) {
  return (
    <ScoreDimensions
      score={avaliacao.score}
      legenda="Qualidade da descrição, estimativa de 0 a 100"
      dimensoes={[
        { nome: "Completude", ...avaliacao.completude },
        { nome: "Clareza", ...avaliacao.clareza },
        { nome: "Relevância", ...avaliacao.relevancia },
        { nome: "Inclusão", ...avaliacao.inclusao },
      ]}
    />
  );
}
