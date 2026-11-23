import { render, screen } from "@testing-library/react";
import { LacunasTecnologiaAviso } from "./LacunasTecnologiaAviso";

describe("LacunasTecnologiaAviso", () => {
  it("lista as tecnologias da vaga que o perfil não mostra e orienta a adicionar a tag", () => {
    render(<LacunasTecnologiaAviso lacunas={["Kafka", "RabbitMQ"]} />);

    expect(
      screen.getByRole("region", { name: "Tecnologias da vaga fora das competências" }),
    ).toHaveTextContent("Tecnologias da vaga que seu perfil não mostra: Kafka, RabbitMQ.");
    expect(screen.getByText(/Se você as usa, adicione a tag em Competências/)).toBeInTheDocument();
  });

  it("não mostra nada sem lacunas", () => {
    const { container } = render(<LacunasTecnologiaAviso lacunas={[]} />);

    expect(container).toBeEmptyDOMElement();
  });
});
