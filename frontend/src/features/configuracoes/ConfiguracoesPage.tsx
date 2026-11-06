import { useMutation } from "@tanstack/react-query";
import { useApiClient } from "../../api/api-client-context";
import { CabecalhoPagina } from "../../app/CabecalhoPagina";
import { copiarTexto } from "../../shared/copiar";
import { usePerfilAtivo } from "../../shared/sessao/use-perfil-ativo";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Panel } from "../../shared/ui/Panel";
import { useToast } from "../../shared/ui/use-toast";

/** T10 — Token de captura para a extensão de navegador (JOB-0006, RF11.1). */
export function ConfiguracoesPage() {
  const api = useApiClient();
  const perfil = usePerfilAtivo();
  const { notificar } = useToast();
  const geracao = useMutation({ mutationFn: () => api.criarTokenCaptura(perfil) });
  const token = geracao.data?.token;

  const copiar = async () => {
    if (!token) return;
    if (await copiarTexto(token)) notificar("Token copiado.", "sucesso");
    else notificar("Não foi possível copiar. Selecione o token e copie manualmente.", "erro");
  };

  return (
    <>
      <CabecalhoPagina
        titulo="Configurações"
        descricao="Preferências e integrações do seu perfil."
      />
      <Panel
        titulo="Extensão de navegador"
        subtitulo="Capture vagas da página que você está vendo, sem copiar e colar."
      >
        <ol
          aria-label="Como usar a extensão"
          style={{ margin: "0 0 16px", paddingLeft: 20, display: "grid", gap: 6 }}
        >
          <li>Gere um token abaixo e copie.</li>
          <li>
            No Chrome, abra <code>chrome://extensions</code>, ative o Modo do desenvolvedor e
            carregue a pasta <code>extensao-chrome</code> do projeto.
          </li>
          <li>
            Abra o popup da extensão, cole o token e clique em <strong>Salvar token</strong>.
          </li>
          <li>
            Na página da vaga, clique em <strong>Capturar vaga desta página</strong>. Ela aparece em
            Vagas salvas.
          </li>
        </ol>
        <p style={{ color: "var(--muted)", fontSize: 12, margin: "0 0 16px" }}>
          A extensão envia as vagas para o servidor de captura em <code>localhost:8502</code>, que
          precisa estar rodando.
        </p>

        {geracao.isError && <Aviso tom="erro">{geracao.error.message}</Aviso>}
        {token ? (
          <>
            <Field
              rotulo="Token de captura"
              readOnly
              value={token}
              onFocus={(evento) => evento.target.select()}
            />
            <Aviso tom="alerta">
              Copie agora: o token não é exibido de novo. Tokens gerados antes continuam válidos.
            </Aviso>
            <div style={{ display: "flex", gap: 9, flexWrap: "wrap" }}>
              <Button variante="primary" onClick={copiar}>
                Copiar token
              </Button>
              <Button carregando={geracao.isPending} onClick={() => geracao.mutate()}>
                Gerar outro token
              </Button>
            </div>
          </>
        ) : (
          <Button
            variante="primary"
            carregando={geracao.isPending}
            onClick={() => geracao.mutate()}
          >
            Gerar token
          </Button>
        )}
      </Panel>
    </>
  );
}
