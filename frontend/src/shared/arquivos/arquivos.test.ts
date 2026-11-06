import { arquivoParaBase64, base64ParaBlob, baixarArquivo, validarArquivoPdf } from "./arquivos";

describe("arquivoParaBase64", () => {
  it("converte o conteúdo do arquivo em base64 sem o prefixo data:", async () => {
    const arquivo = new File(["%PDF-1.4 teste"], "cv.pdf", { type: "application/pdf" });

    const base64 = await arquivoParaBase64(arquivo);

    expect(base64).toBe(btoa("%PDF-1.4 teste"));
  });
});

describe("base64ParaBlob", () => {
  it("reconstrói os bytes com o tipo informado", async () => {
    const blob = base64ParaBlob(btoa("%PDF-1.4 teste"), "application/pdf");

    expect(blob.type).toBe("application/pdf");
    expect(atob(await arquivoParaBase64(blob))).toBe("%PDF-1.4 teste");
  });

  it("usa application/pdf como tipo padrão", () => {
    expect(base64ParaBlob(btoa("x")).type).toBe("application/pdf");
  });

  it("faz o caminho de ida e volta com arquivoParaBase64", async () => {
    const original = new File([new Uint8Array([0, 255, 37, 80])], "bin.pdf");

    const base64Original = await arquivoParaBase64(original);

    const blob = base64ParaBlob(base64Original);

    expect(await arquivoParaBase64(blob)).toBe(base64Original);
    expect(blob.size).toBe(4);
  });
});

describe("baixarArquivo", () => {
  it("dispara o download com o nome informado e libera a URL", () => {
    const criarUrl = vi.fn(() => "blob:teste");
    const revogarUrl = vi.fn();
    vi.stubGlobal("URL", { ...URL, createObjectURL: criarUrl, revokeObjectURL: revogarUrl });
    const cliques: string[] = [];
    const clicar = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (
      this: HTMLAnchorElement,
    ) {
      cliques.push(this.download);
    });

    baixarArquivo(new Blob(["x"]), "curriculo.pdf");

    expect(cliques).toEqual(["curriculo.pdf"]);
    expect(revogarUrl).toHaveBeenCalledWith("blob:teste");
    clicar.mockRestore();
    vi.unstubAllGlobals();
  });
});

describe("validarArquivoPdf", () => {
  const pdf = (tamanho: number, nome = "cv.pdf", tipo = "application/pdf") =>
    new File([new Uint8Array(tamanho)], nome, { type: tipo });

  it("aceita PDF de até 5 MB", () => {
    expect(validarArquivoPdf(pdf(5 * 1024 * 1024))).toBeUndefined();
  });

  it("exige um arquivo", () => {
    expect(validarArquivoPdf(null)).toBe("Escolha um arquivo PDF.");
  });

  it("recusa arquivos que não são PDF", () => {
    expect(validarArquivoPdf(pdf(10, "cv.docx", "application/msword"))).toBe(
      "O arquivo precisa ser um PDF.",
    );
  });

  it("recusa PDF acima de 5 MB", () => {
    expect(validarArquivoPdf(pdf(5 * 1024 * 1024 + 1))).toBe("O arquivo tem mais de 5 MB.");
  });
});
