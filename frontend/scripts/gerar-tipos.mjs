// Gera src/api/schema.d.ts a partir do contrato OpenAPI do backend.
// Uso: npm run gerar-tipos  (OPENAPI_URL aceita URL ou caminho de arquivo)
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const origem = process.env.OPENAPI_URL ?? "http://localhost:8000/openapi.json";
const destino = fileURLToPath(new URL("../src/api/schema.d.ts", import.meta.url));
const cli = fileURLToPath(
  new URL("../node_modules/openapi-typescript/bin/cli.js", import.meta.url),
);

// --default-non-nullable=false: campos com valor padrão no backend continuam opcionais nas requisições.
execFileSync(process.execPath, [cli, origem, "--output", destino, "--default-non-nullable=false"], {
  stdio: "inherit",
});
