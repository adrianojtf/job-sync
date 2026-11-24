import {
  forwardRef,
  useId,
  type InputHTMLAttributes,
  type ReactNode,
  type Ref,
  type SelectHTMLAttributes,
  type TextareaHTMLAttributes,
} from "react";
import estilos from "./Field.module.css";

interface Comum {
  rotulo: string;
  ajuda?: string;
  erro?: string;
  /** Esconde o rótulo só visualmente (ele continua associado, para leitores de tela). */
  rotuloOculto?: boolean;
}

type PropsInput = Comum & { tipoCampo?: "input" } & InputHTMLAttributes<HTMLInputElement>;
type PropsTextarea = Comum & {
  tipoCampo: "textarea";
} & TextareaHTMLAttributes<HTMLTextAreaElement>;
type PropsSelect = Comum & {
  tipoCampo: "select";
  opcoes: { valor: string; rotulo: string }[];
} & SelectHTMLAttributes<HTMLSelectElement>;

export type FieldProps = PropsInput | PropsTextarea | PropsSelect;

type ElementoCampo = HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;

/**
 * Campo com rótulo associado, texto de ajuda e mensagem de erro ligados por aria-describedby.
 * Repassa a ref para funcionar com register() do react-hook-form.
 */
export const Field = forwardRef<ElementoCampo, FieldProps>(function Field(props, ref) {
  const idGerado = useId();
  const { rotulo, ajuda, erro, rotuloOculto, id = idGerado, className } = props;
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
      <label
        className={[estilos.rotulo, rotuloOculto && "sr-only"].filter(Boolean).join(" ")}
        htmlFor={id}
      >
        {rotulo}
      </label>
      {renderizarControle(props, acessibilidade, ref)}
      {ajuda && (
        <p id={idAjuda} className={estilos.ajuda}>
          {ajuda}
        </p>
      )}
      {erro && (
        <p id={idErro} className={estilos.erro}>
          {erro}
        </p>
      )}
    </div>
  );
});

function renderizarControle(
  props: FieldProps,
  acessibilidade: Record<string, unknown>,
  ref: Ref<ElementoCampo>,
): ReactNode {
  if (props.tipoCampo === "textarea") {
    const { rotulo: _r, ajuda: _a, erro: _e, rotuloOculto: _o, tipoCampo: _t, ...nativos } = props;
    void [_r, _a, _e, _o, _t];
    return <textarea {...nativos} {...acessibilidade} ref={ref as Ref<HTMLTextAreaElement>} />;
  }
  if (props.tipoCampo === "select") {
    const {
      rotulo: _r,
      ajuda: _a,
      erro: _e,
      rotuloOculto: _o,
      tipoCampo: _t,
      opcoes,
      ...nativos
    } = props;
    void [_r, _a, _e, _o, _t];
    return (
      <select {...nativos} {...acessibilidade} ref={ref as Ref<HTMLSelectElement>}>
        {opcoes.map((opcao) => (
          <option key={opcao.valor} value={opcao.valor}>
            {opcao.rotulo}
          </option>
        ))}
      </select>
    );
  }
  const { rotulo: _r, ajuda: _a, erro: _e, rotuloOculto: _o, tipoCampo: _t, ...nativos } = props;
  void [_r, _a, _e, _o, _t];
  return <input {...nativos} {...acessibilidade} ref={ref as Ref<HTMLInputElement>} />;
}
