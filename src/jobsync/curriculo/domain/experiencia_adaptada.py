"""Value Object: uma experiência profissional adaptada, com os quatro blocos.

Cada experiência do currículo adaptado segue um padrão: contexto sobre a empresa e o papel,
responsabilidades, realizações (as conquistas) e skills. Cargo, empresa e período identificam
a experiência e não mudam na adaptação.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.shared_kernel.domain.rotulos_blocos_experiencia import BlocoExperiencia, rotulo_do_bloco


def _preenchido(valor: str) -> bool:
    return bool(valor and valor.strip())


@dataclass(frozen=True)
class ExperienciaAdaptada:
    cargo: str
    empresa: str
    periodo: str
    conquistas: tuple[str, ...]
    contexto: str = ""
    responsabilidades: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not _preenchido(self.cargo):
            raise ValueError("Informe o cargo de cada experiência profissional.")
        if not _preenchido(self.empresa):
            raise ValueError("Informe a empresa de cada experiência profissional.")
        if not all(_preenchido(conquista) for conquista in self.conquistas):
            raise ValueError("Cada conquista da experiência precisa de texto.")
        if not all(_preenchido(responsabilidade) for responsabilidade in self.responsabilidades):
            raise ValueError("Cada responsabilidade da experiência precisa de texto.")
        if not all(_preenchido(skill) for skill in self.skills):
            raise ValueError("Cada skill da experiência precisa de texto.")

    @property
    def tem_conteudo(self) -> bool:
        """Indica se há ao menos um dos quatro blocos para trabalhar."""
        return bool(self.conquistas or self.responsabilidades or self.skills) or _preenchido(self.contexto)

    @classmethod
    def revisada(
        cls,
        cargo: str,
        empresa: str,
        periodo: str,
        conquistas: Iterable[str],
        contexto: str,
        responsabilidades: Iterable[str] = (),
        skills: Iterable[str] = (),
    ) -> ExperienciaAdaptada | None:
        """Monta a experiência editada pelo usuário; devolve None se tudo ficou em branco."""
        conquistas_revisadas = tuple(c.strip() for c in conquistas if _preenchido(c))
        responsabilidades_revisadas = tuple(r.strip() for r in responsabilidades if _preenchido(r))
        skills_revisadas = tuple(skill.strip() for skill in skills if _preenchido(skill))
        if not any(
            (
                _preenchido(cargo),
                _preenchido(empresa),
                _preenchido(periodo),
                conquistas_revisadas,
                _preenchido(contexto),
                responsabilidades_revisadas,
                skills_revisadas,
            )
        ):
            return None
        return cls(
            cargo=cargo.strip(),
            empresa=empresa.strip(),
            periodo=periodo.strip(),
            conquistas=conquistas_revisadas,
            contexto=contexto.strip(),
            responsabilidades=responsabilidades_revisadas,
            skills=skills_revisadas,
        )

    def como_descricao(self) -> str:
        """Os quatro blocos por linha, sem marcadores nem rótulos: o texto que a IA recebe e mede."""
        return "\n".join(self._linhas_dos_blocos(com_marcador=False))

    def para_texto(self, idioma_alvo: str) -> str:
        """Texto da experiência no formato que o gerador de PDF reconhece, com os rótulos do idioma.

        Com responsabilidades ou skills, cada bloco leva o seu rótulo (contexto, responsabilidades,
        realizações e skills). Sem elas, mantém o formato anterior: conquistas e, no fim, o contexto.
        """
        rotulo_contexto = rotulo_do_bloco(BlocoExperiencia.CONTEXTO, idioma_alvo)
        if not (self.responsabilidades or self.skills):
            linhas = [self._cabecalho(), *(f"- {conquista}" for conquista in self.conquistas)]
            if _preenchido(self.contexto):
                linhas.append(f"{rotulo_contexto}: {self.contexto.strip()}")
            return "\n".join(linhas)

        linhas = [self._cabecalho()]
        if _preenchido(self.contexto):
            linhas.append(f"{rotulo_contexto}: {self.contexto.strip()}")
        for bloco, itens in (
            (BlocoExperiencia.RESPONSABILIDADES, self.responsabilidades),
            (BlocoExperiencia.REALIZACOES, self.conquistas),
        ):
            if itens:
                linhas.append(f"{rotulo_do_bloco(bloco, idioma_alvo)}:")
                linhas.extend(f"- {item}" for item in itens)
        if self.skills:
            linhas.append(f"{rotulo_do_bloco(BlocoExperiencia.SKILLS, idioma_alvo)}: {' | '.join(self.skills)}")
        return "\n".join(linhas)

    def para_avaliacao(self) -> ExperienciaParaAvaliacao:
        """Experiência para o avaliador: os quatro blocos, sem cabeçalho nem rótulo."""
        return ExperienciaParaAvaliacao(
            descricao="\n".join(self._linhas_dos_blocos(com_marcador=True)),
            cargo=self.cargo,
            empresa=self.empresa,
            periodo=self.periodo,
        )

    def _linhas_dos_blocos(self, com_marcador: bool) -> list[str]:
        marcador = "- " if com_marcador else ""
        linhas = [f"{marcador}{item}" for item in (*self.responsabilidades, *self.conquistas)]
        if _preenchido(self.contexto):
            linhas.append(self.contexto.strip())
        if self.skills:
            linhas.append(", ".join(self.skills))
        return linhas

    def _cabecalho(self) -> str:
        identificacao = f"{self.cargo.strip()} — {self.empresa.strip()}"
        if not _preenchido(self.periodo):
            return identificacao
        return f"{identificacao} ({self.periodo.strip()})"
