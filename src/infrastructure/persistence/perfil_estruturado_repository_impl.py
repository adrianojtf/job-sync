"""Implementação SQLite de PerfilEstruturadoRepository.

Uma linha por `perfil_identificador` (upsert, sem histórico/versionamento —
decisão confirmada no PRD). As sub-listas (experiências, formações,
certificações, idiomas, tecnologias) são serializadas como JSON em colunas de
texto, já que não há necessidade de consultar por campos individuais delas.
"""
from __future__ import annotations

import json

from domain.perfil_estruturado import (
    Certificacao,
    ExperienciaProfissional,
    FormacaoAcademica,
    Idioma,
    NivelIdioma,
    PerfilEstruturado,
)
from domain.perfil_estruturado.perfil_estruturado_repository import PerfilEstruturadoRepository
from infrastructure.persistence._conexao_sqlite import criar_conexao


class PerfilEstruturadoRepositoryImpl(PerfilEstruturadoRepository):
    """Implementação SQLite da porta de Perfil Estruturado."""

    def __init__(self, caminho_banco: str) -> None:
        self._conexao = criar_conexao(caminho_banco)

    def salvar(self, perfil: PerfilEstruturado) -> PerfilEstruturado:
        self._conexao.execute(
            """
            INSERT INTO perfil_estruturado (
                perfil_identificador, nome_completo, email, linkedin, resumo_profissional,
                experiencias_json, formacoes_json, certificacoes_json, idiomas_json, tecnologias_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                json.dumps([e.__dict__ for e in perfil.experiencias]),
                json.dumps([f.__dict__ for f in perfil.formacoes]),
                json.dumps([c.__dict__ for c in perfil.certificacoes]),
                json.dumps([{"idioma": i.idioma, "nivel": i.nivel.name} for i in perfil.idiomas]),
                json.dumps(list(perfil.tecnologias)),
            ),
        )
        self._conexao.commit()
        return perfil

    def buscar_por_perfil(self, perfil_identificador: str) -> PerfilEstruturado | None:
        cursor = self._conexao.execute(
            """
            SELECT nome_completo, email, linkedin, resumo_profissional,
                   experiencias_json, formacoes_json, certificacoes_json, idiomas_json, tecnologias_json
            FROM perfil_estruturado
            WHERE perfil_identificador = ?
            """,
            (perfil_identificador,),
        )
        linha = cursor.fetchone()
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
            experiencias_json,
            formacoes_json,
            certificacoes_json,
            idiomas_json,
            tecnologias_json,
        ) = linha

        experiencias = tuple(ExperienciaProfissional(**e) for e in json.loads(experiencias_json))
        formacoes = tuple(FormacaoAcademica(**f) for f in json.loads(formacoes_json))
        certificacoes = tuple(Certificacao(**c) for c in json.loads(certificacoes_json))
        idiomas = tuple(
            Idioma(idioma=i["idioma"], nivel=NivelIdioma[i["nivel"]]) for i in json.loads(idiomas_json)
        )
        tecnologias = tuple(json.loads(tecnologias_json))

        return PerfilEstruturado(
            perfil_identificador=perfil_identificador,
            nome_completo=nome_completo,
            email=email,
            linkedin=linkedin,
            resumo_profissional=resumo_profissional,
            experiencias=experiencias,
            formacoes=formacoes,
            certificacoes=certificacoes,
            idiomas=idiomas,
            tecnologias=tecnologias,
        )
