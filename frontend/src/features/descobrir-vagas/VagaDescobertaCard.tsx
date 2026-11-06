import { useId } from "react";
import type { VagaDescoberta } from "../../api/tipos";
import { base64ParaBlob, baixarArquivo } from "../../shared/arquivos/arquivos";
import { formatarData } from "../../shared/formatacao";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { AnaliseAtsResultado } from "../ajustar-vaga/AnaliseAtsResultado";
import { CartaGerada } from "../ajustar-vaga/CartaGerada";
import estilos from "./DescobrirVagasPage.module.css";
import { useCandidatarVagaExterna } from "./use-descobrir-vagas";

const FONTES: Record<string, string> = {
  REMOTEOK: "RemoteOK",
  WE_WORK_REMOTELY: "We Work Remotely",
  ARBEITNOW: "Arbeitnow",
  ADZUNA: "Adzuna",
  GOOGLE_CUSTOM_SEARCH: "Google",
};

/** Fonte do currículo usada em "Candidatar": o currículo mestre, se existir; senão o PDF de referência. */
export type FonteCandidatura = { perfil_identificador: string } | { pdf_base64: string };

interface Props {
  vaga: VagaDescoberta;
  idioma: "pt" | "en";
  fonteCurriculo: FonteCandidatura;
}

export function VagaDescobertaCard({ vaga, idioma, fonteCurriculo }: Props) {
  const idTitulo = useId();
  const candidatar = useCandidatarVagaExterna();
  const requisitos = vaga.requisitos_faltantes ?? [];
  const publicacao = vaga.data_publicacao
    ? `Publicada em ${formatarData(vaga.data_publicacao)}`
    : "Data de publicação desconhecida";

  const enviarCandidatura = () =>
    candidatar.mutate({
      vaga: {
        titulo: vaga.titulo,
        empresa: vaga.empresa,
        descricao: vaga.descricao,
        url: vaga.url,
        fonte: vaga.fonte,
        data_publicacao: vaga.data_publicacao ?? null,
      },
      idioma_alvo: idioma,
      ...fonteCurriculo,
    });

  const resultado = candidatar.data;

  return (
    <article className={estilos.vaga} aria-labelledby={idTitulo}>
      <div className={estilos.topo}>
        <div>
          <h3 id={idTitulo} className={estilos.titulo}>
            {vaga.titulo}
          </h3>
          <p className={estilos.meta}>
            {[vaga.empresa, FONTES[vaga.fonte] ?? vaga.fonte, publicacao].join(" · ")}
          </p>
        </div>
        <div className={estilos.compatibilidade}>
          <span className={estilos.compatibilidadeValor}>{vaga.nota}</span>
          <span className={estilos.compatibilidadeRotulo}>compatibilidade</span>
        </div>
      </div>

      {requisitos.length === 0 ? (
        <p className={estilos.requisitos}>Todos os requisitos explícitos foram encontrados.</p>
      ) : (
        <details className={estilos.requisitos}>
          <summary>Requisitos não encontrados no currículo ({requisitos.length})</summary>
          <ul className={estilos.listaRequisitos}>
            {requisitos.map((requisito) => (
              <li key={requisito.nome}>{requisito.nome}</li>
            ))}
          </ul>
        </details>
      )}

      <div className={estilos.acoesVaga}>
        <a
          className={estilos.link}
          href={vaga.url}
          target="_blank"
          rel="noopener noreferrer"
          aria-label={`Ver vaga ${vaga.titulo} na fonte`}
        >
          Ver vaga <span aria-hidden="true">↗</span>
        </a>
        {!resultado && (
          <Button
            variante="primary"
            aria-label={`Candidatar em ${vaga.titulo}`}
            carregando={candidatar.isPending}
            onClick={enviarCandidatura}
          >
            {candidatar.isPending ? "Preparando… pode levar até 1 minuto" : "Candidatar"}
          </Button>
        )}
      </div>

      {candidatar.isError && <Aviso tom="erro">{candidatar.error.message}</Aviso>}

      {resultado && (
        <div className={estilos.candidatura} aria-live="polite">
          <div className={estilos.linhaCandidatura}>
            <strong>Nota ATS do currículo adaptado: {resultado.nota}/100</strong>
            <Button
              onClick={() =>
                baixarArquivo(base64ParaBlob(resultado.pdf_base64), resultado.nome_arquivo)
              }
            >
              Baixar PDF
            </Button>
          </div>
          <AnaliseAtsResultado
            analise={{ nota: resultado.nota, requisitos_faltantes: resultado.requisitos_faltantes }}
            mostrarSugestoes={false}
          />
          <CartaGerada texto={resultado.carta} cargo={vaga.titulo} empresa={vaga.empresa} />
          <a
            className={estilos.abrirVaga}
            href={resultado.url_vaga}
            target="_blank"
            rel="noopener noreferrer"
          >
            Abrir vaga para se candidatar <span aria-hidden="true">↗</span>
          </a>
        </div>
      )}
    </article>
  );
}
