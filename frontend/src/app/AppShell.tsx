import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useMatches, useNavigate } from "react-router-dom";
import { AjustarVagaModal } from "../features/ajustar-vaga/AjustarVagaModal";
import { useSessao } from "../shared/sessao/use-sessao";
import { Button } from "../shared/ui/Button";
import estilos from "./AppShell.module.css";
import { GRUPOS_MENU, PAGINAS } from "./paginas";
import type { HandleRota } from "./rotas";

const NOME_PRODUTO = "job-sync";

function useTituloAtual(): string {
  const matches = useMatches();
  const atual = [...matches]
    .reverse()
    .find((match) => (match.handle as HandleRota | undefined)?.titulo);
  return (atual?.handle as HandleRota | undefined)?.titulo ?? NOME_PRODUTO;
}

/** Estrutura das telas autenticadas: menu lateral, barra superior com trilha e conteúdo (RF1.1–RF1.4). */
export function AppShell() {
  const { usuario, sair } = useSessao();
  const nomeExibido = usuario?.nome || usuario?.email || "";
  const navegar = useNavigate();
  const titulo = useTituloAtual();
  const [menuAberto, setMenuAberto] = useState(false);
  const [ajustandoVaga, setAjustandoVaga] = useState(false);
  // A Visão geral já tem este botão no cabeçalho (protótipo); evita dois controles iguais.
  const mostrarAcaoTopo = useLocation().pathname !== "/";

  useEffect(() => {
    document.title = `${titulo} · ${NOME_PRODUTO}`;
  }, [titulo]);

  useEffect(() => {
    if (!menuAberto) return;
    const aoTeclar = (evento: KeyboardEvent) => {
      if (evento.key === "Escape") setMenuAberto(false);
    };
    document.addEventListener("keydown", aoTeclar);
    return () => document.removeEventListener("keydown", aoTeclar);
  }, [menuAberto]);

  const encerrarSessao = async () => {
    await sair();
    navegar("/entrar", { replace: true });
  };

  return (
    <div className={estilos.app}>
      <a className={estilos.pularConteudo} href="#conteudo">
        Pular para o conteúdo
      </a>

      {menuAberto && (
        <button
          type="button"
          className={estilos.fundoMenu}
          aria-hidden="true"
          tabIndex={-1}
          onClick={() => setMenuAberto(false)}
        />
      )}

      <aside
        id="menu-lateral"
        className={`${estilos.sidebar} ${menuAberto ? estilos.sidebarAberta : ""}`}
      >
        <div className={estilos.marca}>
          <span className={estilos.marcaIcone} aria-hidden="true">
            js
          </span>
          {NOME_PRODUTO}
        </div>

        <nav aria-label="Menu principal">
          {GRUPOS_MENU.map((grupo) => (
            <div key={grupo.id} style={{ marginBottom: 24 }}>
              <h2 className={estilos.rotuloGrupo}>{grupo.rotulo}</h2>
              <ul className={estilos.lista}>
                {PAGINAS.filter((pagina) => pagina.grupo === grupo.id).map((pagina) => (
                  <li key={pagina.caminho}>
                    <NavLink
                      to={pagina.caminho}
                      end={pagina.caminho === "/"}
                      className={({ isActive }) =>
                        `${estilos.item} ${isActive ? estilos.itemAtivo : ""}`
                      }
                      onClick={() => setMenuAberto(false)}
                    >
                      <span className={estilos.icone} aria-hidden="true">
                        {pagina.icone}
                      </span>
                      {pagina.titulo}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>

        <div className={estilos.rodapeSidebar}>
          <span className={estilos.avatar} aria-hidden="true">
            {nomeExibido.slice(0, 2).toUpperCase()}
          </span>
          <span className={estilos.perfil} title={nomeExibido}>
            {nomeExibido}
          </span>
          <Button variante="text" onClick={encerrarSessao}>
            Sair
          </Button>
        </div>
      </aside>

      <div className={estilos.principal}>
        <header className={estilos.topbar}>
          <button
            type="button"
            className={estilos.botaoMenu}
            aria-expanded={menuAberto}
            aria-controls="menu-lateral"
            aria-label={menuAberto ? "Fechar menu" : "Abrir menu"}
            onClick={() => setMenuAberto((aberto) => !aberto)}
          >
            ☰
          </button>
          <nav aria-label="Trilha" className={estilos.trilha}>
            <ol>
              <li>{NOME_PRODUTO}</li>
              <li className={estilos.trilhaAtual} aria-current="page">
                {titulo}
              </li>
            </ol>
          </nav>
          {mostrarAcaoTopo && (
            <div className={estilos.acoesTopo}>
              <Button
                variante="primary"
                aria-label="Ajustar para uma vaga"
                onClick={() => setAjustandoVaga(true)}
              >
                <span aria-hidden="true">＋</span>
                <span className={estilos.rotuloLongo} aria-hidden="true">
                  Ajustar para uma vaga
                </span>
                <span className={estilos.rotuloCurto} aria-hidden="true">
                  Vaga
                </span>
              </Button>
            </div>
          )}
        </header>

        <main id="conteudo" className={estilos.conteudo} tabIndex={-1}>
          <Outlet />
        </main>
        <AjustarVagaModal aberto={ajustandoVaga} aoFechar={() => setAjustandoVaga(false)} />
      </div>
    </div>
  );
}
