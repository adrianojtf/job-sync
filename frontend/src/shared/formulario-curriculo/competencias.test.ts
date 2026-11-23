import type { CategoriaFormulario } from "./campos-curriculo";
import {
  adicionarTags,
  categoriasDeTexto,
  categoriasParaTexto,
  separarTags,
  virgulaAbreNovaTag,
} from "./competencias";

describe("separarTags", () => {
  it("separa por vírgula e apara os espaços", () => {
    expect(separarTags("Go, Rust ,  Kotlin")).toEqual(["Go", "Rust", "Kotlin"]);
  });

  it("não separa vírgulas dentro de parênteses", () => {
    expect(separarTags("Spring (Boot, Data), NestJS")).toEqual(["Spring (Boot, Data)", "NestJS"]);
  });

  it("descarta itens vazios", () => {
    expect(separarTags(" , ,Java,, ")).toEqual(["Java"]);
  });
});

describe("virgulaAbreNovaTag", () => {
  it("é verdadeira fora de parênteses", () => {
    expect(virgulaAbreNovaTag("Spring")).toBe(true);
  });

  it("é falsa com parêntese aberto", () => {
    expect(virgulaAbreNovaTag("Spring (Boot")).toBe(false);
  });

  it("volta a ser verdadeira com o parêntese fechado", () => {
    expect(virgulaAbreNovaTag("Spring (Boot)")).toBe(true);
  });
});

describe("adicionarTags", () => {
  it("acrescenta as tags novas ao fim", () => {
    expect(adicionarTags(["Java"], ["Go", "Rust"])).toEqual(["Java", "Go", "Rust"]);
  });

  it("ignora repetidas sem diferenciar maiúsculas e minúsculas", () => {
    expect(adicionarTags(["Java"], ["java", "JAVA", "Go", "go"])).toEqual(["Java", "Go"]);
  });
});

describe("categoriasDeTexto", () => {
  it("lê uma categoria por linha", () => {
    expect(categoriasDeTexto("Linguagens: Java, Python\nBancos de Dados: SQL, PostgreSQL")).toEqual(
      [
        { nome: "Linguagens", tags: ["Java", "Python"] },
        { nome: "Bancos de Dados", tags: ["SQL", "PostgreSQL"] },
      ],
    );
  });

  it("aceita marcadores no início da linha", () => {
    expect(
      categoriasDeTexto("- Linguagens: Java\n• Frontend: React\n* Ferramentas: Git").map(
        (categoria) => categoria.nome,
      ),
    ).toEqual(["Linguagens", "Frontend", "Ferramentas"]);
  });

  it("junta as linhas sem rótulo na categoria padrão", () => {
    expect(categoriasDeTexto("Java, Python\nSQL")).toEqual([
      { nome: "Tecnologias", tags: ["Java", "Python", "SQL"] },
    ]);
  });

  it("só o primeiro dois-pontos separa o rótulo", () => {
    expect(categoriasDeTexto("Versões: Java 17, Node: 20")).toEqual([
      { nome: "Versões", tags: ["Java 17", "Node: 20"] },
    ]);
  });

  it("ignora linhas em branco e categorias sem tags", () => {
    expect(categoriasDeTexto("\nLinguagens: Java\n\nVazia:\n")).toEqual([
      { nome: "Linguagens", tags: ["Java"] },
    ]);
  });

  it("texto vazio não gera categorias", () => {
    expect(categoriasDeTexto("  \n ")).toEqual([]);
  });
});

describe("categoriasParaTexto", () => {
  it("escreve uma categoria por linha", () => {
    const categorias: CategoriaFormulario[] = [
      { nome: "Linguagens", tags: ["Java", "Python"] },
      { nome: "Frontend", tags: ["React"] },
    ];

    expect(categoriasParaTexto(categorias)).toBe("Linguagens: Java, Python\nFrontend: React");
  });

  it("ida e volta preserva as categorias", () => {
    const categorias: CategoriaFormulario[] = [
      { nome: "Backend", tags: ["Spring (Boot, Data)", "NestJS"] },
      { nome: "Ferramentas", tags: ["Git", "Docker"] },
    ];

    expect(categoriasDeTexto(categoriasParaTexto(categorias))).toEqual(categorias);
  });

  it("ignora categorias sem nome ou sem tags", () => {
    expect(
      categoriasParaTexto([
        { nome: "", tags: ["Java"] },
        { nome: "Vazia", tags: [] },
        { nome: "Ok", tags: ["Git"] },
      ]),
    ).toBe("Ok: Git");
  });
});
