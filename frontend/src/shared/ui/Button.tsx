import type { ButtonHTMLAttributes } from "react";
import estilos from "./Button.module.css";

type Variante = "primary" | "secondary" | "text";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: Variante;
  carregando?: boolean;
  larguraTotal?: boolean;
}

export function Button({
  variante = "secondary",
  carregando = false,
  larguraTotal = false,
  disabled,
  type = "button",
  className,
  children,
  ...resto
}: Props) {
  const classes = [
    estilos.botao,
    estilos[variante],
    larguraTotal && estilos.larguraTotal,
    className,
  ]
    .filter(Boolean)
    .join(" ");
  return (
    <button
      type={type}
      className={classes}
      disabled={disabled || carregando}
      aria-busy={carregando || undefined}
      {...resto}
    >
      {children}
    </button>
  );
}
