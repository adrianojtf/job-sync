"""Implementação PostgreSQL de PerfilEstruturadoRepository.

Uma linha por `perfil_identificador` (upsert, sem histórico/versionamento —
decisão confirmada no PRD). As sub-listas (experiências, formações,
certificações, idiomas, tecnologias) ficam em colunas JSONB, já que não há
necessidade de consultar por campos individuais delas.
"""
from __future__ import annotations

from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

from jobsync.perfil_estruturado.domain.perfil_estruturado import (
    Certificacao,
    Conquista,
    ExperienciaProfissional,
    FormacaoAcademica,
    Idioma,
    NivelIdioma,
    OrigemConquista,
    PerfilEstruturado,
)
from jobsync.perfil_estruturado.domain.perfil_estruturado_repository import PerfilEstruturadoRepository


class PerfilEstruturadoRepositoryImpl(PerfilEstruturadoRepository):
    """Implementação PostgreSQL da porta de Perfil Estruturado."""

    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def salvar(self, perfil: PerfilEstruturado) -> PerfilEstruturado:
        with self._pool.connection() as conexao:
            conexao.execute(
                """
                INSERT INTO perfil_estruturado (
                    perfil_identificador, nome_completo, email, linkedin, resumo_profissional,
                    experiencias_json, formacoes_json, certificacoes_json, idiomas_json, tecnologias_json
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT(perfil_identificador) DO UPDATE SET
                    nome_completo = excluded.nome_completo,
                    email = excluded.email,
                    linkedin = excluded.linkedin,
                    resumo_profissional = excluded.resumo_profissional,
                    experiencias_json = excluded.experiencias_json,
                    formacoes_json = excluded.formacoes_json,
                    certificacoes_json = excluded.certificacoes_json,
                    idiomas_json = excluded.idiomas_json,
                    tecnologias_json = excluded.tecnologias_json
                """,
                (
                    perfil.perfil_identificador,
                    perfil.nome_completo,
                    perfil.email,
                    perfil.linkedin,
                    perfil.resumo_profissional,
                    Jsonb([self._experiencia_para_json(e) for e in perfil.experiencias]),
                    Jsonb([f.__dict__ for f in perfil.formacoes]),
                    Jsonb([c.__dict__ for c in perfil.certificacoes]),
                    Jsonb([{"idioma": i.idioma, "nivel": i.nivel.name} for i in perfil.idiomas]),
                    Jsonb(list(perfil.tecnologias)),
                ),
            )
        return perfil

    @staticmethod
    def _experiencia_para_json(experiencia: ExperienciaProfissional) -> dict:
        return {
            "empresa": experiencia.empresa,
            "cargo": experiencia.cargo,
            "periodo": experiencia.periodo,
            "descricao": experiencia.descricao,
            "contexto": experiencia.contexto,
            "responsabilidades": list(experiencia.responsabilidades),
            "skills": list(experiencia.skills),
            "conquistas": [
                {"texto": conquista.texto, "origem": conquista.origem.name}
                for conquista in experiencia.conquistas
            ],
        }

    @staticmethod
    def _json_para_experiencia(dados: dict) -> ExperienciaProfissional:
        """Perfis salvos antes do banco de conquistas e dos quatro blocos não têm essas chaves."""
        return ExperienciaProfissional(
            empresa=dados["empresa"],
            cargo=dados["cargo"],
            periodo=dados["periodo"],
            descricao=dados["descricao"],
            conquistas=tuple(
                Conquista(texto=c["texto"], origem=OrigemConquista[c["origem"]])
                for c in dados.get("conquistas", [])
            ),
            contexto=dados.get("contexto", ""),
            responsabilidades=tuple(dados.get("responsabilidades", [])),
            skills=tuple(dados.get("skills", [])),
        )

    def buscar_por_perfil(self, perfil_identificador: str) -> PerfilEstruturado | None:
        with self._pool.connection() as conexao:
            linha = conexao.execute(
                """
                SELECT nome_completo, email, linkedin, resumo_profissional,
                       experiencias_json, formacoes_json, certificacoes_json, idiomas_json, tecnologias_json
                FROM perfil_estruturado
                WHERE perfil_identificador = %s
                """,
                (perfil_identificador,),
            ).fetchone()
        if linha is None:
            return None
        return self._linha_para_perfil_estruturado(perfil_identificador, linha)

    @staticmethod
    def _linha_para_perfil_estruturado(perfil_identificador: str, linha: tuple) -> PerfilEstruturado:
        (
            nome_completo,
            email,
            linkedin,
            resumo_profissional,
            experiencias,
            formacoes,
            certificacoes,
            idiomas,
            tecnologias,
        ) = linha

        return PerfilEstruturado(
            perfil_identificador=perfil_identificador,
            nome_completo=nome_completo,
            email=email,
            linkedin=linkedin,
            resumo_profissional=resumo_profissional,
            experiencias=tuple(PerfilEstruturadoRepositoryImpl._json_para_experiencia(e) for e in experiencias),
            formacoes=tuple(FormacaoAcademica(**f) for f in formacoes),
            certificacoes=tuple(Certificacao(**c) for c in certificacoes),
            idiomas=tuple(Idioma(idioma=i["idioma"], nivel=NivelIdioma[i["nivel"]]) for i in idiomas),
            tecnologias=tuple(tecnologias),
        )
