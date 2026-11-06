import { useState, type FormEvent } from "react";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Modal } from "../../shared/ui/Modal";
import { ScoreDimensions } from "../../shared/ui/ScoreDimensions";
import type { ExperienciaFormulario } from "./formulario-perfil";
import { useAvaliarExperiencia } from "./use-perfil-estruturado";

interface Props {
  experiencia: ExperienciaFormulario | null;
  aoFechar: () => void;
}

const ID_FORMULARIO = "form-avaliar-experiencia";

/** RF4.4 — avalia o texto de uma experiência contra uma vaga-alvo (JOB-0013). Nada é alterado. */
export function AvaliarExperienciaModal({ experiencia, aoFechar }: Props) {
  const [descricaoVaga, setDescricaoVaga] = useState("");
  const [erro, setErro] = useState<string>();
  const avaliacao = useAvaliarExperiencia();

  const fechar = () => {
    setDescricaoVaga("");
    setErro(undefined);
    avaliacao.reset();
    aoFechar();
  };

  const avaliar = (evento: FormEvent) => {
    evento.preventDefault();
    if (!experiencia) return;
    const problema = !experiencia.descricao.trim()
      ? "Preencha a descrição da experiência para avaliá-la."
      : !descricaoVaga.trim()
        ? "Cole a descrição da vaga."
        : undefined;
    setErro(problema);
    if (problema) return;
    avaliacao.mutate({ experiencia: { ...experiencia }, descricao_vaga: descricaoVaga.trim() });
  };

  const resultado = avaliacao.data;

  return (
    <Modal
      aberto={experiencia !== null}
      titulo="Avaliar experiência"
      descricao="Compare a experiência com a descrição de uma vaga. O texto não é alterado nem salvo."
      aoFechar={fechar}
      rodape={
        <>
          <Button onClick={fechar}>Fechar</Button>
          <Button
            type="submit"
            form={ID_FORMULARIO}
            variante="primary"
            carregando={avaliacao.isPending}
          >
            {avaliacao.isPending ? "Avaliando…" : "Avaliar"}
          </Button>
        </>
      }
    >
      {experiencia && (
        <p style={{ margin: "0 0 4px" }}>
          <strong>{experiencia.cargo || "Sem cargo"}</strong> ·{" "}
          {experiencia.empresa || "Sem empresa"}
        </p>
      )}
      <form id={ID_FORMULARIO} onSubmit={avaliar} noValidate>
        <Field
          tipoCampo="textarea"
          rotulo="Descrição da vaga"
          placeholder="Cole aqui a descrição completa da oportunidade…"
          value={descricaoVaga}
          onChange={(evento) => setDescricaoVaga(evento.target.value)}
          erro={erro}
        />
      </form>
      {avaliacao.isError && (
        <p role="alert" style={{ color: "var(--red)", margin: 0 }}>
          {avaliacao.error.message}
        </p>
      )}
      {resultado && (
        <div aria-live="polite">
          <ScoreDimensions
            score={resultado.score}
            legenda="Estimativa de 0 a 100 baseada em categorias fixas"
            dimensoes={[
              { nome: "Clareza da escrita", ...resultado.clareza_escrita },
              { nome: "Qualidade do detalhe", ...resultado.qualidade_detalhe },
              { nome: "Aderência à vaga", ...resultado.aderencia_vaga },
              { nome: "Consistência textual", ...resultado.consistencia_textual },
            ]}
          />
        </div>
      )}
    </Modal>
  );
}
