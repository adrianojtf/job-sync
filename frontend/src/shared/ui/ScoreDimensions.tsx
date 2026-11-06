import estilos from "./ScoreDimensions.module.css";

export interface Dimensao {
  nome: string;
  score: number;
  nivel?: string;
}

interface Props {
  score: number;
  legenda?: string;
  dimensoes: Dimensao[];
}

/** Score geral (0–100) e dimensões avaliadas, com o rótulo de nível vindo da API. */
export function ScoreDimensions({ score, legenda = "Estimativa de 0 a 100", dimensoes }: Props) {
  return (
    <div>
      <div className={estilos.score}>
        <span className={estilos.valor}>{score}</span>
        <span className={estilos.legenda}>{legenda}</span>
      </div>
      <ul className={estilos.lista}>
        {dimensoes.map((dimensao) => (
          <li key={dimensao.nome}>
            <div className={estilos.linha}>
              <span>{dimensao.nome}</span>
              <span>
                {dimensao.score}
                {dimensao.nivel && ` · ${dimensao.nivel}`}
              </span>
            </div>
            <div
              className={estilos.barra}
              role="meter"
              aria-label={dimensao.nome}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={dimensao.score}
            >
              <span className={estilos.preenchimento} style={{ width: `${dimensao.score}%` }} />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
