import {
  closestCorners,
  DndContext,
  DragOverlay,
  KeyboardSensor,
  MouseSensor,
  TouchSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragOverEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { sortableKeyboardCoordinates } from "@dnd-kit/sortable";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import type { StatusCandidatura } from "../../api/tipos";
import { CabecalhoPagina } from "../../app/CabecalhoPagina";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { EmptyState } from "../../shared/ui/EmptyState";
import { Panel } from "../../shared/ui/Panel";
import { criarAnuncios, INSTRUCOES_LEITOR_DE_TELA } from "./anuncios";
import { CartaoFlutuante } from "./CartaoCandidatura";
import estilos from "./CandidaturasPage.module.css";
import { ColunaKanban } from "./ColunaKanban";
import { DetalheCandidaturaModal } from "./DetalheCandidaturaModal";
import { calcularDestino, encontrarCandidatura } from "./movimento";
import { ORDEM_STATUS } from "./status";
import { useCandidaturas } from "./use-candidaturas";
import { useMoverComAviso } from "./use-mover-com-aviso";

/** Distância (mouse) e atraso (toque) que separam um clique ou rolagem de um arrasto. */
const ATIVACAO_MOUSE = { distance: 6 };
const ATIVACAO_TOQUE = { delay: 200, tolerance: 8 };

/** Kanban de candidaturas (JOB-0006, JOB-0038): arrastar e soltar, reordenar e abrir o detalhe pelo título. */
export function CandidaturasPage() {
  const candidaturas = useCandidaturas();
  const mover = useMoverComAviso();
  const [idEmDetalhe, setIdEmDetalhe] = useState<string | null>(null);
  const [idArrastado, setIdArrastado] = useState<string | null>(null);
  const [statusSobre, setStatusSobre] = useState<string | null>(null);
  const quadro = candidaturas.data;
  const porStatus = quadro?.por_status ?? {};

  const sensores = useSensors(
    useSensor(MouseSensor, { activationConstraint: ATIVACAO_MOUSE }),
    useSensor(TouchSensor, { activationConstraint: ATIVACAO_TOQUE }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );
  const anuncios = useMemo(() => criarAnuncios(() => quadro), [quadro]);

  const arrastada = quadro && idArrastado ? encontrarCandidatura(quadro, idArrastado) : undefined;
  const emDetalhe =
    quadro && idEmDetalhe ? (encontrarCandidatura(quadro, idEmDetalhe) ?? null) : null;

  const encerrarArrasto = () => {
    setIdArrastado(null);
    setStatusSobre(null);
  };

  const aoSobrepor = ({ active, over }: DragOverEvent) => {
    const destino = quadro && over && calcularDestino(quadro, String(active.id), String(over.id));
    setStatusSobre(destino ? destino.status : null);
  };

  const aoSoltar = ({ active, over }: DragEndEvent) => {
    const destino = quadro && over && calcularDestino(quadro, String(active.id), String(over.id));
    encerrarArrasto();
    if (destino) mover(String(active.id), destino.status as StatusCandidatura, destino.posicao);
  };

  return (
    <>
      <CabecalhoPagina
        titulo="Candidaturas"
        descricao="Acompanhe cada candidatura do envio até a resposta final."
      />

      {candidaturas.isPending && <p role="status">Carregando candidaturas…</p>}
      {candidaturas.isError && (
        <Aviso
          tom="erro"
          acao={<Button onClick={() => candidaturas.refetch()}>Tentar novamente</Button>}
        >
          Não foi possível carregar as candidaturas: {candidaturas.error.message}
        </Aviso>
      )}
      {candidaturas.isSuccess && candidaturas.data.total === 0 && (
        <Panel>
          <EmptyState titulo="Nenhuma candidatura ainda">
            Crie uma a partir de uma vaga salva.{" "}
            <Link to="/vagas-salvas">Ir para Vagas salvas</Link>
          </EmptyState>
        </Panel>
      )}

      {candidaturas.isSuccess && candidaturas.data.total > 0 && (
        <DndContext
          sensors={sensores}
          collisionDetection={closestCorners}
          accessibility={{
            announcements: anuncios,
            screenReaderInstructions: INSTRUCOES_LEITOR_DE_TELA,
          }}
          onDragStart={({ active }: DragStartEvent) => setIdArrastado(String(active.id))}
          onDragOver={aoSobrepor}
          onDragEnd={aoSoltar}
          onDragCancel={encerrarArrasto}
        >
          <div className={estilos.quadro}>
            {ORDEM_STATUS.map((status) => (
              <ColunaKanban
                key={status}
                status={status}
                candidaturas={porStatus[status] ?? []}
                destacada={statusSobre === status && idArrastado !== null}
                aoAbrir={(candidatura) => setIdEmDetalhe(candidatura.id)}
              />
            ))}
          </div>
          <DragOverlay>
            {arrastada ? <CartaoFlutuante candidatura={arrastada} /> : null}
          </DragOverlay>
        </DndContext>
      )}

      <DetalheCandidaturaModal candidatura={emDetalhe} aoFechar={() => setIdEmDetalhe(null)} />
    </>
  );
}
