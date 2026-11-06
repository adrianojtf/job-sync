import { useState } from "react";
import { useForm } from "react-hook-form";
import type { PerfilEstruturado } from "../../api/tipos";
import { CabecalhoPagina } from "../../app/CabecalhoPagina";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Panel } from "../../shared/ui/Panel";
import { useToast } from "../../shared/ui/use-toast";
import { AvaliarExperienciaModal } from "./AvaliarExperienciaModal";
import {
  CERTIFICACAO_VAZIA,
  EXPERIENCIA_VAZIA,
  FORMACAO_VAZIA,
  formularioParaEntrada,
  IDIOMA_VAZIO,
  NIVEIS_IDIOMA,
  perfilParaFormulario,
  type ExperienciaFormulario,
  type FormularioPerfil,
} from "./formulario-perfil";
import { ImportarPerfilModal } from "./ImportarPerfilModal";
import { ListaItensPerfil } from "./ListaItensPerfil";
import estilos from "./PerfilPage.module.css";
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
  const { errors, isDirty } = form.formState;

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
        <Panel titulo="Dados pessoais">
          <div className={estilos.grade}>
            <Field
              rotulo="Nome completo"
              autoComplete="name"
              erro={errors.nome_completo?.message}
              {...form.register("nome_completo", {
                validate: (v) => v.trim() !== "" || "Informe o nome completo.",
              })}
            />
            <Field
              rotulo="E-mail"
              type="email"
              autoComplete="email"
              erro={errors.email?.message}
              {...form.register("email", {
                validate: (v) => v.trim() !== "" || "Informe o e-mail.",
              })}
            />
            <div className={estilos.larguraTotal}>
              <Field
                rotulo="LinkedIn"
                type="url"
                placeholder="https://linkedin.com/in/…"
                {...form.register("linkedin")}
              />
            </div>
            <div className={estilos.larguraTotal}>
              <Field
                tipoCampo="textarea"
                rotulo="Resumo profissional"
                {...form.register("resumo_profissional")}
              />
            </div>
          </div>
        </Panel>

        <ListaItensPerfil
          form={form}
          nome="experiencias"
          titulo="Experiências profissionais"
          subtitulo="Da mais recente para a mais antiga"
          rotuloItem="Experiência"
          itemVazio={EXPERIENCIA_VAZIA}
          campos={[
            { chave: "empresa", rotulo: "Empresa", obrigatorio: "Informe a empresa." },
            { chave: "cargo", rotulo: "Cargo", obrigatorio: "Informe o cargo." },
            { chave: "periodo", rotulo: "Período", larguraTotal: true },
            { chave: "descricao", rotulo: "Descrição", tipoCampo: "textarea", larguraTotal: true },
          ]}
          acoesItem={(indice) => (
            <Button
              aria-label={`Avaliar experiência ${indice + 1}`}
              onClick={() => setExperienciaAvaliada(form.getValues(`experiencias.${indice}`))}
            >
              Avaliar
            </Button>
          )}
        />

        <ListaItensPerfil
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

        <ListaItensPerfil
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

        <ListaItensPerfil
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
