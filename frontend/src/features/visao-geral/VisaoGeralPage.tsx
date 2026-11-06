import { useState } from "react";
import { Link } from "react-router-dom";
import type { PerfilEstruturado } from "../../api/tipos";
import { CabecalhoPagina } from "../../app/CabecalhoPagina";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Panel } from "../../shared/ui/Panel";
import { StatCard } from "../../shared/ui/StatCard";
import { StatusBadge } from "../../shared/ui/StatusBadge";
import { AjustarVagaModal } from "../ajustar-vaga/AjustarVagaModal";
import { ROTULO_STATUS, TOM_STATUS } from "../candidaturas/status";
import { useCandidaturas } from "../candidaturas/use-candidaturas";
import { useCurriculos } from "../curriculos/use-curriculos";
import { usePerfilEstruturado } from "../perfil/use-perfil-estruturado";
import { useVagasSalvas } from "../vagas-salvas/use-vagas-salvas";
import { dataPorExtenso, saudacao, tempoRelativo } from "./datas";
import {
  calcularCompletude,
  montarResumo,
  type Atividade,
  type ItemRecente,
} from "./montar-resumo";
import estilos from "./VisaoGeralPage.module.css";

const SEM_CANDIDATURAS = { por_status: {}, total: 0 };

/** T2 — Visão geral do protótipo: resumo da busca em uma tela (RF3.1–RF3.7). */
export function VisaoGeralPage() {
  const identificador = usePerfilAtivo();
  const [agora] = useState(() => new Date());
  const [ajustandoVaga, setAjustandoVaga] = useState(false);
  const perfil = usePerfilEstruturado();
  const curriculos = useCurriculos();
  const vagas = useVagasSalvas();
  const candidaturas = useCandidaturas();

  const consultas = [perfil, curriculos, vagas, candidaturas];
  const falhas = consultas.filter((consulta) => consulta.isError);
  const resumo = montarResumo({
    curriculos: curriculos.data ?? [],
    vagas: vagas.data ?? [],
    candidaturas: candidaturas.data ?? SEM_CANDIDATURAS,
  });
  const valor = (pronto: boolean, numero: number) => (pronto ? numero : "—");
  const primeiroNome = perfil.data?.nome_completo.trim().split(/\s+/)[0] || identificador;

  return (
    <>
      <CabecalhoPagina
        sobrelinha={dataPorExtenso(agora)}
        titulo={`${saudacao(agora)}, ${primeiroNome}`}
        descricao="Organize seus currículos e prepare a próxima candidatura."
        acoes={
          <Button variante="primary" onClick={() => setAjustandoVaga(true)}>
            <span aria-hidden="true">＋</span> Ajustar para uma vaga
          </Button>
        }
      />

      {falhas.length > 0 && (
        <Aviso
          tom="erro"
          acao={
            <Button onClick={() => falhas.forEach((consulta) => consulta.refetch())}>
              Tentar novamente
            </Button>
          }
        >
          Alguns dados não carregaram: {falhas[0]?.error?.message}
        </Aviso>
      )}

      {perfil.isSuccess && perfil.data === null && (
        <section className={estilos.boasVindas} aria-labelledby="titulo-boas-vindas">
          <div>
            <h2 id="titulo-boas-vindas">Complete seu currículo mestre</h2>
            <p>
              Ele é a base para adaptar currículos, analisar vagas e se candidatar sem enviar PDF
              toda vez.
            </p>
          </div>
          <Link className={`${estilos.botaoLink} ${estilos.botaoPrimario}`} to="/perfil">
            Preencher meu perfil
          </Link>
        </section>
      )}

      <section className={estilos.indicadores} aria-label="Indicadores">
        <StatCard
          rotulo="Currículos salvos"
          icone="▤"
          valor={valor(curriculos.isSuccess, resumo.curriculos)}
          rodape={perfil.data ? "Currículo mestre preenchido" : "Sem currículo mestre"}
        />
        <StatCard
          rotulo="Vagas salvas"
          icone="☆"
          valor={valor(vagas.isSuccess, resumo.vagasSalvas)}
          rodape="aguardando candidatura"
        />
        <StatCard
          rotulo="Candidaturas ativas"
          icone="↗"
          valor={valor(candidaturas.isSuccess, resumo.candidaturasAtivas)}
          rodape={`${resumo.aguardandoRetorno} aguardando retorno`}
        />
        <StatCard
          rotulo="Em entrevista ou oferta"
          icone="◉"
          valor={valor(candidaturas.isSuccess, resumo.emEntrevistaOuOferta)}
          rodape={
            resumo.comOferta > 0 ? (
              <span className={estilos.positivo}>
                {resumo.comOferta} {resumo.comOferta === 1 ? "oferta" : "ofertas"}
              </span>
            ) : (
              "nenhuma oferta ainda"
            )
          }
        />
      </section>

      <div className={estilos.layout}>
        <Panel
          titulo="Suas vagas recentes"
          subtitulo="Candidaturas e vagas salvas, das mais novas para as mais antigas"
          acoes={
            <Link
              to="/candidaturas"
              style={{ color: "var(--accent)", fontWeight: 650, fontSize: 12 }}
            >
              Ver candidaturas <span aria-hidden="true">→</span>
            </Link>
          }
        >
          <ItensRecentes
            itens={resumo.itensRecentes}
            agora={agora}
            carregando={vagas.isPending || candidaturas.isPending}
          />
        </Panel>

        <div className={estilos.colunaDireita}>
          <CurriculoPrincipal perfil={perfil.data ?? null} carregando={perfil.isPending} />
          <aside className={estilos.dica} aria-labelledby="titulo-dica">
            <div className={estilos.dicaRotulo}>Dica de carreira</div>
            <h2 id="titulo-dica">Adapte, não reinvente.</h2>
            <p>Use o currículo mestre como base e ajuste para o que cada vaga pede:</p>
            <ol aria-label="Fluxo sugerido">
              <li>Preencha ou importe o currículo mestre.</li>
              <li>Analise a vaga.</li>
              <li>Revise a nota ATS e as sugestões.</li>
              <li>Baixe o PDF adaptado e a carta.</li>
            </ol>
          </aside>
        </div>
      </div>

      <div className={estilos.atividade}>
        <Panel titulo="Atividade recente">
          <Atividades atividades={resumo.atividades} agora={agora} />
        </Panel>
      </div>

      <AjustarVagaModal aberto={ajustandoVaga} aoFechar={() => setAjustandoVaga(false)} />
    </>
  );
}

function ItensRecentes({
  itens,
  agora,
  carregando,
}: {
  itens: ItemRecente[];
  agora: Date;
  carregando: boolean;
}) {
  if (carregando) return <p className={estilos.vazio}>Carregando…</p>;
  if (itens.length === 0) {
    return (
      <p className={estilos.vazio}>
        Nenhuma vaga ainda. <Link to="/vagas-salvas">Salve uma vaga</Link> ou{" "}
        <Link to="/descobrir-vagas">descubra novas</Link>.
      </p>
    );
  }
  return (
    <ul className={estilos.lista}>
      {itens.map((item) => (
        <li key={`${item.tipo}-${item.id}`} className={estilos.item}>
          <span
            className={`${estilos.letra} ${item.tipo === "candidatura" ? estilos.letraCandidatura : estilos.letraVaga}`}
            aria-hidden="true"
          >
            {(item.subtitulo[0] ?? item.titulo[0] ?? "?").toUpperCase()}
          </span>
          <div className={estilos.info}>
            <Link className={estilos.titulo} to={item.destino}>
              {item.titulo}
            </Link>
            <span className={estilos.meta}>
              {item.subtitulo} · {tempoRelativo(item.data, agora)}
            </span>
          </div>
          {item.status ? (
            <StatusBadge tom={TOM_STATUS[item.status]}>{ROTULO_STATUS[item.status]}</StatusBadge>
          ) : (
            <StatusBadge>Sem candidatura</StatusBadge>
          )}
        </li>
      ))}
    </ul>
  );
}

function CurriculoPrincipal({
  perfil,
  carregando,
}: {
  perfil: PerfilEstruturado | null;
  carregando: boolean;
}) {
  const completude = calcularCompletude(perfil);
  return (
    <Panel
      titulo="Currículo principal"
      acoes={perfil && <StatusBadge tom="sucesso">Salvo</StatusBadge>}
    >
      {carregando ? (
        <p className={estilos.vazio}>Carregando…</p>
      ) : perfil ? (
        <>
          <div className={estilos.previa}>
            <div className={estilos.previaNome}>{perfil.nome_completo}</div>
            <div className={estilos.previaCargo}>
              {perfil.experiencias?.[0]?.cargo ?? "Cargo não informado"}
            </div>
            <div aria-hidden="true">
              <div className={estilos.linhaFalsa} />
              <div className={`${estilos.linhaFalsa} ${estilos.linhaMedia}`} />
              <div className={`${estilos.linhaFalsa} ${estilos.linhaCurta}`} />
            </div>
          </div>
          <div className={estilos.completude}>
            <span>Perfil preenchido</span>
            <strong>{completude}%</strong>
          </div>
          <div
            className={estilos.barra}
            role="progressbar"
            aria-label="Completude do currículo mestre"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={completude}
          >
            <span className={estilos.barraValor} style={{ width: `${completude}%` }} />
          </div>
          <Link className={`${estilos.botaoLink} ${estilos.botaoSecundario}`} to="/perfil">
            Editar currículo
          </Link>
        </>
      ) : (
        <p className={estilos.vazio}>
          Nenhum currículo mestre ainda. <Link to="/perfil">Começar agora</Link>.
        </p>
      )}
    </Panel>
  );
}

const CLASSE_PONTO: Record<Atividade["tipo"], string> = {
  status_candidatura: estilos.pontoCandidatura!,
  curriculo_salvo: estilos.pontoCurriculo!,
  vaga_capturada: estilos.pontoVaga!,
};

function Atividades({ atividades, agora }: { atividades: Atividade[]; agora: Date }) {
  if (atividades.length === 0) return <p className={estilos.vazio}>Nenhuma atividade ainda.</p>;
  return (
    <ul className={estilos.lista}>
      {atividades.map((atividade) => (
        <li
          key={`${atividade.tipo}-${atividade.data}-${atividade.descricao}`}
          className={estilos.evento}
        >
          <span className={`${estilos.ponto} ${CLASSE_PONTO[atividade.tipo]}`} aria-hidden="true" />
          <span>{atividade.descricao}</span>
          <time dateTime={atividade.data}>{tempoRelativo(atividade.data, agora)}</time>
        </li>
      ))}
    </ul>
  );
}
