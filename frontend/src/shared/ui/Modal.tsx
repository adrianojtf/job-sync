import { useEffect, useId, useRef, type KeyboardEvent, type ReactNode } from "react";
import { createPortal } from "react-dom";
import estilos from "./Modal.module.css";

const FOCAVEIS =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

interface Props {
  aberto: boolean;
  titulo: string;
  descricao?: string;
  aoFechar: () => void;
  rodape?: ReactNode;
  children?: ReactNode;
}

export function Modal({ aberto, titulo, descricao, aoFechar, rodape, children }: Props) {
  const idTitulo = useId();
  const idDescricao = useId();
  const dialogo = useRef<HTMLDivElement>(null);
  const corpo = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!aberto) return;
    const focoAnterior = document.activeElement as HTMLElement | null;
    const primeiro = corpo.current?.querySelector<HTMLElement>(FOCAVEIS);
    (primeiro ?? dialogo.current)?.focus();
    return () => focoAnterior?.focus();
  }, [aberto]);

  if (!aberto) return null;

  // O foco fica preso no diálogo, então o teclado é tratado aqui: Esc fecha e Tab circula.
  const aoTeclar = (evento: KeyboardEvent<HTMLDivElement>) => {
    if (evento.key === "Escape") {
      evento.stopPropagation();
      aoFechar();
      return;
    }
    if (evento.key !== "Tab" || !dialogo.current) return;
    const focaveis = Array.from(dialogo.current.querySelectorAll<HTMLElement>(FOCAVEIS));
    const primeiro = focaveis[0];
    const ultimo = focaveis[focaveis.length - 1];
    if (evento.shiftKey && document.activeElement === primeiro) {
      evento.preventDefault();
      ultimo?.focus();
    } else if (!evento.shiftKey && document.activeElement === ultimo) {
      evento.preventDefault();
      primeiro?.focus();
    }
  };

  return createPortal(
    <div
      className={estilos.fundo}
      data-testid="modal-fundo"
      onMouseDown={(evento) => {
        if (evento.target === evento.currentTarget) aoFechar();
      }}
    >
      <div
        ref={dialogo}
        className={estilos.modal}
        role="dialog"
        aria-modal="true"
        aria-labelledby={idTitulo}
        aria-describedby={descricao ? idDescricao : undefined}
        tabIndex={-1}
        onKeyDown={aoTeclar}
      >
        <div className={estilos.cabecalho}>
          <h2 id={idTitulo} className={estilos.titulo}>
            {titulo}
          </h2>
          <button type="button" className={estilos.fechar} aria-label="Fechar" onClick={aoFechar}>
            ×
          </button>
        </div>
        {descricao && (
          <p id={idDescricao} className={estilos.descricao}>
            {descricao}
          </p>
        )}
        <div ref={corpo}>{children}</div>
        {rodape && <div className={estilos.rodape}>{rodape}</div>}
      </div>
    </div>,
    document.body,
  );
}
