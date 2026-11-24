import type { KeyboardEvent } from "react";
import type { DadosVaga } from "../../api/tipos";
import { Button } from "../ui/Button";
import { Field } from "../ui/Field";
import estilos from "./LeituraDeVaga.module.css";
import { ResultadoDaLeitura } from "./ResultadoDaLeitura";
import type { CampoIdentificacao } from "./resumo-da-leitura";
import { useLeituraDeVaga } from "./use-leitura-de-vaga";

interface Props {
  valor: string;
  aoAlterar: (valor: string) => void;
  /** Recebe o rascunho lido; a tela decide o que preencher. */
  aoLer: (dados: DadosVaga) => void;
  /** Campos de identificação que a tela mostra, usados para dizer o que foi preenchido. */
  campos?: CampoIdentificacao[];
  rotulo?: string;
}

/** Campo "Link da vaga" com o botão que lê cargo, empresa, local e descrição do link (JOB-0047). */
export function CampoLinkVaga({ valor, aoAlterar, aoLer, campos, rotulo = "Link da vaga" }: Props) {
  const leitura = useLeituraDeVaga(aoLer, campos);
  const link = valor.trim();

  const ler = () => {
    if (link !== "" && !leitura.lendo) leitura.ler({ url: link });
  };

  // Enter lê a vaga em vez de enviar o formulário que contém o campo.
  const aoTeclar = (evento: KeyboardEvent<HTMLInputElement>) => {
    if (evento.key !== "Enter") return;
    evento.preventDefault();
    ler();
  };

  return (
    <div className={estilos.bloco}>
      <div className={estilos.linha}>
        <div className={estilos.campo}>
          <Field
            rotulo={rotulo}
            type="url"
            placeholder="Cole o link de uma vaga (LinkedIn, Gupy…)"
            ajuda="Funciona com vagas públicas. Se o site bloquear, cole o texto da vaga."
            value={valor}
            onChange={(evento) => aoAlterar(evento.target.value)}
            onKeyDown={aoTeclar}
          />
        </div>
        <Button
          variante="secondary"
          disabled={link === ""}
          carregando={leitura.lendo}
          onClick={ler}
        >
          Ler vaga
        </Button>
      </div>
      <ResultadoDaLeitura
        lendo={leitura.lendo}
        erro={leitura.erro}
        resumo={leitura.resumo}
        origem="link"
        aoCancelar={leitura.cancelar}
      />
    </div>
  );
}
