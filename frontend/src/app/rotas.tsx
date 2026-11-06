import { Navigate, type RouteObject } from "react-router-dom";
import { EntrarPage } from "../features/entrar/EntrarPage";
import { AppShell } from "./AppShell";
import { EmConstrucao } from "./EmConstrucao";
import { ErroDeRota } from "./ErroDeRota";
import { RotaProtegida, SomenteSemSessao } from "./guardas";
import { PAGINAS } from "./paginas";

export interface HandleRota {
  titulo: string;
}

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
        element: <EmConstrucao titulo={pagina.titulo} tarefa={pagina.tarefa} />,
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
