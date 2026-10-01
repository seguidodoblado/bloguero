# Traducciones (i18n)

El idioma fuente del código es **español**: los textos de la interfaz se
escriben directamente en español dentro del código (`_("Conectar con Google")`),
y no hace falta ningún catálogo `es.po` — si no hay traducción cargada,
`gettext` devuelve el texto tal cual.

## Añadir o cambiar un texto de la interfaz

1. Envuelve el texto en `_(...)` (importado de `bloguero.i18n`, o de
   `gettext.gettext` en los módulos de `ui/` pensados para copiarse a otros
   proyectos, como `rich_text.py`).
2. **No** metas la llamada a `_()` dentro de una f-string (`f"...{_('texto')}..."`):
   `xgettext` no la detecta ahí. Saca el texto a una variable antes:
   ```python
   # mal — xgettext no ve "Texto":
   mensaje = f"Hola {_('Texto')}"
   # bien:
   texto = _("Texto")
   mensaje = f"Hola {texto}"
   ```
3. Ejecuta `./i18n-extract.sh` desde la raíz del proyecto. Regenera
   `po/bloguero.pot` y actualiza `po/*.po` con las cadenas nuevas (quedan con
   `msgstr ""` o marcadas `#, fuzzy` si el texto original cambió).
4. Traduce las cadenas nuevas/fuzzy a mano en `po/en.po` (o el idioma que
   corresponda) y quita la marca `#, fuzzy` una vez revisadas.
5. Ejecuta `./i18n-compile.sh` para generar los `.mo` y probarlo en la app:
   ```sh
   LANGUAGE=en python -m bloguero.app
   ```

`build-deb.sh` ya llama a `i18n-compile.sh` automáticamente, así que no hace
falta compilar a mano antes de empaquetar.

## Añadir un idioma nuevo

```sh
msginit --input=po/bloguero.pot --locale=<código> --output=po/<código>.po
```

Traduce `po/<código>.po` y compílalo con `./i18n-compile.sh` — detecta
cualquier `po/*.po` automáticamente, no hace falta tocar el script.

## Dónde vive cada cosa

- `po/*.po`, `po/bloguero.pot` — fuente de las traducciones, versionado en git.
- `src/bloguero/i18n/<idioma>/LC_MESSAGES/bloguero.mo` — catálogo compilado,
  **no** se versiona (está en `.gitignore`), se genera con `i18n-compile.sh`.
- `src/bloguero/i18n/__init__.py` — `install()` (llamar una vez al arrancar la
  app) y `_()` (domain-bound, úsalo en el código específico de la app).
