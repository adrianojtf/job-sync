import { useEffect, useId, useMemo, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import type { ContextoVaga, RascunhoCurriculoAdaptado } from "../../api/tipos";
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
import { ConfirmacaoModal } from "../../shared/ui/ConfirmacaoModal";
import { Field } from "../../shared/ui/Field";
import { Panel } from "../../shared/ui/Panel";
import { AvaliarExperienciaModal } from "../perfil/AvaliarExperienciaModal";
import {
  formularioParaRascunho,
  rascunhoParaFormulario,
  tituloSecaoPerfil,
  type FormularioRevisao,
  type TipoSecao,
} from "./formulario-revisao";

interface Props {
  rascunho: RascunhoCurriculoAdaptado;
  /** Vaga usada na adaptação: orienta as sugestões de IA de cada bloco. */
  contextoVaga: ContextoVaga;
  gerando: boolean;
  erro?: string;
  aoConfirmar: (rascunho: RascunhoCurriculoAdaptado) => void;
  aoVoltar: () => void;
}

/** Bloco de cada seção de texto, com os mesmos títulos da tela de cadastro (Meu perfil). */
const SECOES_TEXTO: Partial<
  Record<TipoSecao, { titulo: string; rotulo: string; ajuda?: string; sugerir?: boolean }>
> = {
  EXPERIENCIAS: {
    titulo: "Experiências profissionais",
    rotulo: "Experiências",
    ajuda: "Separe cada experiência por uma linha em branco.",
    sugerir: true,
  },
  TECNOLOGIAS: {
    titulo: "Tecnologias e ferramentas",
    rotulo: "Tecnologias",
    ajuda: "Use uma linha por categoria. Ex.: Linguagens: Java, Python",
    sugerir: true,
  },
  FORMACAO: { titulo: "Formação acadêmica", rotulo: "Formação" },
  CERTIFICACOES: { titulo: "Certificações", rotulo: "Certificações" },
  IDIOMAS: { titulo: "Idiomas", rotulo: "Idiomas" },
};

/**
 * Revisão do currículo adaptado pela IA antes do PDF (JOB-0033). Todas as seções ficam
 * editáveis ao mesmo tempo; a confirmação é única e envia o estado atual de todas elas.
 */
export function RevisaoCurriculoAdaptado({
  rascunho,
  contextoVaga,
  gerando,
  erro,
  aoConfirmar,
  aoVoltar,
}: Props) {
  const valoresIniciais = useMemo(() => rascunhoParaFormulario(rascunho), [rascunho]);
  const form = useForm<FormularioRevisao>({ defaultValues: valoresIniciais });
  const { isDirty } = form.formState;
  const [confirmandoSaida, setConfirmandoSaida] = useState(false);
  const [experienciaAvaliada, setExperienciaAvaliada] = useState<ExperienciaFormulario | null>(
    null,
  );
  const experienciasEstruturadas = rascunho.experiencias != null;
  const sugestoes = useSugestoes(contextoVaga);

  const idTitulo = useId();
  const titulo = useRef<HTMLHeadingElement>(null);
  useEffect(() => titulo.current?.focus(), []);

  const confirmar = form.handleSubmit((valores) =>
    aoConfirmar(formularioParaRascunho(valores, rascunho)),
  );
  const voltar = () => (isDirty ? setConfirmandoSaida(true) : aoVoltar());

  return (
    <section aria-labelledby={idTitulo}>
      <h2 id={idTitulo} ref={titulo} tabIndex={-1}>
        Revise o currículo adaptado
      </h2>
      <Aviso>Revise o conteúdo sugerido pela IA. O PDF só será gerado quando você confirmar.</Aviso>

      <form onSubmit={confirmar} noValidate className={estilos.secoes}>
        <PainelDadosPessoais
          form={form}
          emailObrigatorio={false}
          sugerirResumo={sugestoes.secao("PERFIL", tituloSecaoPerfil(rascunho))}
        />

        {experienciasEstruturadas && (
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
        )}

        {valoresIniciais.secoes.map((secao, indice) => {
          const bloco = SECOES_TEXTO[secao.tipo];
          if (!bloco) return null;
          return (
            <Panel key={secao.tipo} titulo={bloco.titulo}>
              <Field
                tipoCampo="textarea"
                rotulo={bloco.rotulo}
                ajuda={bloco.ajuda}
                {...form.register(`secoes.${indice}.conteudo`)}
              />
              {bloco.sugerir && (
                <SugestaoCampo
                  form={form}
                  campo={`secoes.${indice}.conteudo`}
                  rotuloBloco={bloco.rotulo.toLowerCase()}
                  sugerir={sugestoes.secao(secao.tipo, secao.titulo)}
                />
              )}
            </Panel>
          );
        })}

        {erro && <Aviso tom="erro">Não foi possível gerar o PDF: {erro}</Aviso>}

        <div className={estilos.rodape}>
          {isDirty && <span className={estilos.pendente}>Alterações não confirmadas</span>}
          <Button onClick={voltar}>Voltar para a vaga</Button>
          <Button type="submit" variante="primary" carregando={gerando}>
            {gerando ? "Gerando PDF…" : "Confirmar e gerar PDF"}
          </Button>
        </div>
      </form>

      <ConfirmacaoModal
        aberto={confirmandoSaida}
        titulo="Descartar a revisão?"
        descricao="As alterações feitas no currículo adaptado serão perdidas."
        rotuloConfirmar="Descartar alterações"
        aoConfirmar={aoVoltar}
        aoCancelar={() => setConfirmandoSaida(false)}
      />
      <AvaliarExperienciaModal
        experiencia={experienciaAvaliada}
        aoFechar={() => setExperienciaAvaliada(null)}
      />
    </section>
  );
}
