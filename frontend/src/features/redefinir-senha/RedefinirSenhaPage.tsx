import { useMutation } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useApiClient } from "../../api/api-client-context";
import { ApiError } from "../../api/api-error";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { AJUDA_SENHA } from "../cadastrar/CadastrarPage";
import { CartaoAutenticacao } from "../entrar/CartaoAutenticacao";
import estilos from "../entrar/EntrarPage.module.css";

/** Define a nova senha pelo link recebido por e-mail; todas as sessões abertas são encerradas. */
export function RedefinirSenhaPage() {
  const api = useApiClient();
  const [parametros] = useSearchParams();
  const token = parametros.get("token");
  const [senha, setSenha] = useState("");
  const [confirmacao, setConfirmacao] = useState("");
  const [erroLocal, setErroLocal] = useState<string>();
  const redefinicao = useMutation({
    mutationFn: (valor: string) => api.redefinirSenha(valor, senha),
  });

  if (!token) {
    return (
      <CartaoAutenticacao titulo="Redefinir senha">
        <Aviso tom="erro">Link incompleto. Abra o link do e-mail de redefinição.</Aviso>
        <div className={estilos.links}>
          <Link to="/recuperar-senha">Pedir novo link</Link>
        </div>
      </CartaoAutenticacao>
    );
  }

  if (redefinicao.isSuccess) {
    return (
      <CartaoAutenticacao titulo="Senha redefinida">
        <Aviso>
          Senha alterada. Por segurança, você precisa entrar de novo em todos os aparelhos.
        </Aviso>
        <div className={estilos.links}>
          <Link to="/entrar">Entrar</Link>
        </div>
      </CartaoAutenticacao>
    );
  }

  const enviar = (evento: FormEvent) => {
    evento.preventDefault();
    if (!senha) {
      setErroLocal("Informe a nova senha.");
      return;
    }
    if (senha !== confirmacao) {
      setErroLocal("As senhas não conferem.");
      return;
    }
    setErroLocal(undefined);
    redefinicao.mutate(token);
  };

  const erro = redefinicao.error;
  const linkInvalido = erro instanceof ApiError && erro.status === 400;
  const erroDeSenha = erro instanceof ApiError && erro.status === 422 ? erro.message : undefined;

  return (
    <CartaoAutenticacao
      titulo="Redefinir senha"
      descricao="Escolha uma nova senha para a sua conta."
    >
      {linkInvalido && (
        <div className={estilos.avisoTopo}>
          <Aviso tom="erro">
            Link inválido ou expirado. <Link to="/recuperar-senha">Peça um novo link</Link>.
          </Aviso>
        </div>
      )}
      <form onSubmit={enviar} noValidate className={estilos.formulario}>
        <Field
          rotulo="Nova senha"
          name="senha"
          type="password"
          autoComplete="new-password"
          ajuda={AJUDA_SENHA}
          value={senha}
          onChange={(evento) => setSenha(evento.target.value)}
          erro={erroDeSenha}
        />
        <Field
          rotulo="Confirmar nova senha"
          name="confirmacao"
          type="password"
          autoComplete="new-password"
          value={confirmacao}
          onChange={(evento) => setConfirmacao(evento.target.value)}
          erro={
            erroLocal ??
            (erro && !linkInvalido && !erroDeSenha
              ? "Não foi possível redefinir agora. Tente novamente."
              : undefined)
          }
        />
        <div className={estilos.acoes}>
          <Button type="submit" variante="primary" larguraTotal carregando={redefinicao.isPending}>
            {redefinicao.isPending ? "Salvando…" : "Salvar nova senha"}
          </Button>
        </div>
      </form>
    </CartaoAutenticacao>
  );
}
