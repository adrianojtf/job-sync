import type { AnaliseAts } from "../../api/tipos";
import estilos from "./Resultados.module.css";

const CATEGORIAS: Record<string, string> = {
  TECNOLOGIA: "tecnologia",
  FERRAMENTA: "ferramenta",
  HABILIDADE: "habilidade",
  METODOLOGIA: "metodologia",
  OUTRA: "outra",
};

/** Nota ATS, requisitos não cobertos e sugestões (JOB-0005). */
interface Props {
  analise: Pick<AnaliseAts, "nota" | "requisitos_faltantes" | "sugestoes">;
  /** A candidatura em vaga externa não gera sugestões: a seção fica oculta. */
  mostrarSugestoes?: boolean;
}

export function AnaliseAtsResultado({ analise, mostrarSugestoes = true }: Props) {
  const requisitos = analise.requisitos_faltantes ?? [];
  const sugestoes = analise.sugestoes ?? [];
  return (
    <div aria-live="polite">
      <div className={estilos.nota}>
        <span className={estilos.notaValor}>{analise.nota}</span>
        <span className={estilos.legenda}>
          de 100 · estimativa baseada nos requisitos explícitos da vaga
        </span>
      </div>

      <h3 className={estilos.subtitulo}>Requisitos não encontrados no currículo</h3>
      {requisitos.length === 0 ? (
        <p className={estilos.texto}>Todos os requisitos explícitos foram encontrados.</p>
      ) : (
        <ul className={estilos.requisitos}>
          {requisitos.map((requisito) => (
            <li key={requisito.nome} className={estilos.requisito}>
              <span>{requisito.nome}</span>
              <span className={estilos.categoria}>
                {CATEGORIAS[requisito.categoria] ?? requisito.categoria}
              </span>
            </li>
          ))}
        </ul>
      )}

      {mostrarSugestoes && (
        <>
          <h3 className={estilos.subtitulo}>Sugestões</h3>
          {sugestoes.length === 0 ? (
            <p className={estilos.texto}>Nenhuma sugestão adicional.</p>
          ) : (
            <ul className={estilos.lista}>
              {sugestoes.map((sugestao) => (
                <li key={sugestao}>{sugestao}</li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
