import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useLocation } from "react-router-dom";
import { CabecalhoPagina } from "../../app/CabecalhoPagina";
import { primeiraLinha } from "../../shared/formatacao";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Panel } from "../../shared/ui/Panel";
import { AnaliseAtsResultado } from "../ajustar-vaga/AnaliseAtsResultado";
import { useFontesCurriculo } from "../ajustar-vaga/fonte-curriculo";
import type { EstadoAnalisarAts } from "../ajustar-vaga/navegacao";
import { SeletorFonteCurriculo } from "../ajustar-vaga/SeletorFonteCurriculo";
import { useAjustarVaga } from "../ajustar-vaga/use-ajustar-vaga";
import { useVagasSalvas } from "../vagas-salvas/use-vagas-salvas";

interface Formulario {
  descricao: string;
  vagaId: string;
  fonte: string;
}

/** T6 — Diagnóstico rápido de aderência ATS, sem gerar PDF (RF7.1). */
export function AnalisarAtsPage() {
  const estado = (useLocation().state ?? {}) as EstadoAnalisarAts;
  const fontes = useFontesCurriculo();
  const vagas = useVagasSalvas();
  const { ats } = useAjustarVaga();
  const [origem, setOrigem] = useState<"colada" | "salva">("colada");
  const form = useForm<Formulario>({
    defaultValues: { descricao: estado.descricao ?? "", vagaId: "", fonte: "" },
  });
  const { errors } = form.formState;
  const listaVagas = vagas.data ?? [];

  const { padrao } = fontes;
  useEffect(() => {
    if (padrao && !form.getValues("fonte")) form.setValue("fonte", padrao);
  }, [padrao, form]);

  const analisar = form.handleSubmit(async (valores) => {
    const descricao =
      origem === "colada"
        ? valores.descricao.trim()
        : (listaVagas.find((vaga) => vaga.id === valores.vagaId)?.texto_descricao ?? "");
    const { curriculoId, ...fonte } = await fontes.resolver(valores.fonte);
    ats.mutate({ curriculoId, dados: { descricao_vaga: descricao, ...fonte } });
  });

  const semFonte = !fontes.carregando && fontes.opcoes.length === 0;

  return (
    <>
      <CabecalhoPagina
        titulo="Analisar ATS"
        descricao="Diagnóstico rápido da aderência do seu currículo a uma vaga, sem gerar PDF."
      />
      <div style={{ display: "grid", gap: 18 }}>
        <Panel titulo="Vaga e currículo">
          <form onSubmit={analisar} noValidate>
            <fieldset
              style={{
                border: 0,
                padding: 0,
                margin: 0,
                display: "flex",
                gap: 18,
                flexWrap: "wrap",
              }}
            >
              <legend className="sr-only">Origem da descrição</legend>
              <label>
                <input
                  type="radio"
                  checked={origem === "colada"}
                  onChange={() => setOrigem("colada")}
                />{" "}
                Colar a descrição
              </label>
              <label>
                <input
                  type="radio"
                  checked={origem === "salva"}
                  disabled={listaVagas.length === 0}
                  onChange={() => setOrigem("salva")}
                />{" "}
                Usar uma vaga salva
              </label>
            </fieldset>

            {origem === "colada" ? (
              <Field
                tipoCampo="textarea"
                rotulo="Descrição da vaga"
                placeholder="Cole aqui a descrição completa da oportunidade…"
                erro={errors.descricao?.message}
                {...form.register("descricao", {
                  validate: (valor) =>
                    origem !== "colada" || valor.trim() !== "" || "Cole a descrição da vaga.",
                })}
              />
            ) : (
              <Field
                tipoCampo="select"
                rotulo="Vaga salva"
                opcoes={[
                  { valor: "", rotulo: "Selecione…" },
                  ...listaVagas.map((vaga) => ({
                    valor: vaga.id,
                    rotulo: primeiraLinha(vaga.texto_descricao),
                  })),
                ]}
                erro={errors.vagaId?.message}
                {...form.register("vagaId", {
                  validate: (valor) =>
                    origem !== "salva" || valor !== "" || "Escolha uma vaga salva.",
                })}
              />
            )}

            <SeletorFonteCurriculo
              opcoes={fontes.opcoes}
              carregando={fontes.carregando}
              {...form.register("fonte")}
            />

            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
              <Button
                type="submit"
                variante="primary"
                disabled={semFonte}
                carregando={ats.isPending}
              >
                {ats.isPending ? "Analisando… pode levar até 1 minuto" : "Analisar ATS"}
              </Button>
            </div>
          </form>
        </Panel>

        {ats.isError && <Aviso tom="erro">{ats.error.message}</Aviso>}
        {ats.data && (
          <Panel titulo="Aderência ATS">
            <AnaliseAtsResultado analise={ats.data} />
          </Panel>
        )}
      </div>
    </>
  );
}
