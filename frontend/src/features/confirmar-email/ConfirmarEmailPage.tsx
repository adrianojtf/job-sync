import { useMutation } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { useApiClient } from "../../api/api-client-context";
import { ApiError } from "../../api/api-error";
import { Aviso } from "../../shared/ui/Aviso";
import { Button } from "../../shared/ui/Button";
import { CartaoAutenticacao } from "../entrar/CartaoAutenticacao";
import estilos from "../entrar/EntrarPage.module.css";

/**
 * Confirma o e-mail pelo link recebido. A confirmação é um clique explícito: o link é de uso
 * único, e abrir a página (por scanners de e-mail, prévias ou recarga) não pode consumi-lo.
 */
export function ConfirmarEmailPage() {
  const api = useApiClient();
  const [parametros] = useSearchParams();
  const token = parametros.get("token");
  const confirmacao = useMutation({ mutationFn: (valor: string) => api.confirmarEmail(valor) });

  if (!token) {
    return (
      <CartaoAutenticacao titulo="Confirmar e-mail">
        <Aviso tom="erro">Link incompleto. Abra o link do e-mail de confirmação.</Aviso>
        <div className={estilos.links}>
          <Link to="/cadastrar">Criar conta</Link>
        </div>
      </CartaoAutenticacao>
    );
  }

  if (confirmacao.isSuccess) {
    return (
      <CartaoAutenticacao titulo="E-mail confirmado">
        <Aviso>Tudo certo. Agora você já pode entrar com o seu e-mail e a senha escolhida.</Aviso>
        <div className={estilos.links}>
          <Link to="/entrar">Entrar</Link>
        </div>
      </CartaoAutenticacao>
    );
  }

  const falhaDeLink = confirmacao.error instanceof ApiError && confirmacao.error.status === 400;
  return (
    <CartaoAutenticacao
      titulo="Confirmar e-mail"
      descricao="Confirme que este e-mail é seu para ativar a conta."
    >
      {confirmacao.error && (
        <div className={estilos.avisoTopo}>
          <Aviso tom="erro">
            {falhaDeLink
              ? "Link inválido ou expirado. Faça o cadastro de novo para receber outro link."
              : "Não foi possível confirmar agora. Tente novamente."}
          </Aviso>
        </div>
      )}
      <Button
        variante="primary"
        larguraTotal
        carregando={confirmacao.isPending}
        onClick={() => confirmacao.mutate(token)}
      >
        Confirmar meu e-mail
      </Button>
    </CartaoAutenticacao>
  );
}
