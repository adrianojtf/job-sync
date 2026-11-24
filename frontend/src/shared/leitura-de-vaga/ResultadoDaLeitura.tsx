import { Aviso } from "../ui/Aviso";
import { Button } from "../ui/Button";
import estilos from "./LeituraDeVaga.module.css";
import { juntarEmPortugues, type ResumoDaLeitura } from "./resumo-da-leitura";

interface Props {
  lendo: boolean;
  erro?: string;
  resumo: ResumoDaLeitura | null;
  origem: "link" | "texto";
  aoCancelar: () => void;
}

/** Estado da leitura da vaga: em andamento (com cancelar), falha ou o que foi preenchido. */
export function ResultadoDaLeitura({ lendo, erro, resumo, origem, aoCancelar }: Props) {
  if (lendo) {
    return (
      <div className={estilos.estado}>
        <p role="status" className={estilos.mensagem}>
          {origem === "link" ? "Lendo a vaga…" : "Identificando os dados no texto…"}
        </p>
        <Button variante="text" onClick={aoCancelar}>
          Cancelar leitura
        </Button>
      </div>
    );
  }
  if (erro) {
    return <Aviso tom="erro">{erro}</Aviso>;
  }
  if (resumo) {
    const ausentes =
      resumo.ausentes.length > 0 ? ` Não encontramos: ${juntarEmPortugues(resumo.ausentes)}.` : "";
    return (
      <p role="status" className={estilos.mensagem}>
        {`${origem === "link" ? "Dados lidos do link" : "Dados identificados no texto"}: ${juntarEmPortugues(resumo.preenchidos)}.${ausentes} Confira antes de continuar.`}
      </p>
    );
  }
  return null;
}
