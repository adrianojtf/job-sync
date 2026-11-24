import { useEffect, useId, useRef, useState } from "react";
import { useForm, useWatch } from "react-hook-form";
import { Link, useLocation, useNavigate } from "react-router-dom";
import type {
  AdaptarCurriculoEntrada,
  CurriculoAdaptadoPdf,
  DadosVaga,
  Lacuna,
  RascunhoAdaptado,
  RascunhoCurriculoAdaptado,
} from "../../api/tipos";
import { CabecalhoPagina } from "../../app/CabecalhoPagina";
import { AvisoAlteracoesNaoSalvas } from "../../shared/formulario-curriculo/AvisoAlteracoesNaoSalvas";
import { base64ParaBlob, baixarArquivo } from "../../shared/arquivos/arquivos";
import { CampoLinkVaga } from "../../shared/leitura-de-vaga/CampoLinkVaga";
import { PreencherPeloTexto } from "../../shared/leitura-de-vaga/PreencherPeloTexto";
import type { CampoIdentificacao } from "../../shared/leitura-de-vaga/resumo-da-leitura";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Panel } from "../../shared/ui/Panel";
import { ScoreDimensions } from "../../shared/ui/ScoreDimensions";
import estilos from "./AjustarVagaPage.module.css";
import { AnaliseAtsResultado } from "./AnaliseAtsResultado";
import { AvaliacaoVagaResultado } from "./AvaliacaoVagaResultado";
import { CartaGerada } from "./CartaGerada";
import { FONTE_PERFIL, useFontesCurriculo } from "./fonte-curriculo";
import type { EstadoAjustarVaga } from "./navegacao";
import { PerguntasSobreAVaga } from "./PerguntasSobreAVaga";
import resultados from "./Resultados.module.css";
import { RevisaoCurriculoAdaptado } from "./RevisaoCurriculoAdaptado";
import { SeletorFonteCurriculo } from "./SeletorFonteCurriculo";
import { usePerfilEstruturado } from "../perfil/use-perfil-estruturado";
import { useAjustarVaga } from "./use-ajustar-vaga";

interface EntradaDaAdaptacao {
  curriculoId: string;
  dados: AdaptarCurriculoEntrada;
}

/** Perguntas sobre a vaga em andamento e o pedido de adaptação que elas liberam (JOB-0043). */
interface PerguntasEmAndamento {
  lacunas: Lacuna[];
  entrada: EntradaDaAdaptacao;
}

interface Formulario {
  cargo: string;
  empresa: string;
  descricao: string;
  idioma: "pt" | "en";
  fonte: string;
}

const IDIOMAS = [
  { valor: "pt", rotulo: "Português" },
  { valor: "en", rotulo: "Inglês" },
];
const AVISO_DEMORA = "pode levar até 1 minuto";
/** Campos de identificação desta tela: a leitura da vaga avisa o que preencheu entre eles. */
const CAMPOS_LIDOS: CampoIdentificacao[] = ["cargo", "empresa"];
const obrigatorio = (mensagem: string) => ({
  validate: (valor: string) => valor.trim() !== "" || mensagem,
});

/**
 * T5 — Ajustar para uma vaga (RF6.1–RF6.5). Um novo pedido vindo do modal recomeça o fluxo.
 * O currículo adaptado passa por revisão antes do PDF (JOB-0033): vaga → revisão → resultado.
 */
export function AjustarVagaPage() {
  const estado = (useLocation().state ?? {}) as EstadoAjustarVaga;
  return <FluxoAjustarVaga key={estado.pedido ?? "inicial"} estado={estado} />;
}

function FluxoAjustarVaga({ estado }: { estado: EstadoAjustarVaga }) {
  const fontes = useFontesCurriculo();
  const perfilEstruturado = usePerfilEstruturado();
  const {
    avaliar,
    lacunas,
    gerarRascunho,
    salvarAdaptado,
    atualizarAdaptado,
    ats,
    carta,
    confirmarCandidatura,
  } = useAjustarVaga();
  // Dados da vaga usados na adaptação em revisão; null fora da etapa de revisão.
  const [vagaEmRevisao, setVagaEmRevisao] = useState<AdaptarCurriculoEntrada | null>(null);
  // Vaga que gerou o PDF atual: a candidatura leva esses dados, não o formulário (editável depois).
  const [vagaDoPdf, setVagaDoPdf] = useState<AdaptarCurriculoEntrada | null>(null);
  // Currículo adaptado salvo (JOB-0041): o PDF atual, o rascunho que o gerou e se está em edição.
  const [pdfAtual, setPdfAtual] = useState<CurriculoAdaptadoPdf | null>(null);
  const [rascunhoSalvo, setRascunhoSalvo] = useState<RascunhoCurriculoAdaptado | null>(null);
  const [editando, setEditando] = useState(false);
  // Perguntas sobre a vaga (JOB-0043): o pedido guardado vale enquanto o candidato as responde ou
  // enquanto as lacunas carregam; pular descarta qualquer resposta que chegar depois.
  const [perguntas, setPerguntas] = useState<PerguntasEmAndamento | null>(null);
  const pedidoEmEspera = useRef<EntradaDaAdaptacao | null>(null);
  const perguntasDispensadas = useRef(false);
  const form = useForm<Formulario>({
    defaultValues: {
      cargo: estado.cargo ?? "",
      empresa: estado.empresa ?? "",
      descricao: estado.descricao ?? "",
      idioma: "pt",
      fonte: "",
    },
  });
  const { errors, isDirty } = form.formState;
  const [linkDaVaga, setLinkDaVaga] = useState("");
  const descricaoDigitada = useWatch({ control: form.control, name: "descricao" });
  // A leitura da vaga (link ou texto) é um rascunho: preenche o que encontrou e mantém o que a
  // pessoa já digitou quando não encontra título ou empresa. Os campos seguem editáveis.
  const preencherComDadosLidos = (dados: DadosVaga) => {
    const opcoes = { shouldDirty: true, shouldValidate: true };
    if (dados.cargo) form.setValue("cargo", dados.cargo, opcoes);
    if (dados.empresa) form.setValue("empresa", dados.empresa, opcoes);
    form.setValue("descricao", dados.descricao, opcoes);
  };
  // O texto digitado conta como enviado depois que a IA o usou: só avisa por texto ainda não enviado.
  const marcarComoEnviado = () => form.reset(form.getValues());

  const { padrao } = fontes;
  useEffect(() => {
    if (padrao && !form.getValues("fonte")) form.setValue("fonte", padrao);
  }, [padrao, form]);

  const analisarVaga = async () => {
    if (!(await form.trigger("descricao"))) return;
    avaliar.mutate(form.getValues("descricao").trim(), { onSuccess: marcarComoEnviado });
  };

  // Análise automática pedida pelo modal, feita uma única vez:
  // - agendada e cancelável: no StrictMode a 1ª montagem é desfeita e só a definitiva dispara
  //   (disparar direto no efeito perdia o resultado, pois a desmontagem desliga o observador);
  // - depois de disparar, a instrução é consumida no histórico (replace, mesmo `pedido`), então
  //   recarregar ou voltar para a página não chama a IA de novo e a tela não é remontada.
  const navegar = useNavigate();
  const { pathname } = useLocation();
  const analisouAoAbrir = useRef(false);
  const { mutate: avaliarVaga } = avaliar;
  useEffect(() => {
    if (!estado.analisarAoAbrir || analisouAoAbrir.current) return;
    const agendamento = setTimeout(() => {
      analisouAoAbrir.current = true;
      avaliarVaga((estado.descricao ?? "").trim());
      const estadoConsumido: EstadoAjustarVaga = { ...estado, analisarAoAbrir: false };
      navegar(pathname, { replace: true, state: estadoConsumido });
    }, 0);
    return () => clearTimeout(agendamento);
  }, [estado, avaliarVaga, navegar, pathname]);

  const montarEntrada = async (): Promise<EntradaDaAdaptacao> => {
    const valores = form.getValues();
    const { curriculoId, ...fonte } = await fontes.resolver(valores.fonte);
    return {
      curriculoId,
      dados: {
        descricao_vaga: valores.descricao.trim(),
        cargo_alvo: valores.cargo.trim(),
        empresa_alvo: valores.empresa.trim(),
        idioma_alvo: valores.idioma,
        ...fonte,
      },
    };
  };

  const gerarCurriculo = async () => {
    if (!(await form.trigger(["cargo", "empresa", "descricao"]))) return;
    limparCurriculoSalvo();
    const entrada = await montarEntrada();
    // Só o perfil estruturado tem experiências para comparar com a vaga.
    if (form.getValues("fonte") !== FONTE_PERFIL) {
      iniciarGeracao(entrada);
      return;
    }
    pedidoEmEspera.current = entrada;
    perguntasDispensadas.current = false;
    lacunas.mutate(
      {
        perfil_identificador: entrada.dados.perfil_identificador ?? "",
        descricao_vaga: entrada.dados.descricao_vaga,
        cargo_alvo: entrada.dados.cargo_alvo,
        idioma_alvo: entrada.dados.idioma_alvo,
      },
      {
        onSuccess: ({ lacunas: itens }) => {
          if (perguntasDispensadas.current) return;
          if (itens.length > 0) setPerguntas({ lacunas: itens, entrada });
          else iniciarGeracao(entrada);
        },
        // As perguntas nunca bloqueiam a geração: sem elas, o currículo sai como antes.
        onError: () => {
          if (!perguntasDispensadas.current) iniciarGeracao(entrada);
        },
      },
    );
  };

  function iniciarGeracao(entrada: EntradaDaAdaptacao) {
    setPerguntas(null);
    gerarRascunho.mutate(entrada, {
      onSuccess: (_rascunho, enviada) => {
        marcarComoEnviado();
        setVagaEmRevisao(enviada.dados);
      },
    });
  }

  const pularPerguntas = () => {
    perguntasDispensadas.current = true;
    const entrada = perguntas?.entrada ?? pedidoEmEspera.current;
    if (entrada) iniciarGeracao(entrada);
  };

  function limparCurriculoSalvo() {
    salvarAdaptado.reset();
    atualizarAdaptado.reset();
    confirmarCandidatura.reset();
    setPdfAtual(null);
    setRascunhoSalvo(null);
    setEditando(false);
  }

  const confirmarRevisao = (
    vaga: AdaptarCurriculoEntrada,
    rascunho: RascunhoCurriculoAdaptado,
    analise: RascunhoAdaptado["analise_vaga"],
  ) =>
    salvarAdaptado.mutate(
      {
        rascunho,
        idioma_alvo: vaga.idioma_alvo,
        cargo_alvo: vaga.cargo_alvo,
        empresa_alvo: vaga.empresa_alvo,
        descricao_vaga: vaga.descricao_vaga,
        analise_vaga: analise,
      },
      {
        onSuccess: (pdf) => {
          setVagaEmRevisao(null);
          setVagaDoPdf(vaga);
          setPdfAtual(pdf);
          setRascunhoSalvo(rascunho);
          confirmarCandidatura.reset();
        },
      },
    );

  const salvarEdicao = (id: string, rascunho: RascunhoCurriculoAdaptado) =>
    atualizarAdaptado.mutate(
      { id, rascunho },
      {
        onSuccess: (pdf) => {
          setPdfAtual(pdf);
          setRascunhoSalvo(rascunho);
          setEditando(false);
        },
      },
    );

  const confirmarCandidaturaDoPdf = (pdf: CurriculoAdaptadoPdf, vaga: AdaptarCurriculoEntrada) =>
    confirmarCandidatura.mutate({
      cargo: vaga.cargo_alvo,
      empresa: vaga.empresa_alvo,
      descricao_vaga: vaga.descricao_vaga,
      nome_arquivo: pdf.nome_arquivo,
      pdf_base64: pdf.pdf_base64,
      curriculo_adaptado_id: pdf.id,
    });

  const descartarRevisao = () => {
    gerarRascunho.reset();
    limparCurriculoSalvo();
    setVagaEmRevisao(null);
  };

  const analisarAts = async () => {
    if (!(await form.trigger("descricao"))) return;
    const { curriculoId, ...fonte } = await fontes.resolver(form.getValues("fonte"));
    ats.mutate(
      { curriculoId, dados: { descricao_vaga: form.getValues("descricao").trim(), ...fonte } },
      { onSuccess: marcarComoEnviado },
    );
  };

  const gerarCarta = async () => {
    if (!(await form.trigger(["cargo", "empresa", "descricao"]))) return;
    carta.mutate((await montarEntrada()).dados);
  };

  const semFonte = !fontes.carregando && fontes.opcoes.length === 0;
  const adaptado = gerarRascunho.data;
  const avaliacaoVaga = avaliar.data ?? adaptado?.avaliacao_vaga ?? null;
  const cabecalho = (
    <CabecalhoPagina
      titulo="Ajustar para uma vaga"
      descricao="Analise a vaga, gere um currículo adaptado e prepare a candidatura."
    />
  );

  if (perguntas) {
    return (
      <>
        {cabecalho}
        <PerguntasSobreAVaga
          lacunas={perguntas.lacunas}
          experiencias={perfilEstruturado.data?.experiencias ?? []}
          idiomaAlvo={perguntas.entrada.dados.idioma_alvo}
          aoConcluir={() => iniciarGeracao(perguntas.entrada)}
          aoPular={pularPerguntas}
        />
      </>
    );
  }

  if (vagaEmRevisao && adaptado) {
    return (
      <>
        {cabecalho}
        <RevisaoCurriculoAdaptado
          rascunho={adaptado.rascunho}
          contextoVaga={{
            descricao_vaga: vagaEmRevisao.descricao_vaga,
            idioma_alvo: vagaEmRevisao.idioma_alvo,
            analise_vaga: adaptado.analise_vaga,
            cargo_alvo: vagaEmRevisao.cargo_alvo,
          }}
          gerando={salvarAdaptado.isPending}
          erro={salvarAdaptado.error?.message}
          aoConfirmar={(rascunho) =>
            confirmarRevisao(vagaEmRevisao, rascunho, adaptado.analise_vaga)
          }
          aoVoltar={descartarRevisao}
        />
      </>
    );
  }

  if (editando && pdfAtual && rascunhoSalvo && vagaDoPdf && adaptado) {
    return (
      <>
        {cabecalho}
        <RevisaoCurriculoAdaptado
          modo="edicao"
          rascunho={rascunhoSalvo}
          contextoVaga={{
            descricao_vaga: vagaDoPdf.descricao_vaga,
            idioma_alvo: vagaDoPdf.idioma_alvo,
            analise_vaga: adaptado.analise_vaga,
            cargo_alvo: vagaDoPdf.cargo_alvo,
          }}
          gerando={atualizarAdaptado.isPending}
          erro={atualizarAdaptado.error?.message}
          aoConfirmar={(rascunho) => salvarEdicao(pdfAtual.id, rascunho)}
          aoVoltar={() => {
            atualizarAdaptado.reset();
            setEditando(false);
          }}
        />
      </>
    );
  }

  return (
    <>
      {cabecalho}
      <AvisoAlteracoesNaoSalvas alterado={isDirty} />

      <div className={estilos.layout}>
        <Panel titulo="Dados da vaga">
          <form noValidate onSubmit={(evento) => evento.preventDefault()}>
            <CampoLinkVaga
              valor={linkDaVaga}
              aoAlterar={setLinkDaVaga}
              aoLer={preencherComDadosLidos}
              campos={CAMPOS_LIDOS}
            />
            <div className={estilos.grade}>
              <Field
                rotulo="Título da vaga"
                placeholder="Ex.: Senior Java Backend Developer"
                erro={errors.cargo?.message}
                {...form.register("cargo", obrigatorio("Informe o título da vaga."))}
              />
              <Field
                rotulo="Empresa"
                placeholder="Ex.: Olist"
                erro={errors.empresa?.message}
                {...form.register(
                  "empresa",
                  obrigatorio("Informe a empresa (usada no nome do arquivo)."),
                )}
              />
              <div className={estilos.larguraTotal}>
                <Field
                  tipoCampo="textarea"
                  rotulo="Descrição da vaga"
                  placeholder="Cole aqui a descrição completa da oportunidade…"
                  erro={errors.descricao?.message}
                  {...form.register("descricao", obrigatorio("Cole a descrição da vaga."))}
                />
                <PreencherPeloTexto
                  texto={descricaoDigitada}
                  aoLer={preencherComDadosLidos}
                  campos={CAMPOS_LIDOS}
                />
              </div>
              <Field
                tipoCampo="select"
                rotulo="Idioma do currículo"
                opcoes={IDIOMAS}
                {...form.register("idioma")}
              />
              <SeletorFonteCurriculo
                opcoes={fontes.opcoes}
                carregando={fontes.carregando}
                {...form.register("fonte")}
              />
            </div>
            <div className={estilos.acoes}>
              <Button carregando={avaliar.isPending} onClick={analisarVaga}>
                {avaliar.isPending ? "Analisando vaga…" : "Analisar vaga"}
              </Button>
              {lacunas.isPending && !gerarRascunho.isPending && (
                <Button variante="text" onClick={pularPerguntas}>
                  Pular perguntas e gerar
                </Button>
              )}
              <Button
                variante="primary"
                disabled={semFonte}
                carregando={gerarRascunho.isPending || lacunas.isPending}
                onClick={gerarCurriculo}
              >
                {gerarRascunho.isPending
                  ? `Gerando… ${AVISO_DEMORA}`
                  : lacunas.isPending
                    ? "Buscando perguntas…"
                    : "Gerar currículo adaptado"}
              </Button>
            </div>
          </form>
        </Panel>

        <div className={estilos.resultados}>
          <Panel
            titulo="Avaliação da vaga"
            subtitulo="Completude, clareza, relevância e inclusão da descrição"
          >
            {avaliar.isError && <Aviso tom="erro">{avaliar.error.message}</Aviso>}
            {adaptado?.status_avaliacao_vaga === "indisponivel" && !avaliar.data && (
              <Aviso tom="alerta">
                A avaliação automática da vaga não está disponível agora. O currículo foi gerado
                normalmente.
              </Aviso>
            )}
            {avaliacaoVaga ? (
              <AvaliacaoVagaResultado avaliacao={avaliacaoVaga} />
            ) : (
              !avaliar.isError && (
                <p className={resultados.texto}>Clique em “Analisar vaga” para ver a avaliação.</p>
              )
            )}
          </Panel>

          <Panel titulo="Currículo adaptado">
            {gerarRascunho.isError && <Aviso tom="erro">{gerarRascunho.error.message}</Aviso>}
            {adaptado && pdfAtual ? (
              <CurriculoGerado
                pdf={pdfAtual}
                adaptado={adaptado}
                aoEditar={() => setEditando(true)}
                confirmacao={{
                  pendente: confirmarCandidatura.isPending,
                  confirmada: confirmarCandidatura.isSuccess,
                  erro: confirmarCandidatura.error?.message,
                }}
                aoConfirmar={() => vagaDoPdf && confirmarCandidaturaDoPdf(pdfAtual, vagaDoPdf)}
              />
            ) : (
              !gerarRascunho.isError && (
                <p className={resultados.texto}>
                  O PDF adaptado aparece aqui depois de “Gerar currículo adaptado” e da revisão.
                </p>
              )
            )}
          </Panel>

          <Panel
            titulo="Aderência ATS"
            acoes={
              <Button
                variante="text"
                disabled={semFonte}
                carregando={ats.isPending}
                onClick={analisarAts}
              >
                {ats.isPending ? "Analisando…" : "Analisar aderência ATS"}
              </Button>
            }
          >
            {ats.isError && <Aviso tom="erro">{ats.error.message}</Aviso>}
            {ats.data ? (
              <AnaliseAtsResultado analise={ats.data} />
            ) : (
              !ats.isError && (
                <p className={resultados.texto}>Veja a nota e os requisitos não cobertos.</p>
              )
            )}
          </Panel>

          <Panel
            titulo="Carta de apresentação"
            acoes={
              <Button
                variante="text"
                disabled={semFonte}
                carregando={carta.isPending}
                onClick={gerarCarta}
              >
                {carta.isPending ? `Gerando… ${AVISO_DEMORA}` : "Gerar carta de apresentação"}
              </Button>
            }
          >
            {carta.isError && <Aviso tom="erro">{carta.error.message}</Aviso>}
            {carta.data ? (
              <CartaGerada
                texto={carta.data.carta}
                cargo={form.getValues("cargo")}
                empresa={form.getValues("empresa")}
              />
            ) : (
              !carta.isError && (
                <p className={resultados.texto}>Gere uma carta personalizada para esta vaga.</p>
              )
            )}
          </Panel>
        </div>
      </div>
    </>
  );
}

interface ConfirmacaoCandidatura {
  pendente: boolean;
  confirmada: boolean;
  erro?: string;
}

function CurriculoGerado({
  pdf,
  adaptado,
  confirmacao,
  aoConfirmar,
  aoEditar,
}: {
  pdf: CurriculoAdaptadoPdf;
  adaptado: RascunhoAdaptado;
  confirmacao: ConfirmacaoCandidatura;
  aoConfirmar: () => void;
  aoEditar: () => void;
}) {
  const idTitulo = useId();
  const baixar = () => baixarArquivo(base64ParaBlob(pdf.pdf_base64), pdf.nome_arquivo);
  const avaliacoes = adaptado.avaliacoes_experiencias ?? [];
  // O botão confirmado fica desabilitado e perderia o foco: ele passa para a mensagem de sucesso.
  const mensagemConfirmada = useRef<HTMLParagraphElement>(null);
  useEffect(() => {
    if (confirmacao.confirmada) mensagemConfirmada.current?.focus();
  }, [confirmacao.confirmada]);
  const rotuloConfirmar = confirmacao.pendente
    ? "Confirmando candidatura…"
    : confirmacao.confirmada
      ? "Candidatura confirmada"
      : "Confirmar candidatura";
  return (
    <div aria-live="polite">
      <div className={estilos.arquivo}>
        <span className={estilos.nomeArquivo}>{pdf.nome_arquivo}</span>
        <div className={estilos.acoesArquivo}>
          <Button
            carregando={confirmacao.pendente}
            disabled={confirmacao.confirmada}
            onClick={aoConfirmar}
          >
            {rotuloConfirmar}
          </Button>
          <Button onClick={aoEditar}>Editar currículo</Button>
          <Button variante="primary" onClick={baixar}>
            Baixar PDF
          </Button>
        </div>
      </div>
      {confirmacao.confirmada && (
        <p ref={mensagemConfirmada} role="status" tabIndex={-1} className={estilos.confirmacao}>
          Candidatura confirmada em Aplicado. <Link to="/candidaturas">Ver no board</Link>
        </p>
      )}
      {confirmacao.erro && <Aviso tom="erro">{confirmacao.erro}</Aviso>}
      {avaliacoes.length > 0 && (
        <section aria-labelledby={idTitulo}>
          <h3 id={idTitulo} className={resultados.subtitulo}>
            Avaliação das experiências
          </h3>
          <div className={resultados.experiencias}>
            {avaliacoes.map(({ experiencia, status, avaliacao }, indice) => (
              <div key={indice} className={resultados.experiencia}>
                <p className={resultados.experienciaTitulo}>
                  <strong>
                    {experiencia.cargo} · {experiencia.empresa}
                  </strong>
                </p>
                {status === "avaliada" && avaliacao ? (
                  <ScoreDimensions
                    score={avaliacao.score}
                    dimensoes={[
                      { nome: "Clareza da escrita", ...avaliacao.clareza_escrita },
                      { nome: "Qualidade do detalhe", ...avaliacao.qualidade_detalhe },
                      { nome: "Aderência à vaga", ...avaliacao.aderencia_vaga },
                      { nome: "Consistência textual", ...avaliacao.consistencia_textual },
                    ]}
                  />
                ) : (
                  <p className={resultados.texto}>Avaliação indisponível para esta experiência.</p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
