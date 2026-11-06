import { Button } from "../shared/ui/Button";
import estilos from "./FalhaInesperada.module.css";

/** Tela exibida quando um erro não tratado interrompe a renderização. */
export function FalhaInesperada() {
  return (
    <div className={estilos.falha}>
      <div>
        <h1 className={estilos.titulo}>Algo deu errado</h1>
        <p className={estilos.texto}>
          Uma falha inesperada interrompeu a tela. Recarregue para tentar de novo.
        </p>
        <Button variante="primary" onClick={() => window.location.reload()}>
          Recarregar
        </Button>
      </div>
    </div>
  );
}
