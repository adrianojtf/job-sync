"""Implementação PostgreSQL de UsuarioRepository."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from psycopg import errors
from psycopg_pool import ConnectionPool

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import IdentidadeJaVinculada, UsuarioDuplicado
from jobsync.autenticacao.domain.identidade_externa import IdentidadeExterna
from jobsync.autenticacao.domain.usuario import Usuario
from jobsync.autenticacao.domain.usuario_repository import UsuarioRepository

_COLUNAS = "u.id, u.email, u.email_verificado, u.nome, u.perfil_identificador, u.criado_em"


def _para_usuario(linha) -> Usuario:
    return Usuario(
        id=linha[0],
        email=Email(linha[1]),
        email_verificado=linha[2],
        nome=linha[3],
        perfil_identificador=linha[4],
        criado_em=linha[5],
    )


class UsuarioRepositoryImpl(UsuarioRepository):
    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def salvar_novo(self, usuario: Usuario) -> None:
        try:
            with self._pool.connection() as conexao:
                conexao.execute(
                    "INSERT INTO perfil (identificador) VALUES (%s) ON CONFLICT DO NOTHING",
                    (usuario.perfil_identificador,),
                )
                conexao.execute(
                    "INSERT INTO usuario (id, email, email_verificado, nome, perfil_identificador, criado_em)"
                    " VALUES (%s, %s, %s, %s, %s, %s)",
                    (
                        usuario.id,
                        usuario.email.valor,
                        usuario.email_verificado,
                        usuario.nome,
                        usuario.perfil_identificador,
                        usuario.criado_em,
                    ),
                )
        except errors.UniqueViolation as erro:
            raise UsuarioDuplicado("E-mail ou perfil já associado a outro usuário.") from erro

    def atualizar(self, usuario: Usuario) -> None:
        with self._pool.connection() as conexao:
            conexao.execute(
                "UPDATE usuario SET email_verificado = %s, nome = %s WHERE id = %s",
                (usuario.email_verificado, usuario.nome, usuario.id),
            )

    def _buscar(self, condicao: str, parametros: tuple) -> Optional[Usuario]:
        with self._pool.connection() as conexao:
            linha = conexao.execute(
                f"SELECT {_COLUNAS} FROM usuario u {condicao}", parametros
            ).fetchone()
        return _para_usuario(linha) if linha else None

    def buscar_por_id(self, usuario_id: UUID) -> Optional[Usuario]:
        return self._buscar("WHERE u.id = %s", (usuario_id,))

    def buscar_por_email(self, email: Email) -> Optional[Usuario]:
        return self._buscar("WHERE lower(u.email) = %s", (email.valor,))

    def buscar_por_perfil(self, perfil_identificador: str) -> Optional[Usuario]:
        return self._buscar("WHERE u.perfil_identificador = %s", (perfil_identificador,))

    def buscar_por_identidade(self, provedor: str, subject: str) -> Optional[Usuario]:
        return self._buscar(
            "JOIN identidade_externa i ON i.usuario_id = u.id WHERE i.provedor = %s AND i.subject = %s",
            (provedor, subject),
        )

    def vincular_identidade(self, identidade: IdentidadeExterna) -> None:
        try:
            with self._pool.connection() as conexao:
                conexao.execute(
                    "INSERT INTO identidade_externa (provedor, subject, usuario_id) VALUES (%s, %s, %s)",
                    (identidade.provedor, identidade.subject, identidade.usuario_id),
                )
        except errors.UniqueViolation as erro:
            raise IdentidadeJaVinculada("Identidade já vinculada.") from erro

    def obter_senha_hash(self, usuario_id: UUID) -> Optional[str]:
        with self._pool.connection() as conexao:
            linha = conexao.execute(
                "SELECT senha_hash FROM credencial_senha WHERE usuario_id = %s", (usuario_id,)
            ).fetchone()
        return linha[0] if linha else None

    def definir_senha_hash(self, usuario_id: UUID, senha_hash: str) -> None:
        with self._pool.connection() as conexao:
            conexao.execute(
                "INSERT INTO credencial_senha (usuario_id, senha_hash) VALUES (%s, %s)"
                " ON CONFLICT (usuario_id) DO UPDATE"
                " SET senha_hash = EXCLUDED.senha_hash, atualizada_em = now()",
                (usuario_id, senha_hash),
            )

    def remover_senha(self, usuario_id: UUID) -> None:
        with self._pool.connection() as conexao:
            conexao.execute("DELETE FROM credencial_senha WHERE usuario_id = %s", (usuario_id,))
