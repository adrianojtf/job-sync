import { useState } from "react";
import { useFieldArray, type UseFormReturn } from "react-hook-form";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { useToast } from "../../shared/ui/use-toast";
import type { FormularioPerfil } from "./formulario-perfil";
import estilos from "./ConquistasDaExperiencia.module.css";
import { useVerificarConquistasParecidas } from "./use-perfil-estruturado";

interface Props {
  form: UseFormReturn<FormularioPerfil>;
  indice: number;
}

interface ConquistaPendente {
  texto: string;
  parecidas: string[];
}

/**
 * Banco de conquistas de uma experiência (JOB-0042): cadastro, edição e exclusão diretos, com aviso
 * quando a conquista nova se parece com outra já cadastrada. O usuário decide se salva mesmo assim.
 */
export function ConquistasDaExperiencia({ form, indice }: Props) {
  const nomeLista = `experiencias.${indice}.conquistas` as const;
  const { fields, append, remove } = useFieldArray({ control: form.control, name: nomeLista });
  const verificar = useVerificarConquistasParecidas();
  const { notificar } = useToast();
  const [novaConquista, setNovaConquista] = useState("");
  const [pendente, setPendente] = useState<ConquistaPendente | null>(null);
  const numeroExperiencia = indice + 1;

  const adicionar = (texto: string) => {
    append({ texto, origem: "MANUAL" });
    setNovaConquista("");
    setPendente(null);
  };

  const solicitarAdicao = () => {
    const texto = novaConquista.trim();
    if (texto === "") return;
    const existentes = (form.getValues(nomeLista) ?? []).map((conquista) => conquista.texto);
    verificar.mutate(
      { texto, conquistas: existentes },
      {
        onSuccess: (parecidas) =>
          parecidas.length > 0 ? setPendente({ texto, parecidas }) : adicionar(texto),
        onError: (erro) => notificar(erro.message, "erro"),
      },
    );
  };

  return (
    <div
      role="group"
      aria-label={`Conquistas da experiência ${numeroExperiencia}`}
      className={estilos.conquistas}
    >
      <h4 className={estilos.titulo}>Conquistas</h4>
      {fields.length === 0 && <p className={estilos.vazio}>Nenhuma conquista cadastrada.</p>}
      {fields.map((campo, posicao) => (
        <div key={campo.id} className={estilos.item}>
          <Field
            tipoCampo="textarea"
            rotulo={`Conquista ${posicao + 1}`}
            {...form.register(`${nomeLista}.${posicao}.texto` as const)}
          />
          <Button
            aria-label={`Remover conquista ${posicao + 1} da experiência ${numeroExperiencia}`}
            onClick={() => remove(posicao)}
          >
            Remover
          </Button>
        </div>
      ))}

      <Field
        tipoCampo="textarea"
        rotulo="Nova conquista"
        ajuda="Uma entrega sua, com o resultado quando houver. Ex.: Reduzi o tempo de deploy de 40 para 10 minutos."
        value={novaConquista}
        onChange={(evento) => setNovaConquista(evento.target.value)}
      />
      <div className={estilos.acoes}>
        <Button
          onClick={solicitarAdicao}
          disabled={novaConquista.trim() === ""}
          carregando={verificar.isPending}
        >
          Adicionar conquista
        </Button>
      </div>

      {pendente && (
        <Aviso
          tom="alerta"
          acao={
            <div className={estilos.acoes}>
              <Button onClick={() => adicionar(pendente.texto)}>Salvar mesmo assim</Button>
              <Button onClick={() => setPendente(null)}>Cancelar</Button>
            </div>
          }
        >
          Esta conquista se parece com outra já cadastrada nesta experiência:
        </Aviso>
      )}
      {pendente && (
        <ul className={estilos.parecidas}>
          {pendente.parecidas.map((parecida) => (
            <li key={parecida}>{parecida}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
