import type { CategoriaFormulario } from "./campos-curriculo";
import {
  adicionarTags,
  categoriasDeTexto,
  categoriasParaTexto,
  idDaCategoria,
  idDaTag,
  lerIdDoArrasto,
  separarTags,
  soltarTag,
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

describe("identificadores do arrastar e soltar", () => {
  it("lê o identificador de categoria e de tag", () => {
    expect(lerIdDoArrasto(idDaCategoria(2))).toEqual({ tipo: "categoria", categoria: 2 });
    expect(lerIdDoArrasto(idDaTag(1, "C#"))).toEqual({ tipo: "tag", categoria: 1, tag: "C#" });
  });

  it("mantém os dois-pontos que fazem parte da tag", () => {
    expect(lerIdDoArrasto(idDaTag(0, "Node: LTS"))).toEqual({
      tipo: "tag",
      categoria: 0,
      tag: "Node: LTS",
    });
  });

  it("devolve null para um identificador desconhecido", () => {
    expect(lerIdDoArrasto("outra-coisa")).toBeNull();
  });
});

describe("soltarTag", () => {
  const categorias: CategoriaFormulario[] = [
    { nome: "Linguagens", tags: ["Java", "Python", "Go"] },
    { nome: "Bancos", tags: ["SQL"] },
    { nome: "Vazia", tags: [] },
  ];

  it("reordena dentro da categoria, sobre outra tag", () => {
    const resultado = soltarTag(categorias, idDaTag(0, "Go"), idDaTag(0, "Java"));

    expect(resultado?.categorias[0]?.tags).toEqual(["Go", "Java", "Python"]);
    expect(resultado).toMatchObject({ de: 0, para: 0, tag: "Go" });
  });

  it("solta no fim da própria categoria quando o alvo é a categoria", () => {
    const resultado = soltarTag(categorias, idDaTag(0, "Java"), idDaCategoria(0));

    expect(resultado?.categorias[0]?.tags).toEqual(["Python", "Go", "Java"]);
  });

  it("move para outra categoria na posição da tag alvo", () => {
    const resultado = soltarTag(categorias, idDaTag(0, "Python"), idDaTag(1, "SQL"));

    expect(resultado?.categorias.map((c) => c.tags)).toEqual([
      ["Java", "Go"],
      ["Python", "SQL"],
      [],
    ]);
    expect(resultado).toMatchObject({ de: 0, para: 1, tag: "Python" });
  });

  it("move para o fim de uma categoria vazia", () => {
    const resultado = soltarTag(categorias, idDaTag(1, "SQL"), idDaCategoria(2));

    expect(resultado?.categorias.map((c) => c.tags)).toEqual([
      ["Java", "Python", "Go"],
      [],
      ["SQL"],
    ]);
  });

  it("não duplica a tag no destino, sem diferenciar a caixa: ela só sai da origem", () => {
    const comRepetida = [
      { nome: "A", tags: ["Java"] },
      { nome: "B", tags: ["java", "SQL"] },
    ];

    const resultado = soltarTag(comRepetida, idDaTag(0, "Java"), idDaCategoria(1));

    expect(resultado?.categorias.map((c) => c.tags)).toEqual([[], ["java", "SQL"]]);
  });

  it("não altera o valor original", () => {
    soltarTag(categorias, idDaTag(0, "Go"), idDaCategoria(1));

    expect(categorias[0]?.tags).toEqual(["Java", "Python", "Go"]);
  });

  it.each([
    ["solta fora de qualquer alvo", idDaTag(0, "Java"), null],
    ["solta na mesma posição", idDaTag(0, "Java"), idDaTag(0, "Java")],
    ["solta no fim estando já no fim", idDaTag(0, "Go"), idDaCategoria(0)],
    ["arrasta uma categoria", idDaCategoria(0), idDaCategoria(1)],
    ["tag que não existe mais", idDaTag(0, "Rust"), idDaCategoria(1)],
    ["categoria destino inexistente", idDaTag(0, "Java"), idDaCategoria(9)],
  ])("devolve null quando %s", (_descricao, ativo, sobre) => {
    expect(soltarTag(categorias, ativo, sobre)).toBeNull();
  });
});
