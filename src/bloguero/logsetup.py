"""Registro de errores en ~/.cache/bloguero/bloguero.log.

Lanzada desde el menú, la salida de errores iría a /dev/null: sin este fichero, un fallo de sincronización que la
aplicación atrapa (y muestra como «Sin conexión») no dejaría ningún rastro. Se guarda solo lo que se registra
(el tipo de error y su traza), nunca el contenido de las entradas ni las credenciales.
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from bloguero.store import CACHE_DIR

LOG_PATH = CACHE_DIR / "bloguero.log"


def setup() -> None:
    """Enciende el registro en fichero; si no se puede escribir, la aplicación sigue sin él."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(LOG_PATH, maxBytes=200_000, backupCount=1, encoding="utf-8")
    except OSError:
        return
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger("bloguero")
    root.setLevel(logging.INFO)
    root.addHandler(handler)
