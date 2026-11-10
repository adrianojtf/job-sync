import estilos from "./TelaCarregando.module.css";

/** Exibida enquanto o servidor ainda não disse se há sessão, para não piscar a tela de entrada. */
export function TelaCarregando() {
  return (
    <div className={estilos.tela} role="status" aria-live="polite">
      Carregando…
    </div>
  );
}
