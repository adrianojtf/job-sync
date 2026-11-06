import type { ReactElement } from "react";
import { Navigate, type RouteObject } from "react-router-dom";
import { AjustarVagaPage } from "../features/ajustar-vaga/AjustarVagaPage";
import { AnalisarAtsPage } from "../features/analisar-ats/AnalisarAtsPage";
import { CandidaturasPage } from "../features/candidaturas/CandidaturasPage";
import { ConfiguracoesPage } from "../features/configuracoes/ConfiguracoesPage";
import { CurriculosPage } from "../features/curriculos/CurriculosPage";
import { DescobrirVagasPage } from "../features/descobrir-vagas/DescobrirVagasPage";
import { EntrarPage } from "../features/entrar/EntrarPage";
import { PerfilPage } from "../features/perfil/PerfilPage";
import { VagasSalvasPage } from "../features/vagas-salvas/VagasSalvasPage";
import { AppShell } from "./AppShell";
import { EmConstrucao } from "./EmConstrucao";
import { ErroDeRota } from "./ErroDeRota";
import { RotaProtegida, SomenteSemSessao } from "./guardas";
import { PAGINAS } from "./paginas";

export interface HandleRota {
  titulo: string;
}

/** Telas já entregues; as demais mostram EmConstrucao até a tarefa correspondente. */
const TELAS: Record<string, ReactElement> = {
  "/perfil": <PerfilPage />,
  "/curriculos": <CurriculosPage />,
  "/ajustar-vaga": <AjustarVagaPage />,
  "/analisar-ats": <AnalisarAtsPage />,
  "/vagas-salvas": <VagasSalvasPage />,
  "/candidaturas": <CandidaturasPage />,
  "/descobrir-vagas": <DescobrirVagasPage />,
  "/configuracoes": <ConfiguracoesPage />,
};

export const rotas: RouteObject[] = [
  {
    path: "/entrar",
    errorElement: <ErroDeRota />,
    element: (
      <SomenteSemSessao>
        <EntrarPage />
      </SomenteSemSessao>
    ),
  },
  {
    path: "/",
    errorElement: <ErroDeRota />,
    element: (
      <RotaProtegida>
        <AppShell />
      </RotaProtegida>
    ),
    children: [
      ...PAGINAS.map<RouteObject>((pagina) => ({
        ...(pagina.caminho === "/" ? { index: true } : { path: pagina.caminho.slice(1) }),
        handle: { titulo: pagina.titulo } satisfies HandleRota,
        element: TELAS[pagina.caminho] ?? (
          <EmConstrucao titulo={pagina.titulo} tarefa={pagina.tarefa} />
        ),
      })),
      { path: "*", element: <Navigate to="/" replace /> },
    ],
  },
];

export const OPCOES_ROUTER = {
  future: {
    v7_relativeSplatPath: true,
    v7_fetcherPersist: true,
    v7_normalizeFormMethod: true,
    v7_partialHydration: true,
    v7_skipActionErrorRevalidation: true,
  },
} as const;
