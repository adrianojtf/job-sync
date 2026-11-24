import { useForm, useWatch } from "react-hook-form";
import { AvisoAlteracoesNaoSalvas } from "../../shared/formulario-curriculo/AvisoAlteracoesNaoSalvas";
import { Link } from "react-router-dom";
import { CabecalhoPagina } from "../../app/CabecalhoPagina";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { EmptyState } from "../../shared/ui/EmptyState";
import { Field } from "../../shared/ui/Field";
import { Panel } from "../../shared/ui/Panel";
import { useCurriculos } from "../curriculos/use-curriculos";
import { usePerfilEstruturado } from "../perfil/use-perfil-estruturado";
import estilos from "./DescobrirVagasPage.module.css";
import { useDescobrirVagas } from "./use-descobrir-vagas";
import { VagaDescobertaCard, type FonteCandidatura } from "./VagaDescobertaCard";

interface Filtros {
  termo: string;
  curriculoId: string;
  idioma: "pt" | "en";
  dias: "" | "7" | "15" | "30";
}

const IDIOMAS = [
  { valor: "pt", rotulo: "Português" },
  { valor: "en", rotulo: "Inglês" },
];
const PERIODOS = [
  { valor: "", rotulo: "Qualquer período" },
  { valor: "7", rotulo: "7 dias" },
  { valor: "15", rotulo: "15 dias" },
  { valor: "30", rotulo: "30 dias" },
];

/** T8 — Descoberta de vagas em fontes externas com nota de compatibilidade (JOB-0007). */
export function DescobrirVagasPage() {
  const curriculos = useCurriculos();

  return (
    <>
      <CabecalhoPagina
        titulo="Descobrir vagas"
        descricao="Busca em RemoteOK, We Work Remotely, Arbeitnow, Adzuna e Google, ordenada pela compatibilidade com o seu currículo."
      />
      {curriculos.isPending && <p role="status">Carregando currículos…</p>}
      {curriculos.isError && (
        <Aviso tom="erro">
          Não foi possível carregar os currículos: {curriculos.error.message}
        </Aviso>
      )}
      {curriculos.isSuccess && (
        <BuscaDeVagas
          key={curriculos.data[0]?.id ?? "sem-curriculo"}
          opcoesCurriculo={curriculos.data.map((c) => ({ valor: c.id, rotulo: c.nome_referencia }))}
        />
      )}
    </>
  );
}

function BuscaDeVagas({
  opcoesCurriculo,
}: {
  opcoesCurriculo: { valor: string; rotulo: string }[];
}) {
  const perfil = usePerfilAtivo();
  const perfilEstruturado = usePerfilEstruturado();
  const busca = useDescobrirVagas();
  const form = useForm<Filtros>({
    defaultValues: {
      termo: "",
      curriculoId: opcoesCurriculo[0]?.valor ?? "",
      idioma: "pt",
      dias: "",
    },
  });
  const { errors, isDirty } = form.formState;
  const semCurriculo = opcoesCurriculo.length === 0;
  const idioma = useWatch({ control: form.control, name: "idioma" });

  const buscar = (filtros: Filtros) =>
    busca.mutate(
      {
        termo: filtros.termo.trim(),
        curriculoId: filtros.curriculoId,
        diasMaximo: filtros.dias ? Number(filtros.dias) : null,
      },
      { onSuccess: () => form.reset(form.getValues()) },
    );

  const fonteCandidatura = (pdfReferencia: string): FonteCandidatura =>
    perfilEstruturado.data ? { perfil_identificador: perfil } : { pdf_base64: pdfReferencia };

  const resultado = busca.data;

  return (
    <div style={{ display: "grid", gap: 18 }}>
      <AvisoAlteracoesNaoSalvas alterado={isDirty} />
      <Panel titulo="Busca">
        {semCurriculo && (
          <Aviso tom="alerta">
            A nota de compatibilidade compara cada vaga com um currículo em PDF. Para buscar,{" "}
            <Link to="/curriculos">envie um currículo</Link>.
          </Aviso>
        )}
        <form onSubmit={(evento) => void form.handleSubmit(buscar)(evento)} noValidate>
          <div className={estilos.grade}>
            <Field
              rotulo="Termo de busca"
              placeholder="Ex.: engenheiro de software backend"
              erro={errors.termo?.message}
              {...form.register("termo", {
                validate: (v) => v.trim() !== "" || "Informe um termo de busca.",
              })}
            />
            {!semCurriculo && (
              <Field
                tipoCampo="select"
                rotulo="Currículo de referência"
                opcoes={opcoesCurriculo}
                {...form.register("curriculoId")}
              />
            )}
            <Field
              tipoCampo="select"
              rotulo="Idioma da candidatura"
              opcoes={IDIOMAS}
              {...form.register("idioma")}
            />
            <Field
              tipoCampo="select"
              rotulo="Publicadas nos últimos"
              opcoes={PERIODOS}
              {...form.register("dias")}
            />
          </div>
          <div className={estilos.acoes}>
            <p className={estilos.nota}>
              A nota é uma estimativa feita com os requisitos explícitos de cada vaga. “Candidatar”
              usa o seu currículo mestre quando ele existe e não preenche formulários de terceiros.
            </p>
            <Button
              type="submit"
              variante="primary"
              disabled={semCurriculo}
              carregando={busca.isPending}
            >
              {busca.isPending ? "Buscando… pode levar até 1 minuto" : "Buscar vagas"}
            </Button>
          </div>
        </form>
      </Panel>

      {busca.isError && (
        <Aviso tom="erro">Não foi possível buscar vagas: {busca.error.message}</Aviso>
      )}

      {resultado && (
        <Panel
          titulo={`${resultado.vagas.length} ${resultado.vagas.length === 1 ? "vaga encontrada" : "vagas encontradas"}`}
        >
          {resultado.vagas.length === 0 ? (
            <EmptyState
              titulo="Nenhuma vaga encontrada"
              descricao="Tente outras palavras ou um período maior."
            />
          ) : (
            <div className={estilos.lista}>
              {resultado.vagas.map((vaga) => (
                <VagaDescobertaCard
                  key={`${vaga.fonte}-${vaga.url}`}
                  vaga={vaga}
                  idioma={idioma}
                  fonteCurriculo={fonteCandidatura(resultado.pdfReferencia)}
                />
              ))}
            </div>
          )}
        </Panel>
      )}
    </div>
  );
}
