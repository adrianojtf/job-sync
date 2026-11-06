import { useId } from "react";
import { baixarArquivo } from "../../shared/arquivos/arquivos";
import { copiarTexto } from "../../shared/copiar";
import { paraSlug } from "../../shared/formatacao";
import { Button } from "../../shared/ui/Button";
import { useToast } from "../../shared/ui/use-toast";
import estilos from "./AjustarVagaPage.module.css";

interface Props {
  texto: string;
  cargo: string;
  empresa: string;
}

/** Carta de apresentação gerada, com copiar e baixar como .txt (JOB-0005). */
export function CartaGerada({ texto, cargo, empresa }: Props) {
  const id = useId();
  const { notificar } = useToast();

  const copiar = async () =>
    (await copiarTexto(texto))
      ? notificar("Carta copiada.", "sucesso")
      : notificar("Não foi possível copiar. Selecione o texto e copie manualmente.", "erro");

  const baixar = () => {
    const nome = ["carta-apresentacao", paraSlug(cargo), paraSlug(empresa)]
      .filter(Boolean)
      .join("-");
    baixarArquivo(new Blob([texto], { type: "text/plain;charset=utf-8" }), `${nome}.txt`);
  };

  return (
    <div>
      <label htmlFor={id} className="sr-only">
        Texto da carta
      </label>
      <textarea id={id} className={estilos.carta} readOnly value={texto} />
      <div className={estilos.acoes}>
        <Button onClick={copiar}>Copiar carta</Button>
        <Button onClick={baixar}>Baixar carta</Button>
      </div>
    </div>
  );
}
