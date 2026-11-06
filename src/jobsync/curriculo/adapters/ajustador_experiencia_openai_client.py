"""Adapter OpenAI para adaptar uma experiência profissional por vez."""
from __future__ import annotations

from jobsync.curriculo.domain.ajustador_experiencia_port import AjustadorExperienciaPort
from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI
from jobsync.vaga.domain.analise_vaga import AnaliseVaga, TipoRequisitoTecnico

_NOME_IDIOMA = {
    "pt": "português do Brasil",
    "en": "inglês (formato americano de currículo)",
}

_PROMPT_SISTEMA = """\
Você adapta descrições de experiências profissionais para uma vaga específica.
Reescreva somente a descrição da experiência, preservando todos os fatos e sem
inventar responsabilidades, tecnologias, resultados ou métricas. Não repita
cargo, empresa ou período no texto de saída. Responda somente em JSON no formato:
{"descricao_ajustada": "descrição da experiência reescrita"}
"""


class AjustadorExperienciaOpenAIClient(AjustadorExperienciaPort):
    """Adapta a descrição de uma experiência sem alterar seus metadados."""

    def __init__(self, cliente_openai: ClienteOpenAI | None = None) -> None:
        self._cliente_openai = cliente_openai or ClienteOpenAI()

    def ajustar(
        self,
        experiencia: ExperienciaParaAvaliacao,
        descricao_vaga: str,
        idioma_alvo: str,
        analise_vaga: AnaliseVaga,
    ) -> ExperienciaParaAvaliacao:
        if not experiencia.descricao.strip():
            return experiencia

        requisitos_explicitos = [
            requisito.nome
            for requisito in analise_vaga.requisitos
            if requisito.tipo == TipoRequisitoTecnico.EXPLICITO
        ]
        requisitos_implicitos = [
            requisito.nome
            for requisito in analise_vaga.requisitos
            if requisito.tipo == TipoRequisitoTecnico.IMPLICITO
        ]
        nome_idioma = _NOME_IDIOMA.get(idioma_alvo, idioma_alvo)
        prompt_usuario = (
            f"Experiência profissional:\n"
            f"- Cargo: {experiencia.cargo or 'não informado'}\n"
            f"- Empresa: {experiencia.empresa or 'não informada'}\n"
            f"- Período: {experiencia.periodo or 'não informado'}\n"
            f"- Descrição original: {experiencia.descricao}\n\n"
            f"Descrição da vaga-alvo:\n{descricao_vaga}\n\n"
            f"Requisitos explícitos da vaga: {', '.join(requisitos_explicitos) or 'nenhum'}\n"
            f"Requisitos implícitos da vaga: {', '.join(requisitos_implicitos) or 'nenhum'}\n\n"
            f"Idioma de saída obrigatório: {nome_idioma}\n"
            "Destaque somente aspectos da descrição original relevantes à vaga. "
            "Se não houver evidência no texto original para um requisito, não o acrescente."
        )
        resposta = self._cliente_openai.solicitar_json(
            prompt_sistema=_PROMPT_SISTEMA,
            prompt_usuario=prompt_usuario,
        )
        descricao_ajustada = resposta.get("descricao_ajustada")
        if not isinstance(descricao_ajustada, str) or not descricao_ajustada.strip():
            raise ValueError("O modelo não retornou uma descrição de experiência ajustada.")

        return ExperienciaParaAvaliacao(
            descricao=descricao_ajustada.strip(),
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
        )
