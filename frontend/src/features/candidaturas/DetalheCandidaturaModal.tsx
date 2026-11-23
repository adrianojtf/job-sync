import type { Candidatura, StatusCandidatura } from "../../api/tipos";
import { formatarData, formatarDataHora } from "../../shared/formatacao";
import { Button } from "../../shared/ui/Button";
import { LinkButton } from "../../shared/ui/LinkButton";
import { Modal } from "../../shared/ui/Modal";
import { StatusBadge } from "../../shared/ui/StatusBadge";
import { useToast } from "../../shared/ui/use-toast";
import { useBaixarCurriculo, useCurriculos } from "../curriculos/use-curriculos";
import { useCurriculosAdaptados } from "../curriculos-adaptados/use-curriculos-adaptados";
import estilos from "./CandidaturasPage.module.css";
import { ORDEM_STATUS, ROTULO_STATUS, rotuloStatus, TOM_STATUS } from "./status";
import { useMoverComAviso } from "./use-mover-com-aviso";

const ID_MOVER = "detalhe-mover-para";

interface Props {
  candidatura: Candidatura | null;
  aoFechar: () => void;
}

/** RF10.3 — dados da candidatura, currículo usado e histórico de status. RF18a — move sem arrastar. */
export function DetalheCandidaturaModal({ candidatura, aoFechar }: Props) {
  const curriculos = useCurriculos();
  const adaptados = useCurriculosAdaptados();
  const download = useBaixarCurriculo();
  const mover = useMoverComAviso();
  const { notificar } = useToast();
  if (!candidatura) return null;

  const curriculo = curriculos.data?.find((item) => item.id === candidatura.curriculo_salvo_id);
  const adaptado = adaptados.data?.find(
    (item) => item.curriculo_salvo_id === candidatura.curriculo_salvo_id,
  );
  const nomeCurriculo = curriculos.isPending
    ? "Carregando…"
    : (curriculo?.nome_referencia ?? "Removido da biblioteca");
  const historico = candidatura.historico_status ?? [];

  return (
    <Modal aberto titulo={candidatura.cargo} aoFechar={aoFechar}>
      <dl className={estilos.dados}>
        <dt>Empresa</dt>
        <dd>{candidatura.empresa}</dd>
        <dt>Status</dt>
        <dd>
          <StatusBadge tom={TOM_STATUS[candidatura.status as StatusCandidatura] ?? "neutro"}>
            {rotuloStatus(candidatura.status)}
          </StatusBadge>
        </dd>
        <dt>
          <label htmlFor={ID_MOVER}>Mover para</label>
        </dt>
        <dd>
          <select
            id={ID_MOVER}
            className={estilos.mover}
            value={candidatura.status}
            onChange={(evento) =>
              mover(candidatura.id, evento.target.value as StatusCandidatura, 0)
            }
          >
            {ORDEM_STATUS.map((opcao) => (
              <option key={opcao} value={opcao}>
                {ROTULO_STATUS[opcao]}
              </option>
            ))}
          </select>
        </dd>
        <dt>Aplicada em</dt>
        <dd>{formatarData(candidatura.data_aplicacao)}</dd>
        <dt>Currículo usado</dt>
        <dd className={estilos.curriculoUsado}>
          {nomeCurriculo}
          {curriculo && (
            <Button
              aria-label="Baixar PDF do currículo usado"
              carregando={download.isPending}
              onClick={() =>
                download.mutate(curriculo.id, {
                  onError: (erro) => notificar(erro.message, "erro"),
                })
              }
            >
              Baixar PDF
            </Button>
          )}
          {adaptado && (
            <LinkButton to={`/curriculos-adaptados/${encodeURIComponent(adaptado.id)}`}>
              Editar currículo
            </LinkButton>
          )}
        </dd>
      </dl>
      <h3 style={{ fontSize: 13, margin: "0 0 6px" }}>Histórico</h3>
      <ul className={estilos.historico} aria-label="Histórico de status">
        {historico.map((mudanca) => (
          <li key={`${mudanca.status}-${mudanca.data}`}>
            {rotuloStatus(mudanca.status)} · {formatarDataHora(mudanca.data)}
          </li>
        ))}
      </ul>
      <p className={estilos.nota}>
        Por enquanto, o sistema guarda só a mudança de status mais recente.
      </p>
    </Modal>
  );
}
