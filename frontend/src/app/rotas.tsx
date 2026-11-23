import type { ReactElement } from "react";
import { Navigate, type RouteObject } from "react-router-dom";
import { AjustarVagaPage } from "../features/ajustar-vaga/AjustarVagaPage";
import { AnalisarAtsPage } from "../features/analisar-ats/AnalisarAtsPage";
import { CandidaturasPage } from "../features/candidaturas/CandidaturasPage";
import { CadastrarPage } from "../features/cadastrar/CadastrarPage";
import { ConfiguracoesPage } from "../features/configuracoes/ConfiguracoesPage";
import { ConfirmarEmailPage } from "../features/confirmar-email/ConfirmarEmailPage";
import { CurriculosPage } from "../features/curriculos/CurriculosPage";
import { EditarCurriculoAdaptadoPage } from "../features/curriculos-adaptados/EditarCurriculoAdaptadoPage";
import { DescobrirVagasPage } from "../features/descobrir-vagas/DescobrirVagasPage";
import { EntrarPage } from "../features/entrar/EntrarPage";
import { PerfilPage } from "../features/perfil/PerfilPage";
import { RecuperarSenhaPage } from "../features/recuperar-senha/RecuperarSenhaPage";
import { RedefinirSenhaPage } from "../features/redefinir-senha/RedefinirSenhaPage";
import { VagasSalvasPage } from "../features/vagas-salvas/VagasSalvasPage";
import { VisaoGeralPage } from "../features/visao-geral/VisaoGeralPage";
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
  "/": <VisaoGeralPage />,
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
    path: "/cadastrar",
    errorElement: <ErroDeRota />,
    element: (
      <SomenteSemSessao>
        <CadastrarPage />
      </SomenteSemSessao>
    ),
  },
  {
    path: "/recuperar-senha",
    errorElement: <ErroDeRota />,
    element: (
      <SomenteSemSessao>
        <RecuperarSenhaPage />
      </SomenteSemSessao>
    ),
  },
  { path: "/confirmar-email", errorElement: <ErroDeRota />, element: <ConfirmarEmailPage /> },
  { path: "/redefinir-senha", errorElement: <ErroDeRota />, element: <RedefinirSenhaPage /> },
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
      {
        path: "curriculos-adaptados/:id",
        handle: { titulo: "Editar currículo adaptado" } satisfies HandleRota,
        element: <EditarCurriculoAdaptadoPage />,
      },
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
