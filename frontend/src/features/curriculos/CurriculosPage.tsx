import { useState } from "react";
import type { CurriculoSalvo } from "../../api/tipos";
import { CabecalhoPagina } from "../../app/CabecalhoPagina";
import { formatarData } from "../../shared/formatacao";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { ConfirmacaoModal } from "../../shared/ui/ConfirmacaoModal";
import { EmptyState } from "../../shared/ui/EmptyState";
import { Panel } from "../../shared/ui/Panel";
import { useToast } from "../../shared/ui/use-toast";
import estilos from "./CurriculosPage.module.css";
import { EnviarCurriculoModal } from "./EnviarCurriculoModal";
import {
  LIMITE_CURRICULOS,
  useBaixarCurriculo,
  useCurriculos,
  useRemoverCurriculo,
} from "./use-curriculos";

/** T4 — Biblioteca de currículos em PDF do perfil (JOB-0004, RF5.1–RF5.3). */
export function CurriculosPage() {
  const curriculos = useCurriculos();
  const remocao = useRemoverCurriculo();
  const download = useBaixarCurriculo();
  const { notificar } = useToast();
  const [enviando, setEnviando] = useState(false);
  const [paraRemover, setParaRemover] = useState<CurriculoSalvo | null>(null);

  const itens = curriculos.data ?? [];
  const noLimite = itens.length >= LIMITE_CURRICULOS;

  const confirmarRemocao = () => {
    if (!paraRemover) return;
    remocao.mutate(paraRemover.id, {
      onSuccess: () => notificar("Currículo removido.", "sucesso"),
      onError: (erro) => notificar(erro.message, "erro"),
      onSettled: () => setParaRemover(null),
    });
  };

  const baixar = (curriculo: CurriculoSalvo) =>
    download.mutate(curriculo.id, { onError: (erro) => notificar(erro.message, "erro") });

  return (
    <>
      <CabecalhoPagina
        titulo="Meus currículos"
        descricao="Guarde até 10 PDFs para importar no currículo mestre ou usar nas candidaturas."
        acoes={
          <Button
            variante="primary"
            disabled={!curriculos.isSuccess || noLimite}
            onClick={() => setEnviando(true)}
          >
            <span aria-hidden="true">＋</span> Enviar currículo
          </Button>
        }
      />

      {noLimite && (
        <Aviso tom="alerta">
          Você atingiu o limite de 10 currículos. Remova um para enviar outro.
        </Aviso>
      )}

      <Panel
        titulo="Biblioteca"
        subtitulo={
          curriculos.isSuccess ? `${itens.length} de ${LIMITE_CURRICULOS} currículos` : undefined
        }
      >
        {curriculos.isPending && <p role="status">Carregando currículos…</p>}
        {curriculos.isError && (
          <Aviso
            tom="erro"
            acao={<Button onClick={() => curriculos.refetch()}>Tentar novamente</Button>}
          >
            Não foi possível carregar os currículos: {curriculos.error.message}
          </Aviso>
        )}
        {curriculos.isSuccess && itens.length === 0 && (
          <EmptyState
            titulo="Nenhum currículo salvo"
            descricao="Envie um PDF, por exemplo o export “Salvar como PDF” do seu LinkedIn."
          />
        )}
        {itens.length > 0 && (
          <ul className={estilos.lista}>
            {itens.map((curriculo) => (
              <li key={curriculo.id} className={estilos.item}>
                <span className={estilos.icone} aria-hidden="true">
                  ▤
                </span>
                <div className={estilos.info}>
                  <strong className={estilos.nome}>{curriculo.nome_referencia}</strong>
                  <span className={estilos.data}>
                    Enviado em {formatarData(curriculo.data_upload)}
                  </span>
                </div>
                <div className={estilos.acoes}>
                  <Button
                    aria-label={`Baixar ${curriculo.nome_referencia}`}
                    carregando={download.isPending && download.variables === curriculo.id}
                    onClick={() => baixar(curriculo)}
                  >
                    Baixar
                  </Button>
                  <Button
                    aria-label={`Remover ${curriculo.nome_referencia}`}
                    onClick={() => setParaRemover(curriculo)}
                  >
                    Remover
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </Panel>

      <EnviarCurriculoModal aberto={enviando} aoFechar={() => setEnviando(false)} />
      <ConfirmacaoModal
        aberto={paraRemover !== null}
        titulo="Remover currículo?"
        descricao={`“${paraRemover?.nome_referencia ?? ""}” será removido da biblioteca. Esta ação não pode ser desfeita.`}
        rotuloConfirmar="Remover"
        confirmando={remocao.isPending}
        aoConfirmar={confirmarRemocao}
        aoCancelar={() => setParaRemover(null)}
      />
    </>
  );
}
