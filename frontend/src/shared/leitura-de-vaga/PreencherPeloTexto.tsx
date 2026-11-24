import type { DadosVaga } from "../../api/tipos";
import { Button } from "../ui/Button";
import estilos from "./LeituraDeVaga.module.css";
import { ResultadoDaLeitura } from "./ResultadoDaLeitura";
import type { CampoIdentificacao } from "./resumo-da-leitura";
import { useLeituraDeVaga } from "./use-leitura-de-vaga";

interface Props {
  texto: string;
  aoLer: (dados: DadosVaga) => void;
  campos?: CampoIdentificacao[];
}

/** Alternativa ao link: identifica título, empresa e demais dados a partir do texto colado. */
export function PreencherPeloTexto({ texto, aoLer, campos }: Props) {
  const leitura = useLeituraDeVaga(aoLer, campos);
  const conteudo = texto.trim();

  return (
    <div className={estilos.bloco}>
      <div>
        <Button
          variante="text"
          disabled={conteudo === ""}
          carregando={leitura.lendo}
          onClick={() => leitura.ler({ texto: conteudo })}
        >
          Preencher os campos pelo texto
        </Button>
      </div>
      <ResultadoDaLeitura
        lendo={leitura.lendo}
        erro={leitura.erro}
        resumo={leitura.resumo}
        origem="texto"
        aoCancelar={leitura.cancelar}
      />
    </div>
  );
}
