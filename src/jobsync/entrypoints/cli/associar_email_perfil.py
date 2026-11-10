"""Associa o e-mail do dono a um perfil criado antes da autenticação real.

Uso:
    python -m jobsync.entrypoints.cli.associar_email_perfil --perfil <identificador> --email <e-mail>

O comando não altera dados do perfil nem libera acesso por si só: o dono completa o vínculo no
primeiro login com esse e-mail verificado (Google ou link de confirmação por e-mail).

Códigos de saída: 0 sucesso, 1 erro inesperado, 2 dados inválidos (e-mail ou perfil),
3 banco inacessível, 4 conflito (perfil ou e-mail já associados a outro usuário).
"""
from __future__ import annotations

import argparse
import sys

import psycopg
from dotenv import load_dotenv

from jobsync.autenticacao.adapters import UsuarioRepositoryImpl
from jobsync.autenticacao.domain.exceptions import (
    EmailEmUso,
    EmailInvalido,
    PerfilInexistente,
    PerfilJaAssociado,
)
from jobsync.autenticacao.service_layer.associar_email_a_perfil import (
    AssociarEmailAPerfil,
    ResultadoAssociacao,
)
from jobsync.perfil.adapters import PerfilRepositoryImpl
from jobsync.shared_kernel.adapters.persistence.conexao_postgres import (
    ErroConexaoBanco,
    criar_pool,
    obter_url_banco,
)
from jobsync.shared_kernel.adapters.persistence.executor_migracoes import executar_migracoes

SUCESSO, ERRO_INESPERADO, DADOS_INVALIDOS, DESTINO_INVALIDO, CONFLITO = 0, 1, 2, 3, 4


def _argumentos(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Associa um e-mail a um perfil legado.")
    parser.add_argument("--perfil", required=True, help="Identificador do perfil existente")
    parser.add_argument("--email", required=True, help="E-mail do dono do perfil")
    return parser.parse_args(argv)


def principal(argv: list[str] | None = None) -> int:
    load_dotenv()
    args = _argumentos(argv)
    try:
        pool = criar_pool(obter_url_banco())
    except (ErroConexaoBanco, psycopg.OperationalError) as erro:
        print(f"Banco inacessível: {erro}", file=sys.stderr)
        return DESTINO_INVALIDO

    try:
        with pool.connection() as conexao:
            executar_migracoes(conexao)
        servico = AssociarEmailAPerfil(UsuarioRepositoryImpl(pool), PerfilRepositoryImpl(pool))
        resultado = servico.executar(args.perfil, args.email)
    except (EmailInvalido, PerfilInexistente) as erro:
        print(f"Dados inválidos: {erro}", file=sys.stderr)
        return DADOS_INVALIDOS
    except (PerfilJaAssociado, EmailEmUso) as erro:
        print(f"Conflito: {erro}", file=sys.stderr)
        return CONFLITO
    finally:
        pool.close()

    if resultado is ResultadoAssociacao.JA_ASSOCIADO:
        print(f"O perfil '{args.perfil}' já estava associado a esse e-mail. Nada foi alterado.")
    else:
        print(
            f"E-mail associado ao perfil '{args.perfil}'. "
            "O vínculo se completa no primeiro login com esse e-mail verificado."
        )
    return SUCESSO


if __name__ == "__main__":
    sys.exit(principal())
