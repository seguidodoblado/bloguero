from __future__ import annotations

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

from bloguero import i18n
from bloguero.ui.window import MainWindow

APPLICATION_ID = "dev.seguidodoblado.Bloguero"

# Con "python3 -m" argv[0] es la ruta de __main__.py y GTK derivaría de ahí el WM_CLASS;
# se fija para que coincida con StartupWMClass del .desktop y el panel muestre el icono.
GLib.set_prgname("bloguero")


class BlogueroApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id=APPLICATION_ID)

    def do_activate(self) -> None:
        window = self.props.active_window
        if window is None:
            window = MainWindow(self)
        window.present()


def main() -> int:
    i18n.install()
    app = BlogueroApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
