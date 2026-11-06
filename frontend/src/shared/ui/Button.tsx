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
  onClick,
  ...resto
}: Props) {
  const classes = [
    estilos.botao,
    estilos[variante],
    larguraTotal && estilos.larguraTotal,
    carregando && estilos.carregando,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  // Em carregamento o botão não usa `disabled`, que tiraria o foco dele: ignora cliques e anuncia ocupado.
  return (
    <button
      type={type}
      className={classes}
      disabled={disabled}
      aria-disabled={carregando || undefined}
      aria-busy={carregando || undefined}
      onClick={(evento) => {
        if (carregando) {
          evento.preventDefault();
          return;
        }
        onClick?.(evento);
      }}
      {...resto}
    >
      {children}
    </button>
  );
}
