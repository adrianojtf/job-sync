import { useQuery } from "@tanstack/react-query";
import { useApiClient } from "../api/api-client-context";

/** Tela provisória da fundação: confirma a conexão com a API até o AppShell (tarefa 4.0). */
export function App() {
  const api = useApiClient();
  const saude = useQuery({ queryKey: ["saude"], queryFn: () => api.verificarSaude() });

  return (
    <main>
      <h1>job-sync</h1>
      <p role="status">
        {saude.isPending && "Verificando a API…"}
        {saude.isSuccess && "API disponível"}
        {saude.isError && `API indisponível: ${saude.error.message}`}
      </p>
    </main>
  );
}
