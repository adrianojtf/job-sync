"""Domain Service: converte um PerfilEstruturado no Curriculo já existente (Fase 0).

Cada seção do Curriculo é montada concatenando as entradas estruturadas
correspondentes em texto formatado. Seções sem conteúdo são omitidas — se
nenhuma seção tiver conteúdo, retorna None, para a UI tratar como "perfil
inexistente" e cair no fluxo de upload de PDF já existente.
"""
from __future__ import annotations

from domain.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from domain.perfil_estruturado import PerfilEstruturado

_NIVEL_LABEL = {
    "BASICO": "Básico",
    "INTERMEDIARIO": "Intermediário",
    "AVANCADO": "Avançado",
    "FLUENTE": "Fluente",
    "NATIVO": "Nativo",
}

_TITULOS: dict[TipoSecao, str] = {
    TipoSecao.TECNOLOGIAS: "Tecnologias",
    TipoSecao.PERFIL: "Perfil",
    TipoSecao.EXPERIENCIAS: "Experiências",
    TipoSecao.FORMACAO: "Formação acadêmica",
    TipoSecao.CERTIFICACOES: "Certificações",
    TipoSecao.IDIOMAS: "Idiomas",
}


class MontarCurriculoDoPerfilEstruturado:
    """Constrói um Curriculo a partir dos dados estruturados do perfil, sem IA."""

    def executar(self, perfil: PerfilEstruturado) -> Curriculo | None:
        secoes: list[SecaoCurriculo] = []

        if perfil.resumo_profissional.strip():
            secoes.append(
                SecaoCurriculo(TipoSecao.PERFIL, _TITULOS[TipoSecao.PERFIL], perfil.resumo_profissional.strip())
            )

        if perfil.experiencias:
            conteudo = "\n\n".join(
                f"{exp.cargo} — {exp.empresa} ({exp.periodo})\n{exp.descricao}".strip()
                for exp in perfil.experiencias
            )
            secoes.append(SecaoCurriculo(TipoSecao.EXPERIENCIAS, _TITULOS[TipoSecao.EXPERIENCIAS], conteudo))

        if perfil.formacoes:
            conteudo = "\n\n".join(
                f"{formacao.curso} — {formacao.instituicao} ({formacao.periodo})"
                for formacao in perfil.formacoes
            )
            secoes.append(SecaoCurriculo(TipoSecao.FORMACAO, _TITULOS[TipoSecao.FORMACAO], conteudo))

        if perfil.certificacoes:
            conteudo = "\n".join(
                f"{cert.nome} — {cert.instituicao} ({cert.ano})" for cert in perfil.certificacoes
            )
            secoes.append(SecaoCurriculo(TipoSecao.CERTIFICACOES, _TITULOS[TipoSecao.CERTIFICACOES], conteudo))

        if perfil.idiomas:
            conteudo = "\n".join(
                f"{idioma.idioma} — {_NIVEL_LABEL[idioma.nivel.name]}" for idioma in perfil.idiomas
            )
            secoes.append(SecaoCurriculo(TipoSecao.IDIOMAS, _TITULOS[TipoSecao.IDIOMAS], conteudo))

        if perfil.tecnologias:
            conteudo = ", ".join(perfil.tecnologias)
            secoes.append(SecaoCurriculo(TipoSecao.TECNOLOGIAS, _TITULOS[TipoSecao.TECNOLOGIAS], conteudo))

        if not secoes:
            return None

        return Curriculo(
            nome_completo=perfil.nome_completo,
            email=perfil.email,
            linkedin=perfil.linkedin,
            secoes=tuple(secoes),
        )
