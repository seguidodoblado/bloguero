# Changelog

Todos los cambios relevantes de este proyecto se documentarán
en este archivo.

## [Unreleased]

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

### Changed

- 

### Fixed

- 
