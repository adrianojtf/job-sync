import { useMutation } from "@tanstack/react-query";
import { useId, useState } from "react";
import { Aviso } from "../ui/Aviso";
import { Button } from "../ui/Button";
import estilos from "./SugestaoIA.module.css";

interface PropsComuns<S> {
  /** Nome do bloco, usado nos rótulos acessíveis (ex.: "resumo", "experiência 2"). */
  rotuloBloco: string;
  /** Texto atual do campo, com as edições ainda não salvas: é o que a IA recebe. */
  textoAtual: string;
  /** Estratégia de busca da sugestão: cada tela injeta a sua (com ou sem contexto de vaga). */
  sugerir: (texto: string) => Promise<S>;
  /** Grava a sugestão no(s) campo(s) do bloco, marcando-o(s) como alterado(s). */
  aplicar: (sugestao: S) => void;
  /** Devolve o foco ao campo de texto do bloco depois de aplicar ou descartar. */
  focarCampo?: () => void;
}

/**
 * Sugestão em texto puro dispensa `descrever`; qualquer outro formato (ex.: conquistas e
 * contexto de uma experiência) precisa dizer como mostrá-lo no painel.
 */
type Props<S> = PropsComuns<S> &
  ([S] extends [string]
    ? { descrever?: (sugestao: S) => string }
    : { descrever: (sugestao: S) => string });

/**
 * Botão "Sugestões de IA" de um bloco do formulário de currículo (JOB-0034). A sugestão é só
 * uma proposta, exibida abaixo do campo: o texto só muda quando o usuário aplica.
 */
export function SugestaoIA<S = string>({
  rotuloBloco,
  textoAtual,
  sugerir,
  aplicar,
  focarCampo,
  descrever = String,
}: Props<S>) {
  const idDica = useId();
  const [sugestao, setSugestao] = useState<S | null>(null);
  const pedido = useMutation({ mutationFn: sugerir });
  const vazio = textoAtual.trim() === "";

  const pedirSugestao = () => {
    setSugestao(null);
    pedido.mutate(textoAtual, { onSuccess: setSugestao });
  };
  const decidir = (aplicando: boolean) => {
    if (aplicando && sugestao !== null) aplicar(sugestao);
    setSugestao(null);
    pedido.reset();
    focarCampo?.();
  };

  return (
    <div className={estilos.bloco}>
      <div className={estilos.acoes}>
        <Button
          variante="text"
          aria-label={`Sugestões de IA para ${rotuloBloco}`}
          aria-describedby={vazio ? idDica : undefined}
          disabled={vazio}
          carregando={pedido.isPending}
          onClick={pedirSugestao}
        >
          {pedido.isPending ? "Gerando sugestão…" : "Sugestões de IA"}
        </Button>
        {vazio && (
          <span id={idDica} className={estilos.soLeitor}>
            Preencha o texto para pedir sugestões.
          </span>
        )}
      </div>
      <div aria-live="polite">
        {pedido.isError && (
          <Aviso tom="erro">Não foi possível gerar a sugestão: {pedido.error.message}</Aviso>
        )}
        {sugestao !== null && (
          <section className={estilos.painel} aria-label={`Sugestão da IA para ${rotuloBloco}`}>
            <h4 className={estilos.titulo}>Sugestão da IA</h4>
            <p className={estilos.texto}>{descrever(sugestao)}</p>
            <div className={estilos.decisao}>
              <Button
                aria-label={`Descartar sugestão de ${rotuloBloco}`}
                onClick={() => decidir(false)}
              >
                Descartar
              </Button>
              <Button
                variante="primary"
                aria-label={`Aplicar sugestão em ${rotuloBloco}`}
                onClick={() => decidir(true)}
              >
                Aplicar
              </Button>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
