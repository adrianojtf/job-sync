import {
  DndContext,
  KeyboardSensor,
  MouseSensor,
  TouchSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { useContext, useEffect, useRef, useState, type ReactNode } from "react";
import {
  get,
  useFieldArray,
  useWatch,
  type ArrayPath,
  type FieldArray,
  type FieldValues,
  type Path,
  type UseFormReturn,
} from "react-hook-form";
import { Button } from "../ui/Button";
import { Field } from "../ui/Field";
import { Panel } from "../ui/Panel";
import { ToastContext } from "../ui/toast-context";
import { anunciosDeLista, INSTRUCOES_DE_LISTA } from "./anuncios-de-lista";
import type { CampoItem } from "./campos-curriculo";
import { CartaoDaLista, type ResumoDoItem } from "./CartaoDaLista";
import { LinhaDaLista } from "./LinhaDaLista";
import estilos from "./FormularioCurriculo.module.css";
import type { ChaveDeOrdem } from "./periodo";
import { ordenarPorChave } from "./periodo";
import { useCartoesAbertos } from "./use-cartoes-abertos";
import type { HistoricoDoFormulario } from "./use-historico-do-formulario";

interface Props<T extends FieldValues, N extends ArrayPath<T>> {
  form: UseFormReturn<T>;
  nome: N;
  titulo: string;
  subtitulo?: string;
  rotuloItem: string;
  itemVazio: FieldArray<T, N>;
  campos: CampoItem[];
  acoesItem?: (indice: number) => ReactNode;
  /** Conteúdo extra abaixo dos campos do item, antes das ações (ex.: sugestão de IA). */
  complementoItem?: (indice: number) => ReactNode;
  /**
   * `formulario` (padrão): todos os itens abertos, como sempre. `cartao` (JOB-0046): cada item
   * aparece recolhido, com resumo, e abre para edição; exige `resumoDoItem`. `linha`: uma linha
   * editável por item, sem abrir (`resumoDoItem` só nomeia o item para os leitores de tela).
   */
  modo?: "formulario" | "cartao" | "linha";
  resumoDoItem?: (valores: FieldArray<T, N>) => ResumoDoItem;
  /** Lembra os cartões abertos no navegador: chave do `localStorage` e a chave de cada item pelo conteúdo. */
  armazenamento?: { chave: string; chaveDoItem: (valores: FieldArray<T, N>) => string };
  /** Só no modo cartão: alça de arrasto e botões de mover. */
  reordenavel?: boolean;
  /** Máximo de itens: ao chegar nele, "Adicionar" fica desabilitado e explica. */
  limite?: number;
  /** Habilita "Ordenar por …", do mais recente para o mais antigo. */
  ordenarPor?: { rotulo: string; chave: (valores: FieldArray<T, N>) => ChaveDeOrdem };
  /** Instantâneo para o "Desfazer" das reordenações, remoções e ordenações. */
  historico?: HistoricoDoFormulario;
}

/**
 * Lista editável de itens de um formulário de currículo (experiências, formações, certificações,
 * idiomas) — RF4.1. Usada no cadastro (Meu perfil) e na revisão do currículo adaptado.
 */
export function ListaItensCurriculo<T extends FieldValues, N extends ArrayPath<T>>({
  form,
  nome,
  titulo,
  subtitulo,
  rotuloItem,
  itemVazio,
  campos,
  acoesItem,
  complementoItem,
  modo = "formulario",
  resumoDoItem,
  armazenamento,
  reordenavel = false,
  limite,
  ordenarPor,
  historico,
}: Props<T, N>) {
  const { fields, append, prepend, remove, move } = useFieldArray({
    control: form.control,
    name: nome,
  });
  const toast = useContext(ToastContext);
  const emCartao = modo === "cartao" && resumoDoItem !== undefined;
  const emLinha = modo === "linha";
  const emLista = emCartao || emLinha;
  const valores = useWatch({
    control: form.control,
    name: nome as unknown as Path<T>,
    disabled: !emLista,
  }) as unknown as FieldArray<T, N>[] | undefined;
  const notificar: NonNullable<typeof toast>["notificar"] = (...argumentos) =>
    toast?.notificar(...argumentos);
  const [arrastando, setArrastando] = useState(false);
  const abrirNovo = useRef(false);
  const focarNovo = useRef<string | null>(null);
  const focoApos = useRef<{ id: string; mover?: "-1" | "1" } | null>(null);
  const rotuloMinusculo = rotuloItem.toLowerCase();
  const noLimite = limite !== undefined && fields.length >= limite;
  const idsDosCampos = fields.map((campoLista) => campoLista.id);
  // Entre adicionar um item e o formulário publicar os valores dele, o item vazio completa o que falta.
  const valoresDoItem = (indice: number) => {
    const publicados = Object.entries((valores ?? [])[indice] ?? {}).filter(
      ([, valor]) => valor !== undefined,
    );
    return { ...(itemVazio as object), ...Object.fromEntries(publicados) } as unknown as FieldArray<
      T,
      N
    >;
  };
  const { abertos, alternar, abrir, abrirVarios, definir } = useCartoesAbertos({
    chaveDeArmazenamento: emCartao ? armazenamento?.chave : undefined,
    ids: idsDosCampos,
    chavesDosItens: fields.map((_, indice) =>
      emCartao && armazenamento ? armazenamento.chaveDoItem(valoresDoItem(indice)) : "",
    ),
  });

  const sensores = useSensors(
    useSensor(MouseSensor, { activationConstraint: { distance: 5 } }),
    useSensor(TouchSensor, { activationConstraint: { delay: 200, tolerance: 8 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  // Um cartão recolhido com campo inválido abre sozinho depois de um envio com erro.
  const idsAtuais = useRef(idsDosCampos);
  useEffect(() => {
    idsAtuais.current = idsDosCampos;
  });
  useEffect(() => {
    if (!emCartao) return;
    return form.subscribe({
      formState: { errors: true },
      callback: ({ errors }) => {
        const doItem = get(errors, nome);
        if (Array.isArray(doItem))
          abrirVarios(idsAtuais.current.filter((_, indice) => doItem[indice]));
      },
    });
  }, [form, nome, emCartao, abrirVarios]);

  useEffect(() => {
    if (!abrirNovo.current || fields.length === 0) return;
    abrirNovo.current = false;
    const novo = fields[0]!.id;
    if (emCartao) {
      abrir(novo);
      focarNovo.current = novo;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fields]);

  useEffect(() => {
    const novo = focarNovo.current;
    if (novo === null || !abertos.has(novo)) return;
    focarNovo.current = null;
    document
      .querySelector(`[data-item-id="${CSS.escape(novo)}"]`)
      ?.querySelector<HTMLElement>("input, textarea, select")
      ?.focus();
  }, [abertos]);

  useEffect(() => {
    const alvo = focoApos.current;
    if (alvo === null) return;
    focoApos.current = null;
    const cartao = document.querySelector(`[data-item-id="${CSS.escape(alvo.id)}"]`);
    const seletor = alvo.mover ? `[data-mover="${alvo.mover}"]` : "[data-alca-id]";
    const botao = cartao?.querySelector<HTMLButtonElement>(seletor);
    (botao && !botao.disabled
      ? botao
      : cartao?.querySelector<HTMLButtonElement>("[data-alca-id]")
    )?.focus();
  }, [fields]);

  const resumos = (): ResumoDoItem[] =>
    fields.map((_, indice) => {
      const resumo = resumoDoItem?.(valoresDoItem(indice));
      return { ...resumo, titulo: resumo?.titulo ?? "" };
    });
  const tituloDe = (indice: number) =>
    resumos()[indice]?.titulo.trim() || `${rotuloItem} ${indice + 1}`;
  const comDesfazer = historico
    ? { acao: { rotulo: "Desfazer", aoClicar: historico.desfazer } }
    : undefined;

  const todasAbertas =
    fields.length > 0 && fields.every((campoLista) => abertos.has(campoLista.id));

  const adicionar = () => {
    if (noLimite) return;
    if (emLista) {
      historico?.registrar();
      abrirNovo.current = true;
      prepend(itemVazio, { shouldFocus: emLinha });
    } else {
      append(itemVazio);
    }
  };

  const moverItem = (de: number, para: number, direcao?: "-1" | "1") => {
    if (para < 0 || para >= fields.length || de === para) return;
    const id = fields[de]!.id;
    historico?.registrar();
    move(de, para);
    focoApos.current = { id, mover: direcao };
    notificar("Ordem alterada.", "info", comDesfazer);
  };

  const remover = (indice: number) => {
    if (emLista) {
      historico?.registrar();
      remove(indice);
      notificar("Item removido.", "info", comDesfazer);
    } else {
      remove(indice);
    }
  };

  const ordenar = () => {
    if (!ordenarPor) return;
    const atuais = form.getValues(nome as unknown as Path<T>) as unknown as FieldArray<T, N>[];
    const ordenados = ordenarPorChave(atuais, ordenarPor.chave);
    const posicoes = ordenados.map((item) => atuais.indexOf(item));
    if (posicoes.every((posicao, indice) => posicao === indice)) {
      notificar("Já estava ordenado.");
      return;
    }
    historico?.registrar();
    const ordemAtual = atuais.map((_, indice) => indice);
    posicoes.forEach((origem, destino) => {
      const atual = ordemAtual.indexOf(origem);
      if (atual !== destino) {
        move(atual, destino);
        ordemAtual.splice(destino, 0, ordemAtual.splice(atual, 1)[0]!);
      }
    });
    notificar("Ordenado do mais recente para o mais antigo.", "info", comDesfazer);
  };

  const soltar = ({ active, over }: DragEndEvent) => {
    setArrastando(false);
    if (!over || active.id === over.id) return;
    const de = idsDosCampos.indexOf(String(active.id));
    const para = idsDosCampos.indexOf(String(over.id));
    if (de < 0 || para < 0) return;
    move(de, para);
    focoApos.current = { id: String(active.id) };
    notificar("Ordem alterada.", "info", comDesfazer);
  };

  const renderizarCampo = (campo: CampoItem, indice: number, emUmaLinha: boolean) => {
    const caminho = `${nome}.${indice}.${campo.chave}` as Path<T>;
    const erro = get(form.formState.errors, caminho)?.message as string | undefined;
    const registro = form.register(caminho, {
      validate:
        campo.obrigatorio || campo.validar
          ? (valor) => {
              const texto = String(valor ?? "");
              if (campo.obrigatorio && texto.trim() === "") return campo.obrigatorio;
              return campo.validar?.(texto) ?? true;
            }
          : undefined,
    });
    const comuns = { rotulo: campo.rotulo, erro, rotuloOculto: emUmaLinha, ...registro };
    const ajuda = emUmaLinha ? undefined : campo.ajuda;
    const classe = emUmaLinha
      ? estilos.campoDaLinha
      : campo.larguraTotal
        ? estilos.larguraTotal
        : undefined;
    return (
      <div key={campo.chave} className={classe}>
        {campo.tipoCampo === "select" ? (
          <Field tipoCampo="select" opcoes={campo.opcoes ?? []} ajuda={ajuda} {...comuns} />
        ) : campo.tipoCampo === "textarea" ? (
          <Field tipoCampo="textarea" ajuda={ajuda} {...comuns} />
        ) : (
          <Field ajuda={ajuda} {...comuns} />
        )}
      </div>
    );
  };

  const camposDoItem = (indice: number) => (
    <>
      <div className={estilos.grade}>
        {campos.map((campo) => renderizarCampo(campo, indice, false))}
      </div>
      {complementoItem?.(indice)}
      <div className={estilos.acoesItem}>
        {acoesItem?.(indice)}
        <Button
          aria-label={`Remover ${rotuloMinusculo} ${indice + 1}`}
          onClick={() => remover(indice)}
        >
          Remover
        </Button>
      </div>
    </>
  );

  const acoesDoPainel = emLista ? (
    <div className={estilos.acoesDaLista}>
      {ordenarPor && (
        <Button variante="text" onClick={ordenar}>
          Ordenar por {ordenarPor.rotulo}
        </Button>
      )}
      {emCartao && (
        <Button onClick={() => definir(todasAbertas ? new Set() : new Set(idsDosCampos))}>
          {todasAbertas ? "Recolher todas" : "Expandir todas"}
        </Button>
      )}
      <Button variante="primary" disabled={noLimite} onClick={adicionar}>
        Adicionar {rotuloMinusculo}
      </Button>
    </div>
  ) : (
    <Button variante="text" onClick={adicionar}>
      Adicionar {rotuloMinusculo}
    </Button>
  );

  return (
    <Panel titulo={titulo} subtitulo={subtitulo} acoes={acoesDoPainel}>
      {fields.length === 0 && <p className={estilos.vazio}>Nenhum item adicionado.</p>}
      {noLimite && (
        <p className={estilos.limite} role="note">
          Você chegou ao limite de {limite} itens nesta lista.
        </p>
      )}
      {emLista ? (
        <DndContext
          sensors={sensores}
          collisionDetection={closestCenter}
          onDragStart={() => {
            historico?.registrar();
            setArrastando(true);
          }}
          onDragEnd={soltar}
          onDragCancel={() => setArrastando(false)}
          accessibility={{
            announcements: anunciosDeLista(() =>
              fields.map((campoLista, indice) => ({ id: campoLista.id, titulo: tituloDe(indice) })),
            ),
            screenReaderInstructions: INSTRUCOES_DE_LISTA,
          }}
        >
          <SortableContext items={idsDosCampos} strategy={verticalListSortingStrategy}>
            <div
              className={[estilos.cartoes, arrastando && estilos.cartoesArrastando]
                .filter(Boolean)
                .join(" ")}
              data-arrastando={arrastando || undefined}
            >
              {fields.map((campoLista, indice) =>
                emLinha ? (
                  <LinhaDaLista
                    key={campoLista.id}
                    id={campoLista.id}
                    indice={indice}
                    total={fields.length}
                    rotuloItem={rotuloItem}
                    titulo={resumos()[indice]?.titulo ?? ""}
                    reordenavel={reordenavel}
                    aoMover={(direcao) =>
                      moverItem(indice, indice + direcao, direcao === -1 ? "-1" : "1")
                    }
                    aoRemover={() => remover(indice)}
                  >
                    {campos.map((campo) => renderizarCampo(campo, indice, true))}
                  </LinhaDaLista>
                ) : (
                  <CartaoDaLista
                    key={campoLista.id}
                    id={campoLista.id}
                    indice={indice}
                    total={fields.length}
                    rotuloItem={rotuloItem}
                    resumo={resumos()[indice] ?? { titulo: "" }}
                    aberto={abertos.has(campoLista.id)}
                    reordenavel={reordenavel}
                    aoAlternar={() => alternar(campoLista.id)}
                    aoMover={(direcao) =>
                      moverItem(indice, indice + direcao, direcao === -1 ? "-1" : "1")
                    }
                  >
                    {camposDoItem(indice)}
                  </CartaoDaLista>
                ),
              )}
            </div>
          </SortableContext>
        </DndContext>
      ) : (
        fields.map((campoLista, indice) => (
          <fieldset key={campoLista.id} className={estilos.item}>
            <legend className={estilos.legenda}>
              {rotuloItem} {indice + 1}
            </legend>
            {camposDoItem(indice)}
          </fieldset>
        ))
      )}
    </Panel>
  );
}
