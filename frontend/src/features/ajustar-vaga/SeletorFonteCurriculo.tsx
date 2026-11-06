import { forwardRef, type SelectHTMLAttributes } from "react";
import { Link } from "react-router-dom";
import { Aviso } from "../../shared/ui/Aviso";
import { Field } from "../../shared/ui/Field";

interface Props extends SelectHTMLAttributes<HTMLSelectElement> {
  opcoes: { valor: string; rotulo: string }[];
  carregando: boolean;
  erro?: string;
}

export const SeletorFonteCurriculo = forwardRef<HTMLSelectElement, Props>(
  function SeletorFonteCurriculo({ opcoes, carregando, erro, ...resto }, ref) {
    if (carregando) return <p>Carregando currículos…</p>;
    if (opcoes.length === 0) {
      return (
        <Aviso tom="alerta">
          Você ainda não tem um currículo base:{" "}
          <Link to="/perfil">preencha o currículo mestre</Link> ou{" "}
          <Link to="/curriculos">envie um PDF</Link>.
        </Aviso>
      );
    }
    return (
      <Field
        tipoCampo="select"
        rotulo="Currículo base"
        ajuda="O currículo mestre dispensa a leitura do PDF por IA."
        opcoes={opcoes}
        erro={erro}
        ref={ref as never}
        {...resto}
      />
    );
  },
);
