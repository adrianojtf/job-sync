"""Caso de uso: login com e-mail e senha, com limite de tentativas por e-mail e por IP."""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional

from jobsync.autenticacao.domain.configuracao import ConfiguracaoAutenticacao
from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import (
    CredenciaisInvalidas,
    EmailInvalido,
    LimiteTentativasExcedido,
)
from jobsync.autenticacao.domain.hasher_senha import HasherSenha
from jobsync.autenticacao.domain.limite_tentativas_repository import LimiteTentativasRepository
from jobsync.autenticacao.domain.token_opaco import chave_de_limite, gerar_token
from jobsync.autenticacao.domain.usuario_repository import UsuarioRepository
from jobsync.autenticacao.service_layer.emitir_sessao.service import EmitirSessao
from jobsync.autenticacao.service_layer.sessao_iniciada import SessaoIniciada
from jobsync.shared_kernel.domain.relogio import agora_utc

logger = logging.getLogger(__name__)


@dataclass
class EntrarComSenha:
    _usuarios: UsuarioRepository
    _limites: LimiteTentativasRepository
    _hasher: HasherSenha
    _emitir_sessao: EmitirSessao
    _config: ConfiguracaoAutenticacao
    _relogio: Callable[[], datetime] = agora_utc
    _hash_ficticio: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._hash_ficticio = self._hasher.gerar(gerar_token())

    def executar(self, email: str, senha: str, ip: Optional[str]) -> SessaoIniciada:
        try:
            email_vo = Email(email)
        except EmailInvalido as erro:
            raise CredenciaisInvalidas("E-mail ou senha incorretos.") from erro
        chave_email = chave_de_limite("email", email_vo.valor)
        chaves = [chave_email] + ([chave_de_limite("ip", ip)] if ip else [])
        self._recusar_se_bloqueado(chaves)

        usuario = self._usuarios.buscar_por_email(email_vo)
        senha_hash = self._usuarios.obter_senha_hash(usuario.id) if usuario else None
        # Sempre confere um hash, mesmo sem usuário, para o tempo de resposta não revelar o e-mail.
        confere = self._hasher.conferir(senha, senha_hash or self._hash_ficticio)
        if not (confere and usuario is not None and senha_hash is not None and usuario.email_verificado):
            self._registrar_falha(chaves)
            raise CredenciaisInvalidas("E-mail ou senha incorretos.")

        self._limites.limpar(chave_email)
        token = self._emitir_sessao.executar(usuario.id)
        logger.info("login_sucesso metodo=senha usuario_id=%s", usuario.id)
        return SessaoIniciada(token=token, usuario=usuario)

    def _recusar_se_bloqueado(self, chaves: list[str]) -> None:
        agora = self._relogio()
        for chave in chaves:
            limite = self._limites.obter(chave)
            if limite is not None and limite.bloqueado(agora):
                logger.warning("login_bloqueado chave=%s", chave)
                restante = (limite.bloqueado_ate - agora).total_seconds()
                raise LimiteTentativasExcedido(math.ceil(restante))

    def _registrar_falha(self, chaves: list[str]) -> None:
        agora = self._relogio()
        for chave in chaves:
            self._limites.registrar_falha(chave, agora, self._config.politica_limite)
        logger.warning("login_falha chave=%s", chaves[0])
