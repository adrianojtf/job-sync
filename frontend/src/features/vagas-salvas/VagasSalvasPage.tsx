import { useState } from "react";
import { Link } from "react-router-dom";
import type { Vaga } from "../../api/tipos";
import { CabecalhoPagina } from "../../app/CabecalhoPagina";
import { dominioDaUrl, formatarData, primeiraLinha } from "../../shared/formatacao";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { EmptyState } from "../../shared/ui/EmptyState";
import { Panel } from "../../shared/ui/Panel";
import { ColarVagaModal } from "./ColarVagaModal";
import { CriarCandidaturaModal } from "./CriarCandidaturaModal";
import { DetalheVagaModal } from "./DetalheVagaModal";
import { useVagasSalvas } from "./use-vagas-salvas";
import estilos from "./VagasSalvasPage.module.css";

/** T7 — Vagas capturadas pela extensão ou coladas, ainda sem candidatura (JOB-0006, RF8.1–RF8.5). */
export function VagasSalvasPage() {
  const vagas = useVagasSalvas();
  const [colando, setColando] = useState(false);
  const [emDetalhe, setEmDetalhe] = useState<Vaga | null>(null);
  const [paraCandidatura, setParaCandidatura] = useState<Vaga | null>(null);
  const itens = vagas.data ?? [];

  return (
    <>
      <CabecalhoPagina
        titulo="Vagas salvas"
        descricao="Vagas capturadas pela extensão ou coladas aqui. Ao virar candidatura, a vaga sai desta lista."
        acoes={
          <Button variante="primary" onClick={() => setColando(true)}>
            <span aria-hidden="true">＋</span> Colar vaga
          </Button>
        }
      />

      <Panel
        titulo="Vagas"
        subtitulo={
          vagas.isSuccess ? `${itens.length} ${itens.length === 1 ? "vaga" : "vagas"}` : undefined
        }
      >
        {vagas.isPending && <p role="status">Carregando vagas…</p>}
        {vagas.isError && (
          <Aviso
            tom="erro"
            acao={<Button onClick={() => vagas.refetch()}>Tentar novamente</Button>}
          >
            Não foi possível carregar as vagas: {vagas.error.message}
          </Aviso>
        )}
        {vagas.isSuccess && itens.length === 0 && (
          <EmptyState titulo="Nenhuma vaga salva">
            Para capturar vagas enquanto navega,{" "}
            <Link to="/configuracoes">gere o token da extensão</Link>. Ou use “Colar vaga”.
          </EmptyState>
        )}
        {itens.length > 0 && (
          <ul className={estilos.lista}>
            {itens.map((vaga) => {
              const titulo = primeiraLinha(vaga.texto_descricao);
              const origem = dominioDaUrl(vaga.url_origem);
              return (
                <li key={vaga.id} className={estilos.item}>
                  <span className={estilos.marca} aria-hidden="true">
                    {(titulo[0] ?? "?").toUpperCase()}
                  </span>
                  <div className={estilos.info}>
                    <strong className={estilos.titulo}>{titulo}</strong>
                    <span className={estilos.meta}>
                      {[origem, `Salva em ${formatarData(vaga.data_captura)}`]
                        .filter(Boolean)
                        .join(" · ")}
                    </span>
                  </div>
                  <div className={estilos.acoes}>
                    <Button
                      aria-label={`Detalhes da vaga ${titulo}`}
                      onClick={() => setEmDetalhe(vaga)}
                    >
                      Detalhes
                    </Button>
                    <Button
                      aria-label={`Criar candidatura para ${titulo}`}
                      onClick={() => setParaCandidatura(vaga)}
                    >
                      Criar candidatura
                    </Button>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </Panel>

      <ColarVagaModal aberto={colando} aoFechar={() => setColando(false)} />
      <DetalheVagaModal
        vaga={emDetalhe}
        aoFechar={() => setEmDetalhe(null)}
        aoCriarCandidatura={setParaCandidatura}
      />
      <CriarCandidaturaModal vaga={paraCandidatura} aoFechar={() => setParaCandidatura(null)} />
    </>
  );
}
