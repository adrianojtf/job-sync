import { Link, type LinkProps } from "react-router-dom";
import estilos from "./Button.module.css";

/** Link de navegação com a aparência de um Button secundário. */
export function LinkButton({ className, ...resto }: LinkProps) {
  return (
    <Link
      className={[estilos.botao, estilos.secondary, className].filter(Boolean).join(" ")}
      {...resto}
    />
  );
}
