import { Component, type ReactNode } from "react";
import { FalhaInesperada } from "./FalhaInesperada";
import { registrarErro } from "./registrar-erro";

interface Props {
  children: ReactNode;
}

interface Estado {
  falhou: boolean;
}

export class ErrorBoundary extends Component<Props, Estado> {
  state: Estado = { falhou: false };

  static getDerivedStateFromError(): Estado {
    return { falhou: true };
  }

  componentDidCatch(erro: Error): void {
    registrarErro(erro);
  }

  render() {
    return this.state.falhou ? <FalhaInesperada /> : this.props.children;
  }
}
