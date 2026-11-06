import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { servidorApi } from "./servidor-api";

beforeAll(() => servidorApi.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  cleanup();
  servidorApi.resetHandlers();
});
afterAll(() => servidorApi.close());
