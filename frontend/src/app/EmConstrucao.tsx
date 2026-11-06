import { EmptyState } from "../shared/ui/EmptyState";
import { Panel } from "../shared/ui/Panel";
import { CabecalhoPagina } from "./CabecalhoPagina";

interface Props {
  titulo: string;
  tarefa: string;
}

/** Marcador das telas que ainda serão entregues pelas próximas tarefas do JOB-0015. */
export function EmConstrucao({ titulo, tarefa }: Props) {
  return (
    <>
      <CabecalhoPagina titulo={titulo} />
      <Panel>
        <EmptyState
          titulo="Tela em construção"
          descricao={`Esta tela será entregue na tarefa ${tarefa} do JOB-0015. Enquanto isso, use o MVP em Streamlit.`}
        />
      </Panel>
    </>
  );
}
