import type { CategoriaFormulario } from "./campos-curriculo";
import { anunciosDeTags } from "./anuncios-de-tags";
import { idDaCategoria, idDaTag } from "./competencias";

const categorias: CategoriaFormulario[] = [
  { nome: "Linguagens", tags: ["Java"] },
  { nome: " ", tags: [] },
];
const anuncios = anunciosDeTags(() => categorias);
const ativo = { id: idDaTag(0, "Java") };

describe("anunciosDeTags", () => {
  it("anuncia ao pegar a tag, com a categoria de origem", () => {
    expect(anuncios.onDragStart!({ active: ativo } as never)).toBe("Tag Java pega em Linguagens.");
  });

  it("anuncia sobre qual categoria a tag está, nomeando a categoria sem nome pela posição", () => {
    expect(anuncios.onDragOver!({ active: ativo, over: { id: idDaCategoria(1) } } as never)).toBe(
      "Tag Java sobre Categoria 2.",
    );
  });

  it("anuncia que a tag saiu das categorias", () => {
    expect(anuncios.onDragOver!({ active: ativo, over: null } as never)).toBe(
      "Tag Java fora das categorias.",
    );
  });

  it("anuncia onde a tag foi solta", () => {
    expect(anuncios.onDragEnd!({ active: ativo, over: { id: idDaTag(0, "Java") } } as never)).toBe(
      "Tag Java solta em Linguagens.",
    );
  });

  it("anuncia que nada mudou ao soltar fora ou cancelar", () => {
    expect(anuncios.onDragEnd!({ active: ativo, over: null } as never)).toBe(
      "Tag Java solta fora das categorias. Nada foi alterado.",
    );
    expect(anuncios.onDragCancel!({ active: ativo, over: null } as never)).toBe(
      "Movimento da tag Java cancelado. Nada foi alterado.",
    );
  });
});
