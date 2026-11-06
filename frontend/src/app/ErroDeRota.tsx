import { useEffect } from "react";
import { useRouteError } from "react-router-dom";
import { FalhaInesperada } from "./FalhaInesperada";
import { registrarErro } from "./registrar-erro";

export function ErroDeRota() {
  const erro = useRouteError();
  useEffect(() => registrarErro(erro), [erro]);
  return <FalhaInesperada />;
}
