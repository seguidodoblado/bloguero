from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

from bloguero.i18n import _
from bloguero.models import Post
from bloguero.ui.rich_text import RichTextEditor

_ICON_PATH = Path(__file__).resolve().parent.parent / "assets" / "bloguero.svg"


class EditorView(Gtk.Box):
    """Editor de una entrada: título, etiquetas, cuerpo enriquecido."""

    def __init__(
        self,
        on_new: Callable[[], None],
        on_save_draft: Callable[[], None],
        on_publish: Callable[[], None],
        on_revert: Callable[[], None],
        on_delete: Callable[[], None],
        on_dirty: Callable[[], None] = lambda: None,
    ) -> None:
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_top=12,
            margin_bottom=12,
            margin_start=12,
            margin_end=12,
        )

        self._has_post = False
        self._status: str | None = None
        self._loading = False
        self._on_dirty = on_dirty

        title_heading = Gtk.Label(label=_("Título"), xalign=0)
        title_heading.add_css_class("heading")
        self.append(title_heading)

        self._title_entry = Gtk.Entry(placeholder_text=_("Título de la entrada"))
        self._title_entry.connect("changed", lambda _entry: self._notify_dirty())
        self.append(self._title_entry)

        self._labels_entry = Gtk.Entry(placeholder_text=_("Etiquetas (separadas por comas)"))
        self._labels_entry.connect("changed", lambda _entry: self._notify_dirty())
        self.append(self._labels_entry)

        self.append(self._build_schedule_box())

        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        body_heading = Gtk.Label(label=_("Cuerpo"), xalign=0)
        body_heading.add_css_class("heading")
        self.append(body_heading)

        self._rich_editor = RichTextEditor(on_changed=self._on_body_changed)

        overlay = Gtk.Overlay(vexpand=True)
        overlay.set_child(self._rich_editor)
        overlay.add_overlay(self._build_placeholder())

        body_frame = Gtk.Frame(vexpand=True)
        body_frame.set_child(overlay)
        self.append(body_frame)

        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        actions = Gtk.FlowBox(
            selection_mode=Gtk.SelectionMode.NONE,
            row_spacing=6,
            column_spacing=6,
            homogeneous=False,
            max_children_per_line=99,
        )
        new_btn = Gtk.Button(label=_("Nueva entrada"))
        new_btn.connect("clicked", lambda _btn: on_new())
        save_btn = Gtk.Button(label=_("Guardar borrador"))
        save_btn.connect("clicked", lambda _btn: on_save_draft())
        self._publish_btn = Gtk.Button(label=_("Publicar"))
        self._publish_btn.add_css_class("suggested-action")
        self._publish_btn.connect("clicked", lambda _btn: on_publish())
        self._revert_btn = Gtk.Button(label=_("Volver a borrador"))
        self._revert_btn.connect("clicked", lambda _btn: on_revert())
        self._revert_btn.set_visible(False)
        delete_btn = Gtk.Button(label=_("Borrar"))
        delete_btn.add_css_class("destructive-action")
        delete_btn.connect("clicked", lambda _btn: on_delete())
        for btn in (new_btn, save_btn, self._publish_btn, self._revert_btn, delete_btn):
            actions.append(btn)
        self.append(actions)

        self._update_placeholder()
        self._update_status_buttons()

    def _build_schedule_box(self) -> Gtk.Widget:
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # Switch en vez de CheckButton: el indicador de color siempre visible no
        # depende del contraste del borde del tema (en Mint-Y-Dark el del check
        # queda casi invisible).
        self._schedule_check = Gtk.Switch(valign=Gtk.Align.CENTER)
        self._schedule_check.connect("notify::active", self._on_schedule_toggled)
        box.append(self._schedule_check)
        box.append(Gtk.Label(label=_("Programar publicación")))

        self._schedule_button = Gtk.MenuButton(sensitive=False)
        popover = Gtk.Popover()
        popover_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10,
        )

        self._calendar = Gtk.Calendar()
        self._calendar.connect("day-selected", lambda _c: self._update_schedule_label())
        popover_box.append(self._calendar)

        time_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        time_row.append(Gtk.Label(label=_("Hora:")))
        self._hour_spin = Gtk.SpinButton.new_with_range(0, 23, 1)
        self._hour_spin.set_value(9)
        self._hour_spin.connect("value-changed", lambda _s: self._update_schedule_label())
        time_row.append(self._hour_spin)
        time_row.append(Gtk.Label(label=":"))
        self._minute_spin = Gtk.SpinButton.new_with_range(0, 59, 1)
        self._minute_spin.connect("value-changed", lambda _s: self._update_schedule_label())
        time_row.append(self._minute_spin)
        popover_box.append(time_row)

        popover.set_child(popover_box)
        self._schedule_button.set_popover(popover)
        box.append(self._schedule_button)

        self._update_schedule_label()
        return box

    def _on_schedule_toggled(self, _switch: Gtk.Switch, _pspec) -> None:
        active = self._schedule_check.get_active()
        self._schedule_button.set_sensitive(active)
        self._publish_btn.set_label(_("Programar") if active else _("Publicar"))

    def _update_schedule_label(self) -> None:
        date = self._calendar.get_date()
        self._schedule_button.set_label(
            f"{date.get_day_of_month():02d}/{date.get_month():02d}/{date.get_year()} "
            f"{self._hour_spin.get_value_as_int():02d}:{self._minute_spin.get_value_as_int():02d}"
        )

    def _set_schedule(self, when: datetime | None) -> None:
        if when:
            self._schedule_check.set_active(True)
            self._calendar.select_day(GLib.DateTime.new_local(when.year, when.month, when.day, 0, 0, 0))
            self._hour_spin.set_value(when.hour)
            self._minute_spin.set_value(when.minute)
        else:
            self._schedule_check.set_active(False)
        self._schedule_button.set_sensitive(self._schedule_check.get_active())
        self._update_schedule_label()

    def scheduled_at(self) -> datetime | None:
        if not self._schedule_check.get_active():
            return None
        date = self._calendar.get_date()
        naive = datetime(
            date.get_year(),
            date.get_month(),
            date.get_day_of_month(),
            self._hour_spin.get_value_as_int(),
            self._minute_spin.get_value_as_int(),
        )
        return naive.astimezone()

    def _build_placeholder(self) -> Gtk.Widget:
        placeholder = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            hexpand=True,
            vexpand=True,
        )
        placeholder.set_can_target(False)
        placeholder.set_opacity(0.5)

        picture = Gtk.Picture.new_for_filename(str(_ICON_PATH))
        picture.set_content_fit(Gtk.ContentFit.CONTAIN)
        picture.set_size_request(64, 64)
        picture.set_halign(Gtk.Align.CENTER)
        picture.set_valign(Gtk.Align.CENTER)
        picture.set_can_shrink(True)
        placeholder.append(picture)

        hint = Gtk.Label(
            label=_("Selecciona una entrada de la lista\no pulsa «Nueva entrada» para escribir una"),
            justify=Gtk.Justification.CENTER,
        )
        placeholder.append(hint)

        self._placeholder = placeholder
        return placeholder

    def _update_placeholder(self) -> None:
        is_empty = self._rich_editor.buffer.get_char_count() == 0
        self._placeholder.set_visible(not self._has_post and is_empty)

    def _update_status_buttons(self) -> None:
        can_revert = self._status in ("live", "scheduled")
        self._publish_btn.set_visible(not can_revert)
        self._revert_btn.set_visible(can_revert)

    def _on_body_changed(self) -> None:
        self._update_placeholder()
        self._notify_dirty()

    def _notify_dirty(self) -> None:
        if self._loading or not self._has_post:
            return
        self._on_dirty()

    def load_post(self, post: Post) -> None:
        self._loading = True
        self._has_post = True
        self._status = post.status
        self._title_entry.set_text(post.title)
        self._labels_entry.set_text(",".join(post.labels))
        self._rich_editor.set_html(post.html)
        self._set_schedule(post.published if post.status == "scheduled" else None)
        self._update_placeholder()
        self._update_status_buttons()
        self._loading = False

    def clear(self) -> None:
        self._loading = True
        self._has_post = False
        self._status = None
        self._title_entry.set_text("")
        self._labels_entry.set_text("")
        self._rich_editor.clear()
        self._set_schedule(None)
        self._update_placeholder()
        self._update_status_buttons()
        self._loading = False

    def title(self) -> str:
        return self._title_entry.get_text()

    def labels(self) -> list[str]:
        return [l.strip() for l in self._labels_entry.get_text().split(",") if l.strip()]

    def body_html(self) -> str:
        return self._rich_editor.get_html()
