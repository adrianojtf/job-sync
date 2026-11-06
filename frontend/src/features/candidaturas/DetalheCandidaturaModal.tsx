import type { Candidatura, StatusCandidatura } from "../../api/tipos";
import { formatarData, formatarDataHora } from "../../shared/formatacao";
import { Modal } from "../../shared/ui/Modal";
import { StatusBadge } from "../../shared/ui/StatusBadge";
import { useCurriculos } from "../curriculos/use-curriculos";
import estilos from "./CandidaturasPage.module.css";
import { rotuloStatus, TOM_STATUS } from "./status";

interface Props {
  candidatura: Candidatura | null;
  aoFechar: () => void;
}

/** RF10.3 — dados da candidatura, currículo usado e histórico de status. */
export function DetalheCandidaturaModal({ candidatura, aoFechar }: Props) {
  const curriculos = useCurriculos();
  if (!candidatura) return null;

  const curriculo = curriculos.data?.find((item) => item.id === candidatura.curriculo_salvo_id);
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
        <dt>Aplicada em</dt>
        <dd>{formatarData(candidatura.data_aplicacao)}</dd>
        <dt>Currículo usado</dt>
        <dd>{nomeCurriculo}</dd>
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
