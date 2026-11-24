import estilos from "./ChipsDaExperiencia.module.css";
import { ehLegada, type ExperienciaPerfilFormulario } from "./formulario-perfil";
import { textoParaLinhas } from "../../shared/formulario-curriculo/linhas";

function Contagem({
  n,
  um,
  varios,
  vazio,
}: {
  n: number;
  um: string;
  varios: string;
  vazio: string;
}) {
  return n > 0 ? (
    <span className={`${estilos.chip} ${estilos.ok}`}>
      {n} {n === 1 ? um : varios}
    </span>
  ) : (
    <span className={`${estilos.chip} ${estilos.vazio}`}>{vazio}</span>
  );
}

/** Chips do cartão recolhido da experiência: contagem dos quatro blocos, ou o selo do formato antigo. */
export function ChipsDaExperiencia({ experiencia }: { experiencia: ExperienciaPerfilFormulario }) {
  if (ehLegada(experiencia)) {
    return (
      <>
        <span className={`${estilos.chip} ${estilos.alerta}`}>Formato antigo</span>
        <span className={estilos.chip}>só descrição</span>
      </>
    );
  }
  const responsabilidades = textoParaLinhas(experiencia.responsabilidades).length;
  const realizacoes = experiencia.conquistas.filter((c) => c.texto.trim() !== "").length;
  return (
    <>
      {experiencia.contexto.trim() !== "" ? (
        <span className={`${estilos.chip} ${estilos.ok}`}>contexto</span>
      ) : (
        <span className={`${estilos.chip} ${estilos.vazio}`}>sem contexto</span>
      )}
      <Contagem
        n={responsabilidades}
        um="responsabilidade"
        varios="responsabilidades"
        vazio="sem responsabilidades"
      />
      <Contagem n={realizacoes} um="realização" varios="realizações" vazio="sem realizações" />
      <Contagem n={experiencia.skills.length} um="skill" varios="skills" vazio="sem skills" />
    </>
  );
}
