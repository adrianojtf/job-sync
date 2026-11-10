import { useMutation } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useApiClient } from "../../api/api-client-context";
import { ApiError } from "../../api/api-error";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { CartaoAutenticacao } from "../entrar/CartaoAutenticacao";
import estilos from "../entrar/EntrarPage.module.css";

export const AJUDA_SENHA = "De 10 a 128 caracteres. Evite senhas comuns.";

/** Cadastro com e-mail e senha: a conta só é ativada depois de confirmar o e-mail. */
export function CadastrarPage() {
  const api = useApiClient();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmacao, setConfirmacao] = useState("");
  const [erroLocal, setErroLocal] = useState<string>();
  const cadastro = useMutation({ mutationFn: () => api.cadastrar(email.trim(), senha) });

  const enviar = (evento: FormEvent) => {
    evento.preventDefault();
    if (!email.trim() || !senha) {
      setErroLocal("Informe o e-mail e a senha.");
      return;
    }
    if (senha !== confirmacao) {
      setErroLocal("As senhas não conferem.");
      return;
    }
    setErroLocal(undefined);
    cadastro.mutate();
  };

  if (cadastro.isSuccess) {
    return (
      <CartaoAutenticacao titulo="Verifique seu e-mail">
        <Aviso>
          Enviamos um link de confirmação para {email.trim()}. A conta só é ativada depois que você
          abrir o link.
        </Aviso>
        <div className={estilos.links}>
          <Link to="/entrar">Voltar para entrar</Link>
        </div>
      </CartaoAutenticacao>
    );
  }

  const erroServidor =
    cadastro.error instanceof ApiError && cadastro.error.status !== 0
      ? cadastro.error.message
      : cadastro.error
        ? "Não foi possível criar a conta agora. Tente novamente."
        : undefined;

  return (
    <CartaoAutenticacao titulo="Criar conta" descricao="Use seu e-mail e uma senha só sua.">
      <form onSubmit={enviar} noValidate className={estilos.formulario}>
        <Field
          rotulo="E-mail"
          name="email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(evento) => setEmail(evento.target.value)}
        />
        <Field
          rotulo="Senha"
          name="senha"
          type="password"
          autoComplete="new-password"
          ajuda={AJUDA_SENHA}
          value={senha}
          onChange={(evento) => setSenha(evento.target.value)}
        />
        <Field
          rotulo="Confirmar senha"
          name="confirmacao"
          type="password"
          autoComplete="new-password"
          value={confirmacao}
          onChange={(evento) => setConfirmacao(evento.target.value)}
          erro={erroLocal ?? erroServidor}
        />
        <div className={estilos.acoes}>
          <Button type="submit" variante="primary" larguraTotal carregando={cadastro.isPending}>
            {cadastro.isPending ? "Criando…" : "Criar conta"}
          </Button>
        </div>
      </form>
      <div className={estilos.links}>
        <Link to="/entrar">Já tenho conta</Link>
      </div>
    </CartaoAutenticacao>
  );
}
