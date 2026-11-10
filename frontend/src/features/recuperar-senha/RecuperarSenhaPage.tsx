import { useMutation } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useApiClient } from "../../api/api-client-context";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { CartaoAutenticacao } from "../entrar/CartaoAutenticacao";
import estilos from "../entrar/EntrarPage.module.css";

/** Pede o link de redefinição. A resposta é a mesma para qualquer e-mail, para não revelar quem tem conta. */
export function RecuperarSenhaPage() {
  const api = useApiClient();
  const [email, setEmail] = useState("");
  const [erroLocal, setErroLocal] = useState<string>();
  const pedido = useMutation({ mutationFn: () => api.solicitarRedefinicaoSenha(email.trim()) });

  const enviar = (evento: FormEvent) => {
    evento.preventDefault();
    if (!email.trim()) {
      setErroLocal("Informe o e-mail.");
      return;
    }
    setErroLocal(undefined);
    pedido.mutate();
  };

  if (pedido.isSuccess) {
    return (
      <CartaoAutenticacao titulo="Verifique seu e-mail">
        <Aviso>
          Se esse e-mail tiver cadastro, enviamos um link para redefinir a senha. O link vale por 1
          hora.
        </Aviso>
        <div className={estilos.links}>
          <Link to="/entrar">Voltar para entrar</Link>
        </div>
      </CartaoAutenticacao>
    );
  }

  return (
    <CartaoAutenticacao
      titulo="Recuperar senha"
      descricao="Informe o e-mail da conta para receber o link de redefinição."
    >
      <form onSubmit={enviar} noValidate className={estilos.formulario}>
        <Field
          rotulo="E-mail"
          name="email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(evento) => setEmail(evento.target.value)}
          erro={
            erroLocal ??
            (pedido.error ? "Não foi possível enviar agora. Tente novamente." : undefined)
          }
        />
        <div className={estilos.acoes}>
          <Button type="submit" variante="primary" larguraTotal carregando={pedido.isPending}>
            {pedido.isPending ? "Enviando…" : "Enviar link"}
          </Button>
        </div>
      </form>
      <div className={estilos.links}>
        <Link to="/entrar">Voltar para entrar</Link>
      </div>
    </CartaoAutenticacao>
  );
}
