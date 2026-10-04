# Changelog

Todos los cambios relevantes de este proyecto se documentarán
en este archivo.

## [Unreleased]

## [0.1.7] - 2026-10-04

### Changed

- Ventana «Acerca de»: usa la licencia GPL-3.0 o posterior predefinida de GTK en lugar de un texto propio, la autoría incluye el correo electrónico (como enlace) y la etiqueta del enlace al proyecto es la dirección del repositorio

### Added

- Créditos de traducción (`translator-credits`) en el catálogo de inglés, que se muestran en la vista de créditos del «Acerca de»

## [0.1.6] - 2026-10-04

### Added

- Ventana «Acerca de» estándar de GNOME (versión, licencia, autoría y enlace al proyecto), accesible desde un nuevo menú hamburguesa en la cabecera que también agrupa "Preferencias"

## [0.1.5] - 2026-10-02

### Removed

- `ui/markdown_toolbar.py`: módulo sin usar por la app, mantenido solo como referencia reutilizable para otros proyectos; Telegraph Writer ya implementó su propio `build_markdown_toolbar()` con el mismo patrón, así que cumplió su propósito

## [0.1.4] - 2026-10-01

### Fixed

- Quita la clase `success` de "Guardar borrador": Mint-Y no la estiliza para botones (ni la define ninguna hoja de estilo del tema), así que no tenía ningún efecto visual; el botón se queda neutro. "Publicar"/"Programar" sigue en verde (`suggested-action`, el color de acción principal en Mint-Y) y "Borrar" en rojo

## [0.1.3] - 2026-10-01

### Changed

- Botones del editor con color según su peso: "Guardar borrador" en verde (`success`), "Publicar"/"Programar" en azul (`suggested-action`); "Nueva entrada" y "Volver a borrador" se quedan neutros, "Borrar" sigue en rojo

## [0.1.2] - 2026-10-01

### Fixed

- El panel izquierdo (lista de entradas) crecía a la mitad de la ventana al maximizarla, en vez de quedarse en su ancho mínimo; ahora el `Gtk.Paned` deja todo el espacio extra al editor

## [0.1.1] - 2026-10-01

### Fixed

- El botón "Aplicar y reiniciar" de Preferencias no volvía a mostrar ventana en el `.deb` instalado: `sys.executable` quedaba apuntando al propio lanzador (`exec -a bloguero python3 ...` renombra `argv[0]`), así que el relanzamiento ejecutaba `/usr/bin/bloguero -m bloguero.app`, que esa app no reconocía como opción propia y se cerraba sola. Ahora se relanza desde `/proc/self/exe`, inmune a ese renombrado, lanzando un proceso nuevo de verdad y cerrando el actual con `quit()`
- El interruptor de "Programar publicación" (antes una casilla `Gtk.CheckButton`) apenas se distinguía en tema oscuro (Mint-Y-Dark): se sustituye por un `Gtk.Switch`, con indicador de color siempre visible

## [0.1.0] - 2026-10-01

### Added

- Estructura inicial del proyecto: paquete `bloguero` (auth, api, models, store, convert, ui) y tests básicos
- Empaquetado `.deb` (`build-deb.sh`, `debian/`) e icono de la app
- Selector de blog y filtros de estado (Publicadas/Borradores/Programadas)
- Botón "Volver a borrador" para despublicar una entrada
- Carga instantánea desde caché al arrancar, aviso de "sin conexión" y manejo de errores de red sin crashear
- Marca `dirty` real: los cambios sin guardar se persisten localmente al instante y no se sobrescriben al refrescar en segundo plano
- Detección de conflictos: si una entrada cambió en Blogger desde otro sitio mientras la editabas, se avisa antes de guardar y se puede elegir qué versión conservar
- Programar la publicación: casilla + selector de fecha/hora en el editor; "Publicar" pasa a "Programar" y usa `publishDate` de la API
- Editor enriquecido (WYSIWYG) nativo en GTK (negrita, cursiva, subrayado, tachado, título H1/H2, listas, cita, código, enlace, color de texto), en `ui/rich_text.py` — serializa directamente a/desde el HTML que espera la API de Blogger, sin Markdown de por medio; reutilizable en otros proyectos (solo depende de `Gtk.TextView`)
- Traducción al inglés (i18n real con `gettext`): toda la interfaz pasa por `_()`, catálogo `po/en.po`, scripts `i18n-extract.sh`/`i18n-compile.sh` y compilación automática al empaquetar
- Preferencias de idioma y tema (botón de engranaje en la cabecera): selector Sistema/Español/English y Sistema/Claro/Oscuro, persistidos en `~/.config/bloguero/settings.json` y aplicados reiniciando la app (el tema deriva la variante clara/oscura del tema GTK activo preservando el acento, como en Telegraph Writer)
