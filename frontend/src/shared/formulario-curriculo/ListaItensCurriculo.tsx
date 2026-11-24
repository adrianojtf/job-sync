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
import estilos from "./FormularioCurriculo.module.css";
import type { ChaveDeOrdem } from "./periodo";
import { ordenarPorChave } from "./periodo";
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
   * aparece recolhido, com resumo, e abre para edição; exige `resumoDoItem`.
   */
  modo?: "formulario" | "cartao";
  resumoDoItem?: (valores: FieldArray<T, N>) => ResumoDoItem;
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
  const valores = useWatch({
    control: form.control,
    name: nome as unknown as Path<T>,
    disabled: !emCartao,
  }) as unknown as FieldArray<T, N>[] | undefined;
  const notificar: NonNullable<typeof toast>["notificar"] = (...argumentos) =>
    toast?.notificar(...argumentos);
  const [abertos, setAbertos] = useState<Set<string>>(new Set());
  const [arrastando, setArrastando] = useState(false);
  const abrirNovo = useRef(false);
  const focoApos = useRef<{ id: string; mover?: "-1" | "1" } | null>(null);
  const rotuloMinusculo = rotuloItem.toLowerCase();
  const noLimite = limite !== undefined && fields.length >= limite;
  const idsDosCampos = fields.map((campoLista) => campoLista.id);

  const sensores = useSensors(
    useSensor(MouseSensor, { activationConstraint: { distance: 5 } }),
    useSensor(TouchSensor, { activationConstraint: { delay: 200, tolerance: 8 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  useEffect(() => {
    if (!abrirNovo.current || fields.length === 0) return;
    abrirNovo.current = false;
    const novo = fields[0]!.id;
    setAbertos((atuais) => new Set(atuais).add(novo));
  }, [fields]);

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
    fields.map(
      (_, indice) =>
        resumoDoItem?.(((valores ?? [])[indice] ?? {}) as FieldArray<T, N>) ?? { titulo: "" },
    );
  const tituloDe = (indice: number) =>
    resumos()[indice]?.titulo.trim() || `${rotuloItem} ${indice + 1}`;
  const comDesfazer = historico
    ? { acao: { rotulo: "Desfazer", aoClicar: historico.desfazer } }
    : undefined;

  const alternar = (id: string) =>
    setAbertos((atuais) => {
      const proximos = new Set(atuais);
      if (!proximos.delete(id)) proximos.add(id);
      return proximos;
    });
  const todasAbertas =
    fields.length > 0 && fields.every((campoLista) => abertos.has(campoLista.id));

  const adicionar = () => {
    if (noLimite) return;
    if (emCartao) {
      historico?.registrar();
      abrirNovo.current = true;
      prepend(itemVazio);
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
    if (emCartao) {
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

  const camposDoItem = (indice: number) => (
    <>
      <div className={estilos.grade}>
        {campos.map((campo) => {
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
          return (
            <div
              key={campo.chave}
              className={campo.larguraTotal ? estilos.larguraTotal : undefined}
            >
              {campo.tipoCampo === "select" ? (
                <Field
                  tipoCampo="select"
                  rotulo={campo.rotulo}
                  opcoes={campo.opcoes ?? []}
                  ajuda={campo.ajuda}
                  erro={erro}
                  {...registro}
                />
              ) : campo.tipoCampo === "textarea" ? (
                <Field
                  tipoCampo="textarea"
                  rotulo={campo.rotulo}
                  ajuda={campo.ajuda}
                  erro={erro}
                  {...registro}
                />
              ) : (
                <Field rotulo={campo.rotulo} ajuda={campo.ajuda} erro={erro} {...registro} />
              )}
            </div>
          );
        })}
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

  const acoesDoPainel = emCartao ? (
    <div className={estilos.acoesDaLista}>
      {ordenarPor && (
        <Button variante="text" onClick={ordenar}>
          Ordenar por {ordenarPor.rotulo}
        </Button>
      )}
      <Button
        onClick={() =>
          setAbertos(todasAbertas ? new Set() : new Set(fields.map((campoLista) => campoLista.id)))
        }
      >
        {todasAbertas ? "Recolher todas" : "Expandir todas"}
      </Button>
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
      {emCartao ? (
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
              {fields.map((campoLista, indice) => (
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
              ))}
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
