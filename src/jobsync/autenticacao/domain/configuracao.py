"""Parâmetros de autenticação: prazos de sessão e de links, e política de bloqueio."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from jobsync.autenticacao.domain.limite_tentativa import PoliticaLimiteTentativas


@dataclass(frozen=True)
class ConfiguracaoAutenticacao:
    url_frontend: str = "http://localhost:8080"
    sessao_inatividade: timedelta = timedelta(days=7)
    sessao_maxima: timedelta = timedelta(days=30)
    sessao_renovacao_minima: timedelta = timedelta(minutes=5)
    validade_confirmacao_email: timedelta = timedelta(hours=24)
    validade_redefinicao_senha: timedelta = timedelta(hours=1)
    validade_estado_oauth: timedelta = timedelta(minutes=10)
    politica_limite: PoliticaLimiteTentativas = field(default_factory=PoliticaLimiteTentativas)
    # Um IP pode agrupar muita gente (NAT, escritório, proxy): o limite dele é bem mais folgado
    # que o da conta, só para frear tentativas em massa contra várias contas.
    politica_limite_ip: PoliticaLimiteTentativas = field(
        default_factory=lambda: PoliticaLimiteTentativas(max_falhas=30)
    )

    def link_do_frontend(self, caminho: str, **parametros: str) -> str:
        consulta = "&".join(f"{chave}={valor}" for chave, valor in parametros.items())
        base = f"{self.url_frontend.rstrip('/')}{caminho}"
        return f"{base}?{consulta}" if consulta else base
