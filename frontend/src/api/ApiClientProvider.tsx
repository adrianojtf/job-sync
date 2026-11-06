import type { ReactNode } from "react";
import type { ApiClient } from "./api-client";
import { ApiClientContext } from "./api-client-context";

interface Props {
  cliente: ApiClient;
  children: ReactNode;
}

export function ApiClientProvider({ cliente, children }: Props) {
  return <ApiClientContext.Provider value={cliente}>{children}</ApiClientContext.Provider>;
}
