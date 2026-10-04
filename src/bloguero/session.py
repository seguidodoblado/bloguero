"""Qué pantalla muestra Bloguero al arrancar, según haya sesión guardada y datos en la caché."""
from __future__ import annotations

# Estados de arranque
CONNECT = "connect"        # hay token guardado: se conecta con Google (carga si no hay caché)
OFFLINE_LOGIN = "offline_login"  # sin token pero con caché: datos locales y botón para iniciar sesión
LOGIN = "login"            # sin token y sin caché: pantalla de login


def startup_state(has_credentials: bool, has_cache: bool) -> str:
    if has_credentials:
        return CONNECT
    return OFFLINE_LOGIN if has_cache else LOGIN
