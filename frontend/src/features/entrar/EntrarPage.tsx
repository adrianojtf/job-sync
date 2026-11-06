import { useMutation } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { useApiClient } from "../../api/api-client-context";
import { useSessao } from "../../shared/sessao/use-sessao";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import estilos from "./EntrarPage.module.css";

/** T1 — Login por identificador (JOB-0004): cria o perfil se ele ainda não existir (RF2.1). */
export function EntrarPage() {
  const api = useApiClient();
  const { entrar } = useSessao();
  const [identificador, setIdentificador] = useState("");
  const [erroValidacao, setErroValidacao] = useState<string>();

  const login = useMutation({
    mutationFn: (id: string) => api.obterOuCriarPerfil(id),
    // Com a sessão ativa, a guarda SomenteSemSessao leva à página pedida.
    onSuccess: (perfil) => entrar(perfil.identificador),
  });

  const enviar = (evento: FormEvent) => {
    evento.preventDefault();
    const valor = identificador.trim();
    if (!valor) {
      setErroValidacao("Informe seu identificador.");
      return;
    }
    setErroValidacao(undefined);
    login.mutate(valor);
  };

  return (
    <main className={estilos.pagina}>
      <div className={estilos.cartao}>
        <div className={estilos.marca}>
          <span className={estilos.marcaIcone} aria-hidden="true">
            js
          </span>
          job-sync
        </div>
        <h1 className={estilos.titulo}>Entrar</h1>
        <p className={estilos.descricao}>
          Organize seus currículos e prepare a próxima candidatura.
        </p>
        <form onSubmit={enviar} noValidate>
          <Field
            rotulo="Identificador"
            name="identificador"
            autoComplete="username"
            placeholder="Ex.: seu nome ou apelido"
            ajuda="Use sempre o mesmo identificador para encontrar seus dados. Não há senha."
            value={identificador}
            onChange={(evento) => setIdentificador(evento.target.value)}
            erro={erroValidacao ?? login.error?.message}
          />
          <div className={estilos.acoes}>
            <Button type="submit" variante="primary" larguraTotal carregando={login.isPending}>
              {login.isPending ? "Entrando…" : "Entrar"}
            </Button>
          </div>
        </form>
      </div>
    </main>
  );
}
