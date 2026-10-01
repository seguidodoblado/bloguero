import gettext

from bloguero import i18n


def test_spanish_is_the_source_language_and_needs_no_catalog():
    assert i18n._("Conectar con Google") == "Conectar con Google"


def test_english_catalog_translates():
    translation = gettext.translation(
        i18n.DOMAIN, localedir=str(i18n.LOCALE_DIR), languages=["en"]
    )
    assert translation.gettext("Conectar con Google") == "Connect with Google"
    assert translation.gettext("Borrar") == "Delete"


def test_english_mo_file_exists():
    mo_path = i18n.LOCALE_DIR / "en" / "LC_MESSAGES" / f"{i18n.DOMAIN}.mo"
    assert mo_path.exists(), "Falta compilar po/en.po (ver po/README.md)"
