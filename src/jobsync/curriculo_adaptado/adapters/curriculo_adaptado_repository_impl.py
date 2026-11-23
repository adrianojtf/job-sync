"""Implementação PostgreSQL de CurriculoAdaptadoRepository.

O rascunho e a análise da vaga ficam em colunas JSONB: não há consulta por campos deles, só
leitura e gravação do conteúdo inteiro. Toda consulta filtra por `perfil_identificador`.
"""
from __future__ import annotations

from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

from jobsync.curriculo_adaptado.adapters.serializador_conteudo import (
    analise_de_json,
    analise_para_json,
    rascunho_de_json,
    rascunho_para_json,
)
from jobsync.curriculo_adaptado.domain.curriculo_adaptado import CurriculoAdaptado
from jobsync.curriculo_adaptado.domain.curriculo_adaptado_repository import (
    CurriculoAdaptadoRepository,
)

_COLUNAS = """
    id, perfil_identificador, nome_referencia, cargo_alvo, empresa_alvo, idioma_alvo,
    descricao_vaga, analise_vaga_json, conteudo_json, curriculo_salvo_id, criado_em, atualizado_em
"""


class CurriculoAdaptadoRepositoryImpl(CurriculoAdaptadoRepository):
    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def salvar(self, curriculo: CurriculoAdaptado) -> CurriculoAdaptado:
        with self._pool.connection() as conexao:
            conexao.execute(
                f"""
                INSERT INTO curriculo_adaptado ({_COLUNAS})
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    nome_referencia = excluded.nome_referencia,
                    cargo_alvo = excluded.cargo_alvo,
                    empresa_alvo = excluded.empresa_alvo,
                    idioma_alvo = excluded.idioma_alvo,
                    descricao_vaga = excluded.descricao_vaga,
                    analise_vaga_json = excluded.analise_vaga_json,
                    conteudo_json = excluded.conteudo_json,
                    curriculo_salvo_id = excluded.curriculo_salvo_id,
                    atualizado_em = excluded.atualizado_em
                WHERE curriculo_adaptado.perfil_identificador = excluded.perfil_identificador
                """,
                (
                    curriculo.id,
                    curriculo.perfil_identificador,
                    curriculo.nome_referencia,
                    curriculo.cargo_alvo,
                    curriculo.empresa_alvo,
                    curriculo.idioma_alvo,
                    curriculo.descricao_vaga,
                    Jsonb(analise_para_json(curriculo.analise_vaga)),
                    Jsonb(rascunho_para_json(curriculo.rascunho)),
                    curriculo.curriculo_salvo_id,
                    curriculo.criado_em,
                    curriculo.atualizado_em,
                ),
            )
        return curriculo

    def buscar(self, curriculo_id: str, perfil_identificador: str) -> CurriculoAdaptado | None:
        with self._pool.connection() as conexao:
            linha = conexao.execute(
                f"SELECT {_COLUNAS} FROM curriculo_adaptado WHERE id = %s AND perfil_identificador = %s",
                (curriculo_id, perfil_identificador),
            ).fetchone()
        return None if linha is None else self._linha_para_curriculo(linha)

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[CurriculoAdaptado, ...]:
        with self._pool.connection() as conexao:
            linhas = conexao.execute(
                f"""
                SELECT {_COLUNAS} FROM curriculo_adaptado
                WHERE perfil_identificador = %s
                ORDER BY atualizado_em DESC, id COLLATE "C" DESC
                """,
                (perfil_identificador,),
            ).fetchall()
        return tuple(self._linha_para_curriculo(linha) for linha in linhas)

    def vincular_curriculo_salvo(
        self, curriculo_id: str, perfil_identificador: str, curriculo_salvo_id: str
    ) -> None:
        with self._pool.connection() as conexao:
            conexao.execute(
                """
                UPDATE curriculo_adaptado SET curriculo_salvo_id = %s
                WHERE id = %s AND perfil_identificador = %s
                """,
                (curriculo_salvo_id, curriculo_id, perfil_identificador),
            )

    @staticmethod
    def _linha_para_curriculo(linha: tuple) -> CurriculoAdaptado:
        (
            id_,
            perfil_identificador,
            nome_referencia,
            cargo_alvo,
            empresa_alvo,
            idioma_alvo,
            descricao_vaga,
            analise_json,
            conteudo_json,
            curriculo_salvo_id,
            criado_em,
            atualizado_em,
        ) = linha
        return CurriculoAdaptado(
            id=id_,
            perfil_identificador=perfil_identificador,
            nome_referencia=nome_referencia,
            cargo_alvo=cargo_alvo,
            empresa_alvo=empresa_alvo,
            idioma_alvo=idioma_alvo,
            descricao_vaga=descricao_vaga,
            analise_vaga=analise_de_json(analise_json),
            rascunho=rascunho_de_json(conteudo_json),
            curriculo_salvo_id=curriculo_salvo_id,
            criado_em=criado_em,
            atualizado_em=atualizado_em,
        )
