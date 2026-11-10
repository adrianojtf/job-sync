import { defineConfig, devices } from "@playwright/test";

const PORTA_API = 8010;
const PORTA_UI = 5180;
const PYTHON = process.env.E2E_PYTHON ?? "python3";

/**
 * E2E contra a API real (PostgreSQL, casos de uso e PDF reais) com dublês só nas portas de IA
 * (src/jobsync/tests/e2e/app_e2e.py) e a UI no build de produção (vite preview + proxy /v1).
 */
export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  workers: 1,
  reporter: process.env.CI ? [["github"], ["list"]] : "list",
  use: {
    baseURL: `http://localhost:${PORTA_UI}`,
    trace: "off",
    acceptDownloads: true,
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: `${PYTHON} -m uvicorn jobsync.tests.e2e.app_e2e:app --port ${PORTA_API}`,
      cwd: "..",
      env: {
        PYTHONPATH: "src",
        DATABASE_URL: process.env.E2E_DATABASE_URL ?? "postgresql://localhost:5432/job_sync_e2e",
        // Login por identificador, só para os testes prepararem dados sem passar pelo e-mail.
        AUTH_LOGIN_SIMPLES_HABILITADO: "true",
        AUTH_BASE_URL_FRONTEND: `http://localhost:${PORTA_UI}`,
      },
      url: `http://localhost:${PORTA_API}/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
    {
      command: `npm run build && npx vite preview --port ${PORTA_UI} --strictPort`,
      env: { VITE_API_PROXY: `http://localhost:${PORTA_API}` },
      url: `http://localhost:${PORTA_UI}`,
      reuseExistingServer: !process.env.CI,
      timeout: 180_000,
    },
  ],
});
