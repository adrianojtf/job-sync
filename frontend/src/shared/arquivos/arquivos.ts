/** Lê um arquivo do navegador e devolve o conteúdo em base64 (sem o prefixo data:). */
export function arquivoParaBase64(arquivo: Blob): Promise<string> {
  return new Promise((resolver, rejeitar) => {
    const leitor = new FileReader();
    leitor.onload = () => {
      const dataUrl = String(leitor.result);
      resolver(dataUrl.slice(dataUrl.indexOf(",") + 1));
    };
    leitor.onerror = () => rejeitar(leitor.error ?? new Error("Falha ao ler o arquivo."));
    leitor.readAsDataURL(arquivo);
  });
}

/** Converte conteúdo base64 (como devolvido pela API) em Blob para download ou pré-visualização. */
export function base64ParaBlob(base64: string, tipo = "application/pdf"): Blob {
  const binario = atob(base64);
  const bytes = Uint8Array.from(binario, (caractere) => caractere.charCodeAt(0));
  return new Blob([bytes], { type: tipo });
}

/** Dispara o download de um Blob no navegador com o nome informado. */
export function baixarArquivo(conteudo: Blob, nomeArquivo: string): void {
  const url = URL.createObjectURL(conteudo);
  const link = document.createElement("a");
  link.href = url;
  link.download = nomeArquivo;
  link.click();
  URL.revokeObjectURL(url);
}

export const TAMANHO_MAXIMO_PDF_BYTES = 5 * 1024 * 1024;

/** Valida um PDF antes do envio. Devolve a mensagem de erro ou undefined se o arquivo for aceito. */
export function validarArquivoPdf(arquivo: File | null | undefined): string | undefined {
  if (!arquivo) return "Escolha um arquivo PDF.";
  const ehPdf = arquivo.type === "application/pdf" || arquivo.name.toLowerCase().endsWith(".pdf");
  if (!ehPdf) return "O arquivo precisa ser um PDF.";
  if (arquivo.size > TAMANHO_MAXIMO_PDF_BYTES) return "O arquivo tem mais de 5 MB.";
  return undefined;
}
