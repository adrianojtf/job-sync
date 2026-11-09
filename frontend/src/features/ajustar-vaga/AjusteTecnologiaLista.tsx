import { useId } from "react";
import type { AjusteTecnologia } from "../../api/tipos";
import estilos from "./AjusteTecnologiaLista.module.css";

interface Props {
  ajustes: AjusteTecnologia[];
}

/**
 * Trocas de tecnologia que a IA fez nas experiências (JOB-0037), para o usuário conferir na
 * revisão. Descreve o que a IA fez; edições posteriores nos campos não a atualizam.
 */
export function AjusteTecnologiaLista({ ajustes }: Props) {
  const idTitulo = useId();
  if (ajustes.length === 0) return null;

  return (
    <section className={estilos.bloco} aria-labelledby={idTitulo}>
      <h3 id={idTitulo} className={estilos.titulo}>
        Ajustes de tecnologia
      </h3>
      <ul className={estilos.lista} aria-labelledby={idTitulo}>
        {ajustes.map((ajuste) => (
          <li key={`${ajuste.indice_experiencia}-${ajuste.original}`}>
            {ajuste.original} → {ajuste.alvo} em {ajuste.cargo} — {ajuste.empresa}
          </li>
        ))}
      </ul>
    </section>
  );
}
