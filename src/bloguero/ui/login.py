from __future__ import annotations

from typing import Callable

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from bloguero.i18n import _


class LoginView(Gtk.Box):
    """Pantalla de login: botón para conectar con Google."""

    def __init__(self, on_login: Callable[[], None]) -> None:
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
        )
        self._on_login = on_login

        label = Gtk.Label(label="Bloguero")
        label.add_css_class("title-1")
        self.append(label)

        self._error_label = Gtk.Label(label="")
        self._error_label.add_css_class("error")
        self._error_label.set_visible(False)
        self.append(self._error_label)

        button = Gtk.Button(label=_("Conectar con Google"))
        button.connect("clicked", lambda _btn: self._on_login())
        self.append(button)

    def show_error(self, message: str) -> None:
        self._error_label.set_text(message)
        self._error_label.set_visible(True)
