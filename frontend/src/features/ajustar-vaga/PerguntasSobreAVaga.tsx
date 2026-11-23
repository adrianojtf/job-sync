import { useState } from "react";
import type { Lacuna, PerfilEstruturado } from "../../api/tipos";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Panel } from "../../shared/ui/Panel";
import { useVerificarConquistasParecidas } from "../perfil/use-perfil-estruturado";
import estilos from "./PerguntasSobreAVaga.module.css";
import { usePerguntasDaVaga } from "./use-perguntas-da-vaga";

type Experiencia = NonNullable<PerfilEstruturado["experiencias"]>[number];

interface Props {
  lacunas: Lacuna[];
  experiencias: Experiencia[];
  idiomaAlvo: string;
  /** Todas as perguntas foram tratadas: segue para a geração do currículo. */
  aoConcluir: () => void;
  /** O candidato dispensa as perguntas que faltam. */
  aoPular: () => void;
}

/**
 * Etapa "Perguntas sobre a vaga" (JOB-0043): para cada tema que o perfil não mostra, o candidato
 * responde Sim, Não ou prefere não responder. Em Sim, aponta a experiência, descreve o caso e aprova
 * a conquista que a IA escreve; só a conquista aprovada é salva no banco da experiência.
 */
export function PerguntasSobreAVaga({
  lacunas,
  experiencias,
  idiomaAlvo,
  aoConcluir,
  aoPular,
}: Props) {
  const [indice, setIndice] = useState(0);
  const total = lacunas.length;
  const lacuna = lacunas[indice];

  const avancar = () => (indice + 1 >= total ? aoConcluir() : setIndice(indice + 1));

  if (!lacuna) return null;
  return (
    <Panel
      titulo="Perguntas sobre a vaga"
      subtitulo={`${total} ${total === 1 ? "pergunta" : "perguntas"} sobre a vaga`}
      acoes={
        <Button variante="text" onClick={aoPular}>
          Pular perguntas e gerar
        </Button>
      }
    >
      <Pergunta
        key={indice}
        lacuna={lacuna}
        numero={indice + 1}
        total={total}
        experiencias={experiencias}
        idiomaAlvo={idiomaAlvo}
        aoResponder={avancar}
      />
    </Panel>
  );
}

type Etapa = "escolha" | "caso" | "revisao";

interface PerguntaProps {
  lacuna: Lacuna;
  numero: number;
  total: number;
  experiencias: Experiencia[];
  idiomaAlvo: string;
  aoResponder: () => void;
}

function Pergunta({ lacuna, numero, total, experiencias, idiomaAlvo, aoResponder }: PerguntaProps) {
  const { redigirConquista, aprovarConquista } = usePerguntasDaVaga();
  const verificarParecidas = useVerificarConquistasParecidas();
  const [etapa, setEtapa] = useState<Etapa>("escolha");
  const [experiencia, setExperiencia] = useState("");
  const [caso, setCaso] = useState("");
  const [conquista, setConquista] = useState("");
  const [parecidas, setParecidas] = useState<string[]>([]);

  const indiceExperiencia = Number(experiencia);
  const opcoes = [
    { valor: "", rotulo: "Selecione…" },
    ...experiencias.map((item, posicao) => ({
      valor: String(posicao),
      rotulo: `${item.cargo} · ${item.empresa}`,
    })),
  ];

  const escrever = () =>
    redigirConquista.mutate(
      {
        tema: lacuna.tema,
        pergunta: lacuna.pergunta,
        caso: caso.trim(),
        experiencia_indice: indiceExperiencia,
        idioma_alvo: idiomaAlvo,
      },
      {
        onSuccess: ({ texto }) => {
          setConquista(texto);
          setParecidas([]);
          setEtapa("revisao");
        },
      },
    );

  const salvar = () =>
    aprovarConquista.mutate(
      { experienciaIndice: indiceExperiencia, texto: conquista.trim() },
      { onSuccess: aoResponder },
    );

  const aprovar = () => {
    const existentes = (experiencias[indiceExperiencia]?.conquistas ?? []).map(
      (item) => item.texto,
    );
    verificarParecidas.mutate(
      { texto: conquista.trim(), conquistas: existentes },
      {
        onSuccess: (encontradas) => (encontradas.length > 0 ? setParecidas(encontradas) : salvar()),
      },
    );
  };

  const erro = redigirConquista.error ?? verificarParecidas.error ?? aprovarConquista.error;
  const salvando = verificarParecidas.isPending || aprovarConquista.isPending;

  return (
    <div role="group" aria-label={`Pergunta ${numero} de ${total}`} className={estilos.pergunta}>
      <p className={estilos.progresso}>
        Pergunta {numero} de {total}
      </p>
      <p className={estilos.texto}>{lacuna.pergunta}</p>

      {etapa === "escolha" && (
        <div className={estilos.acoes}>
          <Button variante="primary" onClick={() => setEtapa("caso")}>
            Sim
          </Button>
          <Button onClick={aoResponder}>Não</Button>
          <Button onClick={aoResponder}>Prefiro não responder</Button>
        </div>
      )}

      {etapa === "caso" && (
        <>
          <Field
            tipoCampo="select"
            rotulo="Em qual experiência?"
            opcoes={opcoes}
            value={experiencia}
            onChange={(evento) => setExperiencia(evento.target.value)}
          />
          <Field
            tipoCampo="textarea"
            rotulo="O que você fez?"
            ajuda="Conte o que fez, para quem e o resultado, se houver. Só isso vira a conquista."
            value={caso}
            onChange={(evento) => setCaso(evento.target.value)}
          />
          {redigirConquista.isError && <Aviso tom="erro">{redigirConquista.error.message}</Aviso>}
          <div className={estilos.acoes}>
            <Button onClick={() => setEtapa("escolha")}>Voltar</Button>
            <Button
              variante="primary"
              disabled={experiencia === "" || caso.trim() === ""}
              carregando={redigirConquista.isPending}
              onClick={escrever}
            >
              Escrever conquista
            </Button>
          </div>
        </>
      )}

      {etapa === "revisao" && (
        <>
          <Field
            tipoCampo="textarea"
            rotulo="Conquista"
            ajuda="Revise o texto: só a conquista que você aprovar é salva no seu perfil."
            value={conquista}
            onChange={(evento) => {
              setConquista(evento.target.value);
              setParecidas([]);
            }}
          />
          {parecidas.length > 0 && (
            <>
              <Aviso tom="alerta">
                Esta conquista se parece com outra já cadastrada nesta experiência:
              </Aviso>
              <ul className={estilos.parecidas}>
                {parecidas.map((parecida) => (
                  <li key={parecida}>{parecida}</li>
                ))}
              </ul>
            </>
          )}
          {erro && etapa === "revisao" && <Aviso tom="erro">{erro.message}</Aviso>}
          <div className={estilos.acoes}>
            <Button onClick={() => setEtapa("caso")}>Voltar</Button>
            {parecidas.length > 0 ? (
              <Button variante="primary" carregando={salvando} onClick={salvar}>
                Aprovar mesmo assim
              </Button>
            ) : (
              <Button
                variante="primary"
                disabled={conquista.trim() === ""}
                carregando={salvando}
                onClick={aprovar}
              >
                Aprovar e salvar
              </Button>
            )}
          </div>
        </>
      )}
    </div>
  );
}
