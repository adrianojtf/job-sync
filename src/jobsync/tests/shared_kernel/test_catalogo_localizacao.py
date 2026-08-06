"""Testes do Value Object CatalogoLocalizacao no shared kernel."""

from jobsync.shared_kernel.domain import CatalogoLocalizacao


def test_mapeia_secao_para_pt_e_en():
    catalogo = CatalogoLocalizacao()

    assert catalogo.localizar_secao("pt", "tecnologias") == "Tecnologias"
    assert catalogo.localizar_secao("en", "tecnologias") == "Technologies"


def test_fallback_para_idioma_desconhecido_usa_portugues():
    catalogo = CatalogoLocalizacao()

    assert catalogo.localizar_secao("fr", "perfil") == "Perfil"
    assert catalogo.localizar_categoria("fr", "Linguagens") == "Linguagens"


def test_preserva_rotulos_nao_mapeados():
    catalogo = CatalogoLocalizacao()

    assert catalogo.localizar_categoria("en", "Personal") == "Personal"
    assert catalogo.localizar_secao("en", "custom-key", fallback="Custom") == "Custom"


def test_normaliza_variantes_de_idioma_para_pt_e_en():
    catalogo = CatalogoLocalizacao()

    assert catalogo.normalizar_idioma("pt-BR") == "pt"
    assert catalogo.normalizar_idioma("en-US") == "en"
    assert catalogo.normalizar_idioma("fr") == "pt"


def test_localiza_categoria_usando_fallback_para_idioma_desconhecido():
    catalogo = CatalogoLocalizacao()

    assert catalogo.localizar_categoria("fr", "Languages") == "Linguagens"
    assert catalogo.localizar_categoria("fr", "Custom Category", fallback="Custom") == "Custom"
