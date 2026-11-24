/** Uma linha por item: linhas em branco e espaços nas pontas são ignorados. */
export function textoParaLinhas(texto: string): string[] {
  return texto
    .split("\n")
    .map((linha) => linha.trim())
    .filter((linha) => linha !== "");
}

export function linhasParaTexto(linhas: string[]): string {
  return linhas.join("\n");
}
