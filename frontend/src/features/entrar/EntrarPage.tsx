import { useMutation, useQuery } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { Link, useLocation, useSearchParams } from "react-router-dom";
import { useApiClient } from "../../api/api-client-context";
import { useSessao } from "../../shared/sessao/use-sessao";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { CartaoAutenticacao } from "./CartaoAutenticacao";
import { IconeGoogle } from "./IconeGoogle";
import estilos from "./EntrarPage.module.css";
import { mensagemDoErroDeLogin, mensagemDoErroDeProvedor } from "./mensagens-autenticacao";

/** Entrada com Google, e-mail e senha (JOB-0013) e, só em desenvolvimento, por identificador. */
export function EntrarPage() {
  const api = useApiClient();
  const { entrar } = useSessao();
  const [parametros] = useSearchParams();
  const destino = (useLocation().state as { de?: string } | null)?.de ?? "/";
  const provedores = useQuery({
    queryKey: ["provedores"],
    queryFn: () => api.listarProvedores(),
    staleTime: 5 * 60_000,
  });
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [identificador, setIdentificador] = useState("");
  const [erroValidacao, setErroValidacao] = useState<string>();

  // Com a sessão ativa, a guarda SomenteSemSessao leva à página pedida.
  const loginComSenha = useMutation({
    mutationFn: () => api.entrarComSenha(email.trim(), senha),
    onSuccess: entrar,
  });
  const loginSimples = useMutation({
    mutationFn: () => api.entrarComIdentificador(identificador.trim()),
    onSuccess: entrar,
  });

  const enviarSenha = (evento: FormEvent) => {
    evento.preventDefault();
    if (!email.trim() || !senha) {
      setErroValidacao("Informe o e-mail e a senha.");
      return;
    }
    setErroValidacao(undefined);
    loginComSenha.mutate();
  };

  const enviarIdentificador = (evento: FormEvent) => {
    evento.preventDefault();
    if (identificador.trim()) loginSimples.mutate();
  };

  const erroDoProvedor = mensagemDoErroDeProvedor(parametros.get("erro"));
  const temGoogle = provedores.data?.provedores.includes("google") ?? false;
  const mensagemDeErro =
    erroValidacao ?? (loginComSenha.error ? mensagemDoErroDeLogin(loginComSenha.error) : undefined);

  return (
    <CartaoAutenticacao
      titulo="Entrar"
      descricao="Organize seus currículos e prepare a próxima candidatura."
    >
      {erroDoProvedor && (
        <div className={estilos.avisoTopo}>
          <Aviso tom="erro">{erroDoProvedor}</Aviso>
        </div>
      )}

      {temGoogle && (
        <>
          <a className={estilos.botaoProvedor} href={api.urlAutorizacao("google", destino)}>
            <IconeGoogle />
            Entrar com Google
          </a>
          <div className={estilos.separador}>ou</div>
        </>
      )}

      <form onSubmit={enviarSenha} noValidate className={estilos.formulario}>
        <Field
          rotulo="E-mail"
          name="email"
          type="email"
          autoComplete="username"
          value={email}
          onChange={(evento) => setEmail(evento.target.value)}
        />
        <Field
          rotulo="Senha"
          name="senha"
          type="password"
          autoComplete="current-password"
          value={senha}
          onChange={(evento) => setSenha(evento.target.value)}
          erro={mensagemDeErro}
        />
        <div className={estilos.acoes}>
          <Button
            type="submit"
            variante="primary"
            larguraTotal
            carregando={loginComSenha.isPending}
          >
            {loginComSenha.isPending ? "Entrando…" : "Entrar"}
          </Button>
        </div>
      </form>

      <div className={estilos.links}>
        <Link to="/cadastrar">Criar conta</Link>
        <Link to="/recuperar-senha">Esqueci minha senha</Link>
      </div>

      {provedores.data?.login_simples && (
        <form onSubmit={enviarIdentificador} noValidate className={estilos.desenvolvimento}>
          <Field
            rotulo="Identificador (somente desenvolvimento)"
            name="identificador"
            autoComplete="off"
            value={identificador}
            onChange={(evento) => setIdentificador(evento.target.value)}
            erro={loginSimples.error?.message}
          />
          <Button type="submit" larguraTotal carregando={loginSimples.isPending}>
            Entrar por identificador
          </Button>
        </form>
      )}
    </CartaoAutenticacao>
  );
}
