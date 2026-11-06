import { useEffect, useId, useRef } from "react";
import { useForm } from "react-hook-form";
import { useLocation, useNavigate } from "react-router-dom";
import type { AdaptarCurriculoEntrada, CurriculoAdaptado } from "../../api/tipos";
import { CabecalhoPagina } from "../../app/CabecalhoPagina";
import { base64ParaBlob, baixarArquivo } from "../../shared/arquivos/arquivos";
import { paraSlug } from "../../shared/formatacao";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Panel } from "../../shared/ui/Panel";
import { ScoreDimensions } from "../../shared/ui/ScoreDimensions";
import { useToast } from "../../shared/ui/use-toast";
import estilos from "./AjustarVagaPage.module.css";
import { AnaliseAtsResultado } from "./AnaliseAtsResultado";
import { AvaliacaoVagaResultado } from "./AvaliacaoVagaResultado";
import { useFontesCurriculo } from "./fonte-curriculo";
import type { EstadoAjustarVaga } from "./navegacao";
import resultados from "./Resultados.module.css";
import { SeletorFonteCurriculo } from "./SeletorFonteCurriculo";
import { useAjustarVaga } from "./use-ajustar-vaga";

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
const obrigatorio = (mensagem: string) => ({
  validate: (valor: string) => valor.trim() !== "" || mensagem,
});

/** T5 — Ajustar para uma vaga (RF6.1–RF6.5). Um novo pedido vindo do modal recomeça o fluxo. */
export function AjustarVagaPage() {
  const estado = (useLocation().state ?? {}) as EstadoAjustarVaga;
  return <FluxoAjustarVaga key={estado.pedido ?? "inicial"} estado={estado} />;
}

function FluxoAjustarVaga({ estado }: { estado: EstadoAjustarVaga }) {
  const { notificar } = useToast();
  const fontes = useFontesCurriculo();
  const { avaliar, adaptar, ats, carta } = useAjustarVaga();
  const form = useForm<Formulario>({
    defaultValues: {
      cargo: estado.cargo ?? "",
      empresa: estado.empresa ?? "",
      descricao: estado.descricao ?? "",
      idioma: "pt",
      fonte: "",
    },
  });
  const { errors } = form.formState;

  const { padrao } = fontes;
  useEffect(() => {
    if (padrao && !form.getValues("fonte")) form.setValue("fonte", padrao);
  }, [padrao, form]);

  const analisarVaga = async () => {
    if (!(await form.trigger("descricao"))) return;
    avaliar.mutate(form.getValues("descricao").trim());
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

  const montarEntrada = async (): Promise<{
    curriculoId: string;
    dados: AdaptarCurriculoEntrada;
  }> => {
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
    adaptar.mutate(await montarEntrada());
  };

  const analisarAts = async () => {
    if (!(await form.trigger("descricao"))) return;
    const { curriculoId, ...fonte } = await fontes.resolver(form.getValues("fonte"));
    ats.mutate({
      curriculoId,
      dados: { descricao_vaga: form.getValues("descricao").trim(), ...fonte },
    });
  };

  const gerarCarta = async () => {
    if (!(await form.trigger(["cargo", "empresa", "descricao"]))) return;
    carta.mutate((await montarEntrada()).dados);
  };

  const copiarCarta = async (texto: string) => {
    try {
      await navigator.clipboard.writeText(texto);
      notificar("Carta copiada.", "sucesso");
    } catch {
      notificar("Não foi possível copiar. Selecione o texto e copie manualmente.", "erro");
    }
  };

  const baixarCarta = (texto: string) => {
    const { cargo, empresa } = form.getValues();
    const nome = ["carta-apresentacao", paraSlug(cargo), paraSlug(empresa)]
      .filter(Boolean)
      .join("-");
    baixarArquivo(new Blob([texto], { type: "text/plain;charset=utf-8" }), `${nome}.txt`);
  };

  const semFonte = !fontes.carregando && fontes.opcoes.length === 0;
  const avaliacaoVaga = avaliar.data ?? adaptar.data?.avaliacao_vaga ?? null;

  return (
    <>
      <CabecalhoPagina
        titulo="Ajustar para uma vaga"
        descricao="Analise a vaga, gere um currículo adaptado e prepare a candidatura."
      />

      <div className={estilos.layout}>
        <Panel titulo="Dados da vaga">
          <form noValidate onSubmit={(evento) => evento.preventDefault()}>
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
              <Button
                variante="primary"
                disabled={semFonte}
                carregando={adaptar.isPending}
                onClick={gerarCurriculo}
              >
                {adaptar.isPending ? `Gerando… ${AVISO_DEMORA}` : "Gerar currículo adaptado"}
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
            {adaptar.data?.status_avaliacao_vaga === "indisponivel" && !avaliar.data && (
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
            {adaptar.isError && <Aviso tom="erro">{adaptar.error.message}</Aviso>}
            {adaptar.data ? (
              <CurriculoGerado resultado={adaptar.data} />
            ) : (
              !adaptar.isError && (
                <p className={resultados.texto}>
                  O PDF adaptado aparece aqui depois de “Gerar currículo adaptado”.
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
              <CartaGerada texto={carta.data.carta} aoCopiar={copiarCarta} aoBaixar={baixarCarta} />
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

function CurriculoGerado({ resultado }: { resultado: CurriculoAdaptado }) {
  const idTitulo = useId();
  const baixar = () => baixarArquivo(base64ParaBlob(resultado.pdf_base64), resultado.nome_arquivo);
  const avaliacoes = resultado.avaliacoes_experiencias ?? [];
  return (
    <div aria-live="polite">
      <div className={estilos.arquivo}>
        <span className={estilos.nomeArquivo}>{resultado.nome_arquivo}</span>
        <Button variante="primary" onClick={baixar}>
          Baixar PDF
        </Button>
      </div>
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

interface PropsCarta {
  texto: string;
  aoCopiar: (texto: string) => void;
  aoBaixar: (texto: string) => void;
}

function CartaGerada({ texto, aoCopiar, aoBaixar }: PropsCarta) {
  const id = useId();
  return (
    <div>
      <label htmlFor={id} className="sr-only">
        Texto da carta
      </label>
      <textarea id={id} className={estilos.carta} readOnly value={texto} />
      <div className={estilos.acoes}>
        <Button onClick={() => aoCopiar(texto)}>Copiar carta</Button>
        <Button onClick={() => aoBaixar(texto)}>Baixar carta</Button>
      </div>
    </div>
  );
}
