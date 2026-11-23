import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import type { CurriculoAdaptadoPdf, RascunhoCurriculoAdaptado } from "../../api/tipos";
import { CabecalhoPagina } from "../../app/CabecalhoPagina";
import { base64ParaBlob, baixarArquivo } from "../../shared/arquivos/arquivos";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Panel } from "../../shared/ui/Panel";
import { RevisaoCurriculoAdaptado } from "../ajustar-vaga/RevisaoCurriculoAdaptado";
import { useAtualizarCurriculoAdaptado, useCurriculoAdaptado } from "./use-curriculos-adaptados";

interface Salvo {
  pdf: CurriculoAdaptadoPdf;
  rascunho: RascunhoCurriculoAdaptado;
}

/**
 * Edição de um currículo adaptado já salvo (JOB-0041), aberta depois de fechar a tela de ajuste.
 * As sugestões de IA usam a vaga original, guardada junto do currículo.
 */
export function EditarCurriculoAdaptadoPage() {
  const { id = "" } = useParams();
  const curriculo = useCurriculoAdaptado(id);
  const atualizar = useAtualizarCurriculoAdaptado(id);
  const navegar = useNavigate();
  // Último PDF salvo nesta tela; com ele a edição seguinte parte do que foi salvo, não do que foi carregado.
  const [salvo, setSalvo] = useState<Salvo | null>(null);
  const [verResultado, setVerResultado] = useState(false);

  const cabecalho = (
    <CabecalhoPagina
      titulo="Editar currículo adaptado"
      descricao="Corrija o currículo e gere o PDF de novo."
    />
  );

  if (curriculo.isPending) {
    return (
      <>
        {cabecalho}
        <p role="status">Carregando currículo…</p>
      </>
    );
  }

  if (curriculo.isError) {
    return (
      <>
        {cabecalho}
        <Aviso tom="erro">Não foi possível abrir o currículo: {curriculo.error.message}</Aviso>
        <p>
          <Link to="/curriculos">Voltar para Meus currículos</Link>
        </p>
      </>
    );
  }

  const dados = curriculo.data;

  if (verResultado && salvo) {
    return (
      <>
        {cabecalho}
        <Panel titulo="Currículo salvo" subtitulo="O PDF foi gerado de novo com a sua edição.">
          <p>{salvo.pdf.nome_arquivo}</p>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <Button
              variante="primary"
              onClick={() =>
                baixarArquivo(base64ParaBlob(salvo.pdf.pdf_base64), salvo.pdf.nome_arquivo)
              }
            >
              Baixar PDF
            </Button>
            <Button onClick={() => setVerResultado(false)}>Editar de novo</Button>
            <Link to="/curriculos">Voltar para Meus currículos</Link>
          </div>
        </Panel>
      </>
    );
  }

  return (
    <>
      {cabecalho}
      <RevisaoCurriculoAdaptado
        modo="edicao"
        rascunho={salvo?.rascunho ?? dados.rascunho}
        contextoVaga={{
          descricao_vaga: dados.descricao_vaga,
          idioma_alvo: dados.idioma_alvo,
          analise_vaga: dados.analise_vaga,
          cargo_alvo: dados.cargo_alvo,
        }}
        gerando={atualizar.isPending}
        erro={atualizar.error?.message}
        aoConfirmar={(rascunho) =>
          atualizar.mutate(rascunho, {
            onSuccess: (pdf) => {
              setSalvo({ pdf, rascunho });
              setVerResultado(true);
            },
          })
        }
        aoVoltar={() => navegar("/curriculos")}
      />
    </>
  );
}
