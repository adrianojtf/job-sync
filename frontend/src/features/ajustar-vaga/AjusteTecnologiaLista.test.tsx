import { render, screen } from "@testing-library/react";
import { AjusteTecnologiaLista } from "./AjusteTecnologiaLista";

describe("AjusteTecnologiaLista", () => {
  it("lista cada troca de tecnologia com a experiência que a recebeu", () => {
    render(
      <AjusteTecnologiaLista
        ajustes={[
          {
            indice_experiencia: 0,
            cargo: "Dev Full Stack",
            empresa: "Empresa X",
            original: "React",
            alvo: "Angular",
          },
          {
            indice_experiencia: 1,
            cargo: "Dev Backend",
            empresa: "Empresa Y",
            original: "MySQL",
            alvo: "PostgreSQL",
          },
        ]}
      />,
    );

    const lista = screen.getByRole("list", { name: "Ajustes de tecnologia" });
    expect(screen.getByRole("heading", { name: "Ajustes de tecnologia" })).toBeInTheDocument();
    expect(lista.querySelectorAll("li")).toHaveLength(2);
    expect(lista).toHaveTextContent("React → Angular em Dev Full Stack — Empresa X");
    expect(lista).toHaveTextContent("MySQL → PostgreSQL em Dev Backend — Empresa Y");
  });

  it("não aparece quando a IA não trocou tecnologias", () => {
    const { container } = render(<AjusteTecnologiaLista ajustes={[]} />);

    expect(container).toBeEmptyDOMElement();
  });
});
