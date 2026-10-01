from __future__ import annotations

import gettext
import locale
from pathlib import Path

DOMAIN = "bloguero"
LOCALE_DIR = Path(__file__).parent


def install() -> None:
    try:
        locale.setlocale(locale.LC_ALL, "")
    except locale.Error:
        pass  # locale del sistema no instalado: seguimos con el idioma por defecto (es)
    gettext.bindtextdomain(DOMAIN, str(LOCALE_DIR))
    gettext.textdomain(DOMAIN)


def _(message: str) -> str:
    return gettext.dgettext(DOMAIN, message)
