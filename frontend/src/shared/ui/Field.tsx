import { useId, type InputHTMLAttributes, type TextareaHTMLAttributes } from "react";
import estilos from "./Field.module.css";

interface Comum {
  rotulo: string;
  ajuda?: string;
  erro?: string;
}

type PropsInput = Comum & { multilinha?: false } & InputHTMLAttributes<HTMLInputElement>;
type PropsTextarea = Comum & { multilinha: true } & TextareaHTMLAttributes<HTMLTextAreaElement>;

/** Campo com rótulo associado, texto de ajuda e mensagem de erro anunciada por leitores de tela. */
export function Field(props: PropsInput | PropsTextarea) {
  const idGerado = useId();
  const { rotulo, ajuda, erro, id = idGerado, className, ...resto } = props;
  const idAjuda = ajuda ? `${id}-ajuda` : undefined;
  const idErro = erro ? `${id}-erro` : undefined;
  const acessibilidade = {
    id,
    className: [estilos.entrada, className].filter(Boolean).join(" "),
    "aria-invalid": erro ? true : undefined,
    "aria-describedby": [idAjuda, idErro].filter(Boolean).join(" ") || undefined,
  };

  return (
    <div className={estilos.campo}>
      <label className={estilos.rotulo} htmlFor={id}>
        {rotulo}
      </label>
      {resto.multilinha ? (
        <textarea {...omitirMultilinha(resto)} {...acessibilidade} />
      ) : (
        <input {...omitirMultilinha(resto)} {...acessibilidade} />
      )}
      {ajuda && (
        <p id={idAjuda} className={estilos.ajuda}>
          {ajuda}
        </p>
      )}
      {erro && (
        <p id={idErro} className={estilos.erro} role="alert">
          {erro}
        </p>
      )}
    </div>
  );
}

function omitirMultilinha<T extends { multilinha?: boolean }>(props: T): Omit<T, "multilinha"> {
  const { multilinha: _ignorado, ...resto } = props;
  void _ignorado;
  return resto;
}
