import { useState } from "react";
import { useForm } from "react-hook-form";
import type { PerfilEstruturado } from "../../api/tipos";
import { CabecalhoPagina } from "../../app/CabecalhoPagina";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";
import {
  CAMPOS_EXPERIENCIA,
  EXPERIENCIA_VAZIA,
  type ExperienciaFormulario,
} from "../../shared/formulario-curriculo/campos-curriculo";
import estilos from "../../shared/formulario-curriculo/FormularioCurriculo.module.css";
import { ListaItensCurriculo } from "../../shared/formulario-curriculo/ListaItensCurriculo";
import { PainelDadosPessoais } from "../../shared/formulario-curriculo/PainelDadosPessoais";
import { SugestaoCampo } from "../../shared/formulario-curriculo/SugestaoCampo";
import { useSugestoes } from "../../shared/formulario-curriculo/use-sugestoes";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Panel } from "../../shared/ui/Panel";
import { useToast } from "../../shared/ui/use-toast";
import { AvaliarExperienciaModal } from "./AvaliarExperienciaModal";
import {
  CERTIFICACAO_VAZIA,
  FORMACAO_VAZIA,
  formularioParaEntrada,
  IDIOMA_VAZIO,
  NIVEIS_IDIOMA,
  perfilParaFormulario,
  type FormularioPerfil,
} from "./formulario-perfil";
import { ImportarPerfilModal } from "./ImportarPerfilModal";
import { usePerfilEstruturado, useSalvarPerfilEstruturado } from "./use-perfil-estruturado";

const TITULO = "Meu perfil";
const DESCRICAO = "Seu currículo mestre: a base usada para adaptar currículos e analisar vagas.";

/** T3 — Currículo mestre (perfil estruturado, JOB-0009). */
export function PerfilPage() {
  const consulta = usePerfilEstruturado();

  if (consulta.isPending) {
    return (
      <>
        <CabecalhoPagina titulo={TITULO} descricao={DESCRICAO} />
        <p role="status">Carregando perfil…</p>
      </>
    );
  }
  if (consulta.isError) {
    return (
      <>
        <CabecalhoPagina titulo={TITULO} descricao={DESCRICAO} />
        <Aviso
          tom="erro"
          acao={<Button onClick={() => consulta.refetch()}>Tentar novamente</Button>}
        >
          Não foi possível carregar o perfil: {consulta.error.message}
        </Aviso>
      </>
    );
  }
  return <FormularioPerfilEstruturado perfilSalvo={consulta.data} />;
}

function FormularioPerfilEstruturado({ perfilSalvo }: { perfilSalvo: PerfilEstruturado | null }) {
  const perfil = usePerfilAtivo();
  const { notificar } = useToast();
  const form = useForm<FormularioPerfil>({ defaultValues: perfilParaFormulario(perfilSalvo) });
  const salvar = useSalvarPerfilEstruturado(perfilSalvo !== null);
  const [importando, setImportando] = useState(false);
  const [experienciaAvaliada, setExperienciaAvaliada] = useState<ExperienciaFormulario | null>(
    null,
  );
  const { isDirty } = form.formState;
  // Sem vaga-alvo aqui: a IA só melhora a escrita do texto (JOB-0034).
  const sugestoes = useSugestoes();

  const enviar = form.handleSubmit((valores) =>
    salvar.mutate(formularioParaEntrada(valores, perfil), {
      onSuccess: (salvo) => {
        form.reset(perfilParaFormulario(salvo));
        notificar("Perfil salvo.", "sucesso");
      },
      onError: (erro) => notificar(erro.message, "erro"),
    }),
  );

  const aplicarRascunho = (rascunho: PerfilEstruturado) => {
    form.reset(perfilParaFormulario(rascunho), { keepDefaultValues: true });
    notificar("Dados importados. Revise e clique em Salvar perfil.");
  };

  return (
    <>
      <CabecalhoPagina
        titulo={TITULO}
        descricao={DESCRICAO}
        acoes={<Button onClick={() => setImportando(true)}>Importar de PDF</Button>}
      />

      {perfilSalvo === null && (
        <Aviso>
          Você ainda não tem um currículo mestre. Preencha os campos abaixo ou importe um PDF para
          começar.
        </Aviso>
      )}

      <form onSubmit={enviar} noValidate className={estilos.secoes}>
        <PainelDadosPessoais form={form} sugerirResumo={sugestoes.secao("PERFIL", "Perfil")} />

        <ListaItensCurriculo
          form={form}
          nome="experiencias"
          titulo="Experiências profissionais"
          subtitulo="Da mais recente para a mais antiga"
          rotuloItem="Experiência"
          itemVazio={EXPERIENCIA_VAZIA}
          campos={CAMPOS_EXPERIENCIA}
          complementoItem={(indice) => (
            <SugestaoCampo
              form={form}
              campo={`experiencias.${indice}.descricao`}
              rotuloBloco={`experiência ${indice + 1}`}
              sugerir={sugestoes.experiencia(() => form.getValues(`experiencias.${indice}`))}
            />
          )}
          acoesItem={(indice) => (
            <Button
              aria-label={`Avaliar experiência ${indice + 1}`}
              onClick={() => setExperienciaAvaliada(form.getValues(`experiencias.${indice}`))}
            >
              Avaliar
            </Button>
          )}
        />

        <ListaItensCurriculo
          form={form}
          nome="formacoes"
          titulo="Formação acadêmica"
          rotuloItem="Formação"
          itemVazio={FORMACAO_VAZIA}
          campos={[
            { chave: "instituicao", rotulo: "Instituição", obrigatorio: "Informe a instituição." },
            { chave: "curso", rotulo: "Curso", obrigatorio: "Informe o curso." },
            { chave: "periodo", rotulo: "Período" },
          ]}
        />

        <ListaItensCurriculo
          form={form}
          nome="certificacoes"
          titulo="Certificações"
          rotuloItem="Certificação"
          itemVazio={CERTIFICACAO_VAZIA}
          campos={[
            { chave: "nome", rotulo: "Nome", obrigatorio: "Informe o nome da certificação." },
            { chave: "instituicao", rotulo: "Instituição" },
            { chave: "ano", rotulo: "Ano" },
          ]}
        />

        <ListaItensCurriculo
          form={form}
          nome="idiomas"
          titulo="Idiomas"
          rotuloItem="Idioma"
          itemVazio={IDIOMA_VAZIO}
          campos={[
            { chave: "idioma", rotulo: "Idioma", obrigatorio: "Informe o idioma." },
            { chave: "nivel", rotulo: "Nível", tipoCampo: "select", opcoes: NIVEIS_IDIOMA },
          ]}
        />

        <Panel titulo="Tecnologias e ferramentas">
          <Field
            rotulo="Tecnologias"
            ajuda="Separe por vírgula. Ex.: Java, Spring Boot, AWS"
            {...form.register("tecnologias")}
          />
        </Panel>

        <div className={estilos.rodape}>
          {isDirty && <span className={estilos.pendente}>Alterações não salvas</span>}
          <Button type="submit" variante="primary" carregando={salvar.isPending}>
            {salvar.isPending ? "Salvando…" : "Salvar perfil"}
          </Button>
        </div>
      </form>

      <ImportarPerfilModal
        aberto={importando}
        aoFechar={() => setImportando(false)}
        aoImportar={aplicarRascunho}
      />
      <AvaliarExperienciaModal
        experiencia={experienciaAvaliada}
        aoFechar={() => setExperienciaAvaliada(null)}
      />
    </>
  );
}
