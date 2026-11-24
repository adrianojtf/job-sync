"""Adapter OpenAI (implementa CompletadorBlocosExperienciaPort): gera só os blocos ausentes de uma experiência."""
from __future__ import annotations

from jobsync.perfil_estruturado.domain.blocos_experiencia import BlocosExperiencia, ExperienciaParaCompletar
from jobsync.perfil_estruturado.domain.completador_blocos_experiencia_port import (
    CompletadorBlocosExperienciaPort,
)
from jobsync.perfil_estruturado.domain.exceptions import CompletarBlocosIndisponivel
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI
from jobsync.shared_kernel.domain.rotulos_blocos_experiencia import BlocoExperiencia

_MAXIMO_DE_ITENS = 5

_NOME_IDIOMA = {"pt": "português do Brasil", "en": "inglês (formato americano de currículo)"}

_CHAVE_DO_BLOCO = {
    BlocoExperiencia.CONTEXTO: "contexto",
    BlocoExperiencia.RESPONSABILIDADES: "responsabilidades",
    BlocoExperiencia.REALIZACOES: "realizacoes",
    BlocoExperiencia.SKILLS: "skills",
}

_PROMPT_SISTEMA = """\
Você completa os blocos ausentes de uma experiência profissional de um currículo.
Responda somente em JSON, com as chaves dos blocos pedidos:
{"contexto": "parágrafo", "responsabilidades": ["..."], "realizacoes": ["..."], "skills": ["..."]}

Regras:
- Gere somente os blocos pedidos; não repita nem reescreva os blocos já existentes.
- Contexto: de 1 a 3 frases sobre a empresa, a área, o time e o papel, sem repetir as realizações.
- Responsabilidades: de 3 a 5 frases curtas sobre o que o profissional faz no dia a dia, cada uma com verbo de ação.
- Realizações: de 3 a 5 frases curtas com verbo de ação e, quando houver dado, o resultado medido.
- Skills: tecnologias e competências realmente citadas ou claramente implícitas no texto, sem repetição.
- Prefira sempre os fatos e números do texto original. Quando faltarem, proponha contextos, volumes e métricas
  plausíveis e conservadores para o setor e o papel (ex.: em sistema bancário, transações, conciliação, prazos).
- Não invente empresas, datas nem formações. Não altere cargo, empresa nem período e não os repita no texto.
"""

_ERRO_FORMATO = "O modelo devolveu os blocos da experiência fora do formato esperado."


class CompletadorBlocosExperienciaOpenAIClient(CompletadorBlocosExperienciaPort):
    """Pede à IA somente os blocos que faltam, com o que já foi reconhecido como contexto."""

    def __init__(self, cliente_openai: ClienteOpenAI | None = None) -> None:
        self._cliente_openai = cliente_openai or ClienteOpenAI()

    def completar(self, experiencia: ExperienciaParaCompletar, idioma: str | None = None) -> BlocosExperiencia:
        ausentes = experiencia.reconhecidos.ausentes
        try:
            resposta = self._cliente_openai.solicitar_json(
                prompt_sistema=_PROMPT_SISTEMA,
                prompt_usuario=self._prompt_do_usuario(experiencia, ausentes, idioma),
            )
            return self._blocos(resposta, ausentes)
        except (ValueError, RuntimeError) as erro:
            raise CompletarBlocosIndisponivel() from erro

    @staticmethod
    def _prompt_do_usuario(
        experiencia: ExperienciaParaCompletar, ausentes: tuple[BlocoExperiencia, ...], idioma: str | None
    ) -> str:
        reconhecidos = experiencia.reconhecidos
        existentes = "\n".join(
            linha
            for linha in (
                f"- Contexto: {reconhecidos.contexto}" if reconhecidos.contexto else "",
                "- Responsabilidades: " + "; ".join(reconhecidos.responsabilidades)
                if reconhecidos.responsabilidades
                else "",
                "- Realizações: " + "; ".join(reconhecidos.realizacoes) if reconhecidos.realizacoes else "",
                "- Skills: " + ", ".join(reconhecidos.skills) if reconhecidos.skills else "",
            )
            if linha
        )
        idioma_de_saida = (
            _NOME_IDIOMA.get(idioma, idioma) if idioma else "o mesmo idioma do texto original da experiência"
        )
        return (
            "Experiência profissional:\n"
            f"- Cargo: {experiencia.cargo or 'não informado'}\n"
            f"- Empresa: {experiencia.empresa or 'não informada'}\n"
            f"- Período: {experiencia.periodo or 'não informado'}\n"
            f"- Texto original: {experiencia.resto.strip() or '(não informado)'}\n\n"
            f"Blocos já existentes (não alterar):\n{existentes or '(nenhum)'}\n\n"
            f"Blocos a gerar: {', '.join(_CHAVE_DO_BLOCO[bloco] for bloco in ausentes)}\n"
            f"Idioma de saída obrigatório: {idioma_de_saida}"
        )

    @staticmethod
    def _blocos(resposta: object, ausentes: tuple[BlocoExperiencia, ...]) -> BlocosExperiencia:
        if not isinstance(resposta, dict):
            raise ValueError(_ERRO_FORMATO)
        campos: dict[str, object] = {}
        for bloco in ausentes:
            chave = _CHAVE_DO_BLOCO[bloco]
            valor = resposta.get(chave)
            if bloco == BlocoExperiencia.CONTEXTO:
                if not isinstance(valor, str) or not valor.strip():
                    raise ValueError(_ERRO_FORMATO)
                campos[chave] = valor.strip()
            else:
                if (
                    not isinstance(valor, list)
                    or not valor
                    or not all(isinstance(item, str) and item.strip() for item in valor)
                ):
                    raise ValueError(_ERRO_FORMATO)
                campos[chave] = tuple(item.strip() for item in valor[:_MAXIMO_DE_ITENS])
        return BlocosExperiencia(**campos)
