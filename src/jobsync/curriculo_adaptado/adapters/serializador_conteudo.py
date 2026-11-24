"""Conversão do conteúdo do currículo adaptado de e para JSON (colunas JSONB).

O formato leva um número de versão: o rascunho evolui com o produto e o JSON já gravado
precisa continuar legível. Uma versão desconhecida é rejeitada em vez de lida às cegas.
"""
from __future__ import annotations

from typing import Any

from jobsync.curriculo import (
    AjusteTecnologia,
    CategoriaCompetencia,
    EquivalenciaTecnologia,
    ExperienciaAdaptada,
    RascunhoCurriculoAdaptado,
    SecaoCurriculo,
    TipoSecao,
)
from jobsync.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)

VERSAO_DO_FORMATO = 2
VERSOES_LEGIVEIS = (1, VERSAO_DO_FORMATO)


def rascunho_para_json(rascunho: RascunhoCurriculoAdaptado) -> dict[str, Any]:
    return {
        "versao": VERSAO_DO_FORMATO,
        "nome_completo": rascunho.nome_completo,
        "email": rascunho.email,
        "linkedin": rascunho.linkedin,
        "secoes": [
            {"tipo": secao.tipo.name, "titulo": secao.titulo, "conteudo": secao.conteudo}
            for secao in rascunho.secoes
        ],
        "experiencias": (
            None
            if rascunho.experiencias is None
            else [
                {
                    "cargo": experiencia.cargo,
                    "empresa": experiencia.empresa,
                    "periodo": experiencia.periodo,
                    "conquistas": list(experiencia.conquistas),
                    "contexto": experiencia.contexto,
                    "responsabilidades": list(experiencia.responsabilidades),
                    "skills": list(experiencia.skills),
                }
                for experiencia in rascunho.experiencias
            ]
        ),
        "titulo_experiencias": rascunho.titulo_experiencias,
        "competencias": (
            None
            if rascunho.competencias is None
            else [
                {"nome": categoria.nome, "tags": list(categoria.tags)}
                for categoria in rascunho.competencias
            ]
        ),
        "titulo_competencias": rascunho.titulo_competencias,
        "ajustes_tecnologia": [
            {
                "indice_experiencia": ajuste.indice_experiencia,
                "original": ajuste.equivalencia.original,
                "alvo": ajuste.equivalencia.alvo,
            }
            for ajuste in rascunho.ajustes_tecnologia
        ],
    }


def rascunho_de_json(conteudo: dict[str, Any]) -> RascunhoCurriculoAdaptado:
    versao = conteudo.get("versao")
    if versao not in VERSOES_LEGIVEIS:
        raise ValueError(f"A versão {versao!r} do conteúdo do currículo adaptado não é suportada.")
    experiencias = conteudo["experiencias"]
    competencias = conteudo["competencias"]
    return RascunhoCurriculoAdaptado(
        nome_completo=conteudo["nome_completo"],
        email=conteudo["email"],
        linkedin=conteudo["linkedin"],
        secoes=tuple(
            SecaoCurriculo(TipoSecao[secao["tipo"]], secao["titulo"], secao["conteudo"])
            for secao in conteudo["secoes"]
        ),
        experiencias=(
            None
            if experiencias is None
            else tuple(
                ExperienciaAdaptada(
                    cargo=experiencia["cargo"],
                    empresa=experiencia["empresa"],
                    periodo=experiencia["periodo"],
                    conquistas=tuple(experiencia["conquistas"]),
                    contexto=experiencia["contexto"],
                    responsabilidades=tuple(experiencia.get("responsabilidades", ())),
                    skills=tuple(experiencia.get("skills", ())),
                )
                for experiencia in experiencias
            )
        ),
        titulo_experiencias=conteudo["titulo_experiencias"],
        competencias=(
            None
            if competencias is None
            else tuple(
                CategoriaCompetencia(categoria["nome"], tuple(categoria["tags"]))
                for categoria in competencias
            )
        ),
        titulo_competencias=conteudo["titulo_competencias"],
        ajustes_tecnologia=tuple(
            AjusteTecnologia(
                ajuste["indice_experiencia"],
                EquivalenciaTecnologia(original=ajuste["original"], alvo=ajuste["alvo"]),
            )
            for ajuste in conteudo["ajustes_tecnologia"]
        ),
    )


def analise_para_json(analise: AnaliseVaga) -> dict[str, Any]:
    return {
        "requisitos": [
            {
                "nome": requisito.nome,
                "categoria": requisito.categoria.name,
                "tipo": requisito.tipo.name,
                "origem": requisito.origem.name,
            }
            for requisito in analise.requisitos
        ],
        "ambiguidade": list(analise.ambiguidade),
        "texto_original": analise.texto_original,
    }


def analise_de_json(conteudo: dict[str, Any]) -> AnaliseVaga:
    return AnaliseVaga(
        requisitos=tuple(
            RequisitoTecnico(
                nome=requisito["nome"],
                categoria=CategoriaRequisitoTecnico[requisito["categoria"]],
                tipo=TipoRequisitoTecnico[requisito["tipo"]],
                origem=OrigemRequisitoTecnico[requisito["origem"]],
            )
            for requisito in conteudo["requisitos"]
        ),
        ambiguidade=tuple(conteudo["ambiguidade"]),
        texto_original=conteudo["texto_original"],
    )
