import { useEffect, useRef, useState, type KeyboardEvent, type ReactNode } from "react";
import { Button } from "../ui/Button";
import { Field } from "../ui/Field";
import { Panel } from "../ui/Panel";
import { CATEGORIA_VAZIA, type CategoriaFormulario } from "./campos-curriculo";
import { adicionarTags, separarTags, virgulaAbreNovaTag } from "./competencias";
import estiloEditor from "./EditorCompetencias.module.css";
import estilos from "./FormularioCurriculo.module.css";

interface Props {
  valor: CategoriaFormulario[];
  aoMudar: (valor: CategoriaFormulario[]) => void;
  titulo?: string;
  /** Conteúdo extra no fim do painel (ex.: sugestão de IA). */
  complemento?: ReactNode;
}

/**
 * Competências do currículo por categoria e tag (JOB-0041): cada categoria tem um nome editável
 * e tags que se criam com Enter, vírgula ou ao sair do campo, e se removem pelo botão da tag.
 * Componente controlado: quem usa guarda o valor (no formulário da revisão, via Controller).
 */
export function EditorCompetencias({
  valor,
  aoMudar,
  titulo = "Competências",
  complemento,
}: Props) {
  const [anuncio, setAnuncio] = useState("");
  const indiceParaFocar = useRef<number | null>(null);
  const camposDeNome = useRef<(HTMLInputElement | null)[]>([]);

  const quantidade = valor.length;
  useEffect(() => {
    if (indiceParaFocar.current === null) return;
    camposDeNome.current[indiceParaFocar.current]?.focus();
    indiceParaFocar.current = null;
  }, [quantidade]);

  const alterar = (indice: number, categoria: CategoriaFormulario) =>
    aoMudar(valor.map((atual, posicao) => (posicao === indice ? categoria : atual)));

  const criarTags = (indice: number, texto: string) => {
    const categoria = valor[indice];
    if (!categoria) return;
    const novas = adicionarTags(categoria.tags, separarTags(texto));
    const criadas = novas.slice(categoria.tags.length);
    if (criadas.length === 0) return;
    alterar(indice, { ...categoria, tags: novas });
    setAnuncio(
      `${criadas.length === 1 ? `Tag ${criadas[0]} adicionada` : `${criadas.length} tags adicionadas`} em ${nomeDe(categoria, indice)}.`,
    );
  };

  const removerTag = (indice: number, tag: string) => {
    const categoria = valor[indice];
    if (!categoria) return;
    alterar(indice, { ...categoria, tags: categoria.tags.filter((atual) => atual !== tag) });
    setAnuncio(`Tag ${tag} removida de ${nomeDe(categoria, indice)}.`);
  };

  const adicionarCategoria = () => {
    aoMudar([...valor, { ...CATEGORIA_VAZIA, tags: [] }]);
    indiceParaFocar.current = valor.length;
  };

  const excluirCategoria = (indice: number) => {
    const categoria = valor[indice];
    if (!categoria) return;
    setAnuncio(`Categoria ${nomeDe(categoria, indice)} excluída.`);
    aoMudar(valor.filter((_, posicao) => posicao !== indice));
  };

  return (
    <Panel
      titulo={titulo}
      subtitulo="Agrupe as competências por categoria. Digite uma tag e tecle Enter ou vírgula."
      acoes={
        <Button variante="text" onClick={adicionarCategoria}>
          Adicionar categoria
        </Button>
      }
    >
      {valor.length === 0 && <p className={estilos.vazio}>Nenhuma categoria adicionada.</p>}
      {valor.map((categoria, indice) => (
        <fieldset key={indice} className={estilos.item}>
          <legend className={estilos.legenda}>{nomeDe(categoria, indice)}</legend>
          <Field
            ref={(elemento) => {
              camposDeNome.current[indice] = elemento as HTMLInputElement | null;
            }}
            rotulo="Nome da categoria"
            value={categoria.nome}
            onChange={(evento) => alterar(indice, { ...categoria, nome: evento.target.value })}
          />
          {categoria.tags.length > 0 && (
            <ul className={estiloEditor.tags} aria-label={`Tags de ${nomeDe(categoria, indice)}`}>
              {categoria.tags.map((tag) => (
                <li key={tag} className={estiloEditor.tag}>
                  <span>{tag}</span>
                  <button
                    type="button"
                    className={estiloEditor.removerTag}
                    aria-label={`Remover ${tag}`}
                    onClick={() => removerTag(indice, tag)}
                  >
                    <span aria-hidden="true">×</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
          <CampoNovaTag aoCriar={(texto) => criarTags(indice, texto)} />
          <div className={estilos.acoesItem}>
            <Button
              aria-label={`Excluir categoria ${nomeDe(categoria, indice)}`}
              onClick={() => excluirCategoria(indice)}
            >
              Excluir categoria
            </Button>
          </div>
        </fieldset>
      ))}
      {complemento}
      <p role="status" className="sr-only">
        {anuncio}
      </p>
    </Panel>
  );
}

function nomeDe(categoria: CategoriaFormulario, indice: number): string {
  return categoria.nome.trim() || `Categoria ${indice + 1}`;
}

function CampoNovaTag({ aoCriar }: { aoCriar: (texto: string) => void }) {
  const [texto, setTexto] = useState("");

  const confirmar = () => {
    if (texto.trim() !== "") aoCriar(texto);
    setTexto("");
  };

  const aoTeclar = (evento: KeyboardEvent<HTMLInputElement>) => {
    if (evento.key === "Enter" || (evento.key === "," && virgulaAbreNovaTag(texto))) {
      evento.preventDefault();
      confirmar();
    }
  };

  return (
    <Field
      rotulo="Nova tag"
      placeholder="Digite e tecle Enter"
      value={texto}
      onChange={(evento) => setTexto(evento.target.value)}
      onKeyDown={aoTeclar}
      onBlur={confirmar}
    />
  );
}
