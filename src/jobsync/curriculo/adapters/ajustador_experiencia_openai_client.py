"""Adapter OpenAI para adaptar uma experiência profissional por vez, nos quatro blocos (uma chamada)."""
from __future__ import annotations

from jobsync.curriculo.domain.ajustador_experiencia_port import AjustadorExperienciaPort
from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.contexto_vaga import ContextoVaga
from jobsync.curriculo.domain.equivalencia_tecnologia import DiretrizesExperiencia
from jobsync.curriculo.adapters.prompt_contexto_vaga import (
    REGRA_RESPONSABILIDADES_IMPLICITAS,
    REGRA_SELECAO_DE_CONQUISTAS,
    linha_cargo_alvo,
)
from jobsync.curriculo.adapters.prompt_refino import bloco_refino
from jobsync.curriculo.domain.experiencia_adaptada import ExperienciaAdaptada
from jobsync.curriculo.domain.refino import PedidoRefino
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI
from jobsync.vaga.domain.analise_vaga import AnaliseVaga, TipoRequisitoTecnico

_NOME_IDIOMA = {
    "pt": "português do Brasil",
    "en": "inglês (formato americano de currículo)",
}

_ERRO_FORMATO = (
    "O modelo devolveu conquistas, contexto, responsabilidades e skills fora do formato esperado."
)

_MAXIMO_DE_ITENS = 5
_MAXIMO_DE_SKILLS = 15

_PROMPT_SISTEMA = f"""\
Você adapta experiências profissionais de um currículo para uma vaga específica, nos quatro
blocos: contexto, responsabilidades, conquistas (as principais realizações) e skills.
Responda somente em JSON no formato:
{{"contexto": "parágrafo de contexto", "responsabilidades": ["responsabilidade 1"],
  "conquistas": ["conquista 1", "conquista 2"], "skills": ["Java", "SQL"]}}

Regras:
- Conquistas: de 3 a 5 frases curtas, no idioma de saída, cada uma começando com verbo de ação
  e, quando houver dado, citando o resultado medido.
- Responsabilidades: de 3 a 5 frases curtas sobre o que o profissional faz no dia a dia, no idioma de
  saída, cada uma começando com verbo de ação, sem repetir as conquistas.
- Skills: as tecnologias e competências usadas na experiência, sem repetição, priorizando as da vaga
  que o texto sustenta.
- Prefira sempre os números e fatos da descrição original. Quando ela não trouxer número,
  você pode propor métricas e volumes plausíveis e conservadores.
- Contexto: de 1 a 3 frases sobre a empresa, a área e o papel, sem repetir as conquistas.
- Destaque o que é mais relevante para a vaga. Use o cargo-alvo para escolher a ênfase e o vocabulário.
- Não invente empresas nem datas. Não acrescente tecnologias além das que estão no texto e das trocas indicadas.
- {REGRA_RESPONSABILIDADES_IMPLICITAS}
- Não altere cargo, empresa nem período e não os repita no texto de saída.
"""


class AjustadorExperienciaOpenAIClient(AjustadorExperienciaPort):
    """Escreve uma experiência em conquistas e contexto sem alterar seus metadados."""

    def __init__(self, cliente_openai: ClienteOpenAI | None = None) -> None:
        self._cliente_openai = cliente_openai or ClienteOpenAI()

    def ajustar(
        self,
        experiencia: ExperienciaParaAvaliacao,
        contexto: ContextoVaga,
        diretrizes: DiretrizesExperiencia,
    ) -> ExperienciaAdaptada:
        if not self._tem_conteudo(experiencia):
            return self._sem_conteudo(experiencia)

        return self._solicitar(
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
            texto_da_experiencia=(
                f"- Descrição original: {experiencia.descricao.strip() or '(não informada)'}"
                f"{self._blocos_cadastrados(experiencia)}"
                f"{self._conquistas_cadastradas(experiencia.conquistas)}"
                f"{self._ajustes_de_tecnologia(diretrizes)}"
            ),
            contexto=contexto,
        )

    def refinar(
        self, experiencia: ExperienciaAdaptada, contexto: ContextoVaga, refino: PedidoRefino
    ) -> ExperienciaAdaptada:
        conquistas_atuais = "\n".join(f"- {conquista}" for conquista in experiencia.conquistas)
        responsabilidades_atuais = "\n".join(f"- {item}" for item in experiencia.responsabilidades)
        return self._solicitar(
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
            texto_da_experiencia=(
                "- Conquistas atuais (reescreva a partir delas):\n"
                f"{conquistas_atuais or '(nenhuma)'}\n"
                "- Responsabilidades atuais (reescreva a partir delas):\n"
                f"{responsabilidades_atuais or '(nenhuma)'}\n"
                f"- Contexto atual: {experiencia.contexto.strip() or '(nenhum)'}\n"
                f"- Skills atuais: {', '.join(experiencia.skills) or '(nenhuma)'}\n"
                "- Mantenha as tecnologias já citadas nas conquistas, no contexto, nas responsabilidades e nas skills atuais.\n\n"
                f"{bloco_refino(refino, com_vaga=True)}"
            ),
            contexto=contexto,
        )

    @staticmethod
    def _tem_conteudo(experiencia: ExperienciaParaAvaliacao) -> bool:
        return bool(
            experiencia.descricao.strip()
            or experiencia.conquistas
            or experiencia.contexto.strip()
            or experiencia.responsabilidades
            or experiencia.skills
        )

    @staticmethod
    def _blocos_cadastrados(experiencia: ExperienciaParaAvaliacao) -> str:
        """Contexto, responsabilidades e skills já cadastrados no perfil; vazio quando não há nenhum."""
        linhas = []
        if experiencia.contexto.strip():
            linhas.append(f"- Contexto cadastrado: {experiencia.contexto.strip()}")
        if experiencia.responsabilidades:
            itens = "\n".join(f"  - {item}" for item in experiencia.responsabilidades)
            linhas.append(f"- Responsabilidades cadastradas:\n{itens}")
        if experiencia.skills:
            linhas.append(f"- Skills cadastradas: {', '.join(experiencia.skills)}")
        return "\n" + "\n".join(linhas) if linhas else ""

    @staticmethod
    def _conquistas_cadastradas(conquistas: tuple[str, ...]) -> str:
        """Bloco do banco de conquistas (JOB-0042); vazio quando a experiência não tem conquistas."""
        if not conquistas:
            return ""
        lista = "\n".join(f"- {conquista}" for conquista in conquistas)
        return f"\n\nConquistas cadastradas pelo usuário:\n{lista}\n\n{REGRA_SELECAO_DE_CONQUISTAS}"

    @staticmethod
    def _ajustes_de_tecnologia(diretrizes: DiretrizesExperiencia) -> str:
        """Trocas e manutenções que o `PlanoAdaptacao` definiu para esta experiência."""
        linhas = [
            f"- Use {troca.alvo} no lugar de {troca.original} e cite {troca.alvo} de forma explícita "
            f"no contexto, dizendo em que parte do trabalho foi usada, e inclua {troca.alvo} nas skills no lugar de "
            f"{troca.original}."
            for troca in diretrizes.trocar
        ] + [
            f"- Mantenha {tecnologia} e cite {tecnologia} de forma explícita no contexto, "
            "dizendo em que parte do trabalho foi usada."
            for tecnologia in diretrizes.manter
        ]
        return "\n\nAjustes de tecnologia nesta experiência:\n" + "\n".join(linhas) if linhas else ""

    @staticmethod
    def _sem_conteudo(experiencia: ExperienciaParaAvaliacao) -> ExperienciaAdaptada:
        """Sem texto de origem, não há o que adaptar sem inventar a experiência inteira."""
        return ExperienciaAdaptada(
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
            conquistas=(),
        )

    def _solicitar(
        self,
        cargo: str,
        empresa: str,
        periodo: str,
        texto_da_experiencia: str,
        contexto: ContextoVaga,
    ) -> ExperienciaAdaptada:
        resposta = self._cliente_openai.solicitar_json(
            prompt_sistema=_PROMPT_SISTEMA,
            prompt_usuario=(
                "Experiência profissional:\n"
                f"- Cargo: {cargo or 'não informado'}\n"
                f"- Empresa: {empresa or 'não informada'}\n"
                f"- Período: {periodo or 'não informado'}\n"
                f"{texto_da_experiencia}\n\n"
                f"{linha_cargo_alvo(contexto)}"
                f"Descrição da vaga-alvo:\n{contexto.descricao_vaga}\n\n"
                f"{self._requisitos(contexto.analise_vaga)}\n\n"
                f"Idioma de saída obrigatório: {_NOME_IDIOMA.get(contexto.idioma_alvo, contexto.idioma_alvo)}"
            ),
        )
        return ExperienciaAdaptada(
            cargo=cargo,
            empresa=empresa,
            periodo=periodo,
            conquistas=self._conquistas(resposta),
            contexto=self._contexto(resposta),
            responsabilidades=self._itens(resposta, "responsabilidades", _MAXIMO_DE_ITENS),
            skills=self._itens(resposta, "skills", _MAXIMO_DE_SKILLS),
        )

    @staticmethod
    def _requisitos(analise_vaga: AnaliseVaga) -> str:
        def nomes(tipo: TipoRequisitoTecnico) -> str:
            return ", ".join(r.nome for r in analise_vaga.requisitos if r.tipo == tipo) or "nenhum"

        return (
            f"Requisitos explícitos da vaga: {nomes(TipoRequisitoTecnico.EXPLICITO)}\n"
            f"Requisitos implícitos da vaga: {nomes(TipoRequisitoTecnico.IMPLICITO)}"
        )

    @staticmethod
    def _conquistas(resposta: dict) -> tuple[str, ...]:
        conquistas = resposta.get("conquistas")
        if (
            not isinstance(conquistas, list)
            or not conquistas
            or not all(isinstance(c, str) and c.strip() for c in conquistas)
        ):
            raise ValueError(_ERRO_FORMATO)
        return tuple(c.strip() for c in conquistas[:_MAXIMO_DE_ITENS])

    @staticmethod
    def _itens(resposta: dict, chave: str, maximo: int) -> tuple[str, ...]:
        """Lista opcional de textos: ausente vira vazia; presente, precisa ser lista de textos."""
        itens = resposta.get(chave)
        if itens is None:
            return ()
        if not isinstance(itens, list) or not all(isinstance(item, str) and item.strip() for item in itens):
            raise ValueError(_ERRO_FORMATO)
        return tuple(item.strip() for item in itens[:maximo])

    @staticmethod
    def _contexto(resposta: dict) -> str:
        contexto = resposta.get("contexto")
        if contexto is None:
            return ""
        if not isinstance(contexto, str):
            raise ValueError(_ERRO_FORMATO)
        return contexto.strip()
