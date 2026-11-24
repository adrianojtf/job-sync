import { useState, type KeyboardEvent } from "react";
import { Field } from "../ui/Field";
import { adicionarTags, separarTags, virgulaAbreNovaTag } from "./competencias";
import estilos from "./EditorCompetencias.module.css";

interface Props {
  tags: string[];
  aoMudar: (tags: string[]) => void;
  /** Nome do grupo de tags, usado nos rótulos acessíveis e nos anúncios (ex.: "Linguagens"). */
  nome: string;
  /** Recebe o texto de cada criação ou remoção, para o leitor de tela. */
  aoAnunciar?: (mensagem: string) => void;
  rotuloNovaTag?: string;
  ajuda?: string;
}

/**
 * Tags editáveis: criam-se com Enter, vírgula ou ao sair do campo, e removem-se pelo botão da tag.
 * Componente controlado, usado nas competências por categoria (JOB-0041) e nas skills de cada
 * experiência (JOB-0045).
 */
export function EditorTags({
  tags,
  aoMudar,
  nome,
  aoAnunciar,
  rotuloNovaTag = "Nova tag",
  ajuda,
}: Props) {
  const criar = (texto: string) => {
    const novas = adicionarTags(tags, separarTags(texto));
    const criadas = novas.slice(tags.length);
    if (criadas.length === 0) return;
    aoMudar(novas);
    aoAnunciar?.(
      `${criadas.length === 1 ? `Tag ${criadas[0]} adicionada` : `${criadas.length} tags adicionadas`} em ${nome}.`,
    );
  };

  const remover = (tag: string) => {
    aoMudar(tags.filter((atual) => atual !== tag));
    aoAnunciar?.(`Tag ${tag} removida de ${nome}.`);
  };

  return (
    <>
      {tags.length > 0 && (
        <ul className={estilos.tags} aria-label={`Tags de ${nome}`}>
          {tags.map((tag) => (
            <li key={tag} className={estilos.tag}>
              <span>{tag}</span>
              <button
                type="button"
                className={estilos.removerTag}
                aria-label={`Remover ${tag}`}
                onClick={() => remover(tag)}
              >
                <span aria-hidden="true">×</span>
              </button>
            </li>
          ))}
        </ul>
      )}
      <CampoNovaTag rotulo={rotuloNovaTag} ajuda={ajuda} aoCriar={criar} />
    </>
  );
}

function CampoNovaTag({
  rotulo,
  ajuda,
  aoCriar,
}: {
  rotulo: string;
  ajuda?: string;
  aoCriar: (texto: string) => void;
}) {
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
      rotulo={rotulo}
      ajuda={ajuda}
      placeholder="Digite e tecle Enter"
      value={texto}
      onChange={(evento) => setTexto(evento.target.value)}
      onKeyDown={aoTeclar}
      onBlur={confirmar}
    />
  );
}
