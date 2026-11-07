"""Value Object: uma experiência profissional adaptada, com conquistas e contexto.

Cada experiência do currículo adaptado segue um padrão: uma lista de conquistas
(achievements) e um parágrafo de contexto sobre a empresa e o papel. Cargo, empresa e
período identificam a experiência e não mudam na adaptação.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao


def _preenchido(valor: str) -> bool:
    return bool(valor and valor.strip())


@dataclass(frozen=True)
class ExperienciaAdaptada:
    cargo: str
    empresa: str
    periodo: str
    conquistas: tuple[str, ...]
    contexto: str = ""

    def __post_init__(self) -> None:
        if not _preenchido(self.cargo):
            raise ValueError("Informe o cargo de cada experiência profissional.")
        if not _preenchido(self.empresa):
            raise ValueError("Informe a empresa de cada experiência profissional.")
        if not all(_preenchido(conquista) for conquista in self.conquistas):
            raise ValueError("Cada conquista da experiência precisa de texto.")

    @property
    def tem_conteudo(self) -> bool:
        """Indica se há ao menos uma conquista ou um contexto para trabalhar."""
        return bool(self.conquistas) or _preenchido(self.contexto)

    @classmethod
    def revisada(
        cls,
        cargo: str,
        empresa: str,
        periodo: str,
        conquistas: Iterable[str],
        contexto: str,
    ) -> ExperienciaAdaptada | None:
        """Monta a experiência editada pelo usuário; devolve None se tudo ficou em branco."""
        conquistas_revisadas = tuple(c.strip() for c in conquistas if _preenchido(c))
        if not any(
            (_preenchido(cargo), _preenchido(empresa), _preenchido(periodo), conquistas_revisadas, _preenchido(contexto))
        ):
            return None
        return cls(
            cargo=cargo.strip(),
            empresa=empresa.strip(),
            periodo=periodo.strip(),
            conquistas=conquistas_revisadas,
            contexto=contexto.strip(),
        )

    def como_descricao(self) -> str:
        """Conquistas por linha, sem marcadores, e o contexto: o texto que a IA recebe e mede."""
        linhas = list(self.conquistas)
        if _preenchido(self.contexto):
            linhas.append(self.contexto.strip())
        return "\n".join(linhas)

    def para_texto(self, rotulo_contexto: str) -> str:
        """Texto da experiência no formato que o gerador de PDF reconhece."""
        linhas = [self._cabecalho(), *(f"- {conquista}" for conquista in self.conquistas)]
        if _preenchido(self.contexto):
            linhas.append(f"{rotulo_contexto}: {self.contexto.strip()}")
        return "\n".join(linhas)

    def para_avaliacao(self) -> ExperienciaParaAvaliacao:
        """Experiência para o avaliador: conquistas e contexto, sem cabeçalho nem rótulo."""
        linhas = [f"- {conquista}" for conquista in self.conquistas]
        if _preenchido(self.contexto):
            linhas.append(self.contexto.strip())
        return ExperienciaParaAvaliacao(
            descricao="\n".join(linhas),
            cargo=self.cargo,
            empresa=self.empresa,
            periodo=self.periodo,
        )

    def _cabecalho(self) -> str:
        identificacao = f"{self.cargo.strip()} — {self.empresa.strip()}"
        if not _preenchido(self.periodo):
            return identificacao
        return f"{identificacao} ({self.periodo.strip()})"
