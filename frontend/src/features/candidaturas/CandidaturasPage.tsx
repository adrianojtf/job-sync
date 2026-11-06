import { useState } from "react";
import { Link } from "react-router-dom";
import type { Candidatura, StatusCandidatura } from "../../api/tipos";
import { CabecalhoPagina } from "../../app/CabecalhoPagina";
import { formatarData } from "../../shared/formatacao";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { EmptyState } from "../../shared/ui/EmptyState";
import { Panel } from "../../shared/ui/Panel";
import { useToast } from "../../shared/ui/use-toast";
import estilos from "./CandidaturasPage.module.css";
import { DetalheCandidaturaModal } from "./DetalheCandidaturaModal";
import { ORDEM_STATUS, ROTULO_STATUS } from "./status";
import { useCandidaturas, useMoverCandidatura } from "./use-candidaturas";

const contar = (quantidade: number) =>
  `${quantidade} ${quantidade === 1 ? "candidatura" : "candidaturas"}`;

/** T9 — Kanban de candidaturas (JOB-0006, RF10.1–RF10.3). */
export function CandidaturasPage() {
  const candidaturas = useCandidaturas();
  const mover = useMoverCandidatura();
  const { notificar } = useToast();
  const [emDetalhe, setEmDetalhe] = useState<Candidatura | null>(null);
  const porStatus = candidaturas.data?.por_status ?? {};

  const moverPara = (candidatura: Candidatura, novoStatus: StatusCandidatura) =>
    mover.mutate(
      { id: candidatura.id, novoStatus },
      {
        onSuccess: () =>
          notificar(`Candidatura movida para ${ROTULO_STATUS[novoStatus]}.`, "sucesso"),
        onError: (erro) => notificar(erro.message, "erro"),
      },
    );

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
        <div className={estilos.quadro}>
          {ORDEM_STATUS.map((status) => {
            const itens = porStatus[status] ?? [];
            return (
              <section
                key={status}
                className={estilos.coluna}
                aria-label={`${ROTULO_STATUS[status]}, ${contar(itens.length)}`}
              >
                <h2 className={estilos.cabecalhoColuna}>
                  {ROTULO_STATUS[status]}
                  <span className={estilos.contagem} aria-hidden="true">
                    {itens.length}
                  </span>
                </h2>
                {itens.length === 0 ? (
                  <p className={estilos.vazio}>Nenhuma candidatura</p>
                ) : (
                  <ul className={estilos.cartoes}>
                    {itens.map((candidatura) => (
                      <CartaoCandidatura
                        key={candidatura.id}
                        candidatura={candidatura}
                        status={status}
                        aoMover={(novo) => moverPara(candidatura, novo)}
                        aoDetalhar={() => setEmDetalhe(candidatura)}
                      />
                    ))}
                  </ul>
                )}
              </section>
            );
          })}
        </div>
      )}

      <DetalheCandidaturaModal candidatura={emDetalhe} aoFechar={() => setEmDetalhe(null)} />
    </>
  );
}

interface PropsCartao {
  candidatura: Candidatura;
  status: StatusCandidatura;
  aoMover: (novo: StatusCandidatura) => void;
  aoDetalhar: () => void;
}

function CartaoCandidatura({ candidatura, status, aoMover, aoDetalhar }: PropsCartao) {
  const idMover = `mover-${candidatura.id}`;
  return (
    <li className={estilos.cartao}>
      <strong className={estilos.cargo}>{candidatura.cargo}</strong>
      <span className={estilos.empresa}>{candidatura.empresa}</span>
      <span className={estilos.data}>Aplicada em {formatarData(candidatura.data_aplicacao)}</span>
      <div className={estilos.rodapeCartao}>
        <label htmlFor={idMover} className="sr-only">
          Mover {candidatura.cargo} para
        </label>
        <select
          id={idMover}
          className={estilos.mover}
          value={status}
          onChange={(evento) => aoMover(evento.target.value as StatusCandidatura)}
        >
          {ORDEM_STATUS.map((opcao) => (
            <option key={opcao} value={opcao}>
              {ROTULO_STATUS[opcao]}
            </option>
          ))}
        </select>
        <Button
          variante="text"
          aria-label={`Detalhes de ${candidatura.cargo}`}
          onClick={aoDetalhar}
        >
          Detalhes
        </Button>
      </div>
    </li>
  );
}
