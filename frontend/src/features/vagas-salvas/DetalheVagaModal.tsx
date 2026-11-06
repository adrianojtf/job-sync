import { useNavigate } from "react-router-dom";
import type { Vaga } from "../../api/tipos";
import { AvaliacaoVagaResultado } from "../ajustar-vaga/AvaliacaoVagaResultado";
import {
  ROTA_AJUSTAR_VAGA,
  ROTA_ANALISAR_ATS,
  type EstadoAjustarVaga,
  type EstadoAnalisarAts,
} from "../ajustar-vaga/navegacao";
import { formatarData, primeiraLinha } from "../../shared/formatacao";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Modal } from "../../shared/ui/Modal";
import { useAvaliarDescricaoVaga } from "./use-vagas-salvas";
import estilos from "./VagasSalvasPage.module.css";

interface Props {
  vaga: Vaga | null;
  aoFechar: () => void;
  aoCriarCandidatura: (vaga: Vaga) => void;
}

/** RF8.3 e RF8.5 — descrição completa, avaliação e atalhos para os fluxos de currículo. */
export function DetalheVagaModal({ vaga, aoFechar, aoCriarCandidatura }: Props) {
  const navegar = useNavigate();
  const avaliacao = useAvaliarDescricaoVaga();

  const fechar = () => {
    avaliacao.reset();
    aoFechar();
  };

  if (!vaga) return <Modal aberto={false} titulo="" aoFechar={fechar} />;

  const titulo = primeiraLinha(vaga.texto_descricao, 120);

  const ajustarCurriculo = () => {
    const estado: EstadoAjustarVaga = {
      cargo: titulo,
      descricao: vaga.texto_descricao,
      pedido: Date.now(),
    };
    fechar();
    navegar(ROTA_AJUSTAR_VAGA, { state: estado });
  };

  const analisarAts = () => {
    const estado: EstadoAnalisarAts = { descricao: vaga.texto_descricao };
    fechar();
    navegar(ROTA_ANALISAR_ATS, { state: estado });
  };

  return (
    <Modal
      aberto
      titulo={titulo}
      descricao={`Salva em ${formatarData(vaga.data_captura)}`}
      aoFechar={fechar}
      rodape={
        <>
          <Button onClick={analisarAts}>Analisar ATS</Button>
          <Button onClick={ajustarCurriculo}>Ajustar currículo</Button>
          <Button
            variante="primary"
            onClick={() => {
              fechar();
              aoCriarCandidatura(vaga);
            }}
          >
            Criar candidatura
          </Button>
        </>
      }
    >
      <p className={estilos.descricao}>{vaga.texto_descricao}</p>
      {vaga.url_origem && (
        <a
          className={estilos.linkOriginal}
          href={vaga.url_origem}
          target="_blank"
          rel="noopener noreferrer"
        >
          Abrir vaga original <span aria-hidden="true">↗</span>
        </a>
      )}

      <div className={estilos.secao}>
        {avaliacao.isError && <Aviso tom="erro">{avaliacao.error.message}</Aviso>}
        {avaliacao.data ? (
          <AvaliacaoVagaResultado avaliacao={avaliacao.data} />
        ) : (
          <Button
            variante="text"
            carregando={avaliacao.isPending}
            onClick={() => avaliacao.mutate(vaga.texto_descricao)}
          >
            {avaliacao.isPending ? "Avaliando…" : "Avaliar descrição"}
          </Button>
        )}
      </div>
    </Modal>
  );
}
