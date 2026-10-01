"""Editor de texto enriquecido para Gtk.TextView, serializable a HTML.

Solo depende de Gtk/Pango: RichTextEditor es un Gtk.Box con barra de
herramientas + TextView, con get_html()/set_html() para convertir el
contenido desde/hacia el HTML que espera la API de Blogger. Pensado para
poder copiarse tal cual a otro proyecto (p. ej. telegraph-writer).
"""

from __future__ import annotations

import html as html_lib
from gettext import gettext as _
from html.parser import HTMLParser
from typing import Callable

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Pango", "1.0")
from gi.repository import Gdk, Gtk, Pango

# --- Nombres de tag "simples" (sin parámetros variables) -------------------

BOLD = "bold"
ITALIC = "italic"
UNDERLINE = "underline"
STRIKETHROUGH = "strike"
CODE = "code"
H1 = "h1"
H2 = "h2"
QUOTE = "quote"
BULLET = "bullet"
NUMBERED = "numbered"

_BLOCK_TAGS = (H1, H2, QUOTE, BULLET, NUMBERED)
_INLINE_TAGS = (BOLD, ITALIC, UNDERLINE, STRIKETHROUGH, CODE)

_LINK_COLOR = Gdk.RGBA()
_LINK_COLOR.parse("#2563eb")


def _setup_tags(buffer: Gtk.TextBuffer) -> None:
    table = buffer.get_tag_table()
    if table.lookup(BOLD) is not None:
        return  # ya configurado para este buffer

    buffer.create_tag(BOLD, weight=Pango.Weight.BOLD)
    buffer.create_tag(ITALIC, style=Pango.Style.ITALIC)
    buffer.create_tag(UNDERLINE, underline=Pango.Underline.SINGLE)
    buffer.create_tag(STRIKETHROUGH, strikethrough=True)
    buffer.create_tag(CODE, family="monospace", background_rgba=_mix_bg(buffer))
    buffer.create_tag(H1, weight=Pango.Weight.BOLD, scale=1.8, pixels_above_lines=6, pixels_below_lines=4)
    buffer.create_tag(H2, weight=Pango.Weight.BOLD, scale=1.4, pixels_above_lines=4, pixels_below_lines=3)
    buffer.create_tag(QUOTE, style=Pango.Style.ITALIC, left_margin=24, foreground="#9a9996")
    buffer.create_tag(BULLET, left_margin=24)
    buffer.create_tag(NUMBERED, left_margin=24)


def _mix_bg(buffer: Gtk.TextBuffer) -> Gdk.RGBA:
    rgba = Gdk.RGBA()
    rgba.parse("#80808040")
    return rgba


def _link_tag(buffer: Gtk.TextBuffer, url: str) -> Gtk.TextTag:
    """Crea (o reutiliza) un tag de enlace para `url`, guardando la URL en el propio tag."""
    name = f"link::{url}"
    table = buffer.get_tag_table()
    tag = table.lookup(name)
    if tag is None:
        tag = buffer.create_tag(name, foreground_rgba=_LINK_COLOR, underline=Pango.Underline.SINGLE)
        tag.href = url
    return tag


class RichTextEditor(Gtk.Box):
    """Caja con barra de formato + TextView enriquecido."""

    def __init__(self, on_changed: Callable[[], None] = lambda: None) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self._on_changed = on_changed

        self.text_view = Gtk.TextView(
            vexpand=True,
            wrap_mode=Gtk.WrapMode.WORD,
            top_margin=8,
            bottom_margin=8,
            left_margin=8,
            right_margin=8,
        )
        self.buffer = self.text_view.get_buffer()
        _setup_tags(self.buffer)
        self.buffer.connect("changed", lambda _b: self._on_changed())

        self.append(self._build_toolbar())

        scroller = Gtk.ScrolledWindow(vexpand=True)
        scroller.set_child(self.text_view)
        self.append(scroller)

    def _build_toolbar(self) -> Gtk.Widget:
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        toolbar.add_css_class("toolbar")

        simple_buttons = [
            ("format-text-bold-symbolic", _("Negrita"), lambda: self._toggle_inline(BOLD)),
            ("format-text-italic-symbolic", _("Cursiva"), lambda: self._toggle_inline(ITALIC)),
            ("format-text-underline-symbolic", _("Subrayado"), lambda: self._toggle_inline(UNDERLINE)),
            ("format-text-strikethrough-symbolic", _("Tachado"), lambda: self._toggle_inline(STRIKETHROUGH)),
        ]
        for icon_name, tooltip, action in simple_buttons:
            toolbar.append(self._make_button(icon_name, None, tooltip, action))

        toolbar.append(self._make_button(None, "H", _("Título: H1 / H2 / normal"), self._cycle_heading))
        toolbar.append(
            self._make_button(
                "view-list-bullet-symbolic", None, _("Lista con viñetas"), self._toggle_bullet_list
            )
        )
        toolbar.append(
            self._make_button(
                "view-list-ordered-symbolic", None, _("Lista numerada"), self._toggle_numbered_list
            )
        )
        toolbar.append(
            self._make_button(
                "format-indent-more-symbolic", None, _("Cita"), lambda: self._toggle_block(QUOTE)
            )
        )
        toolbar.append(self._make_button(None, "<>", _("Código"), lambda: self._toggle_inline(CODE)))
        toolbar.append(self._make_button("insert-link-symbolic", None, _("Enlace"), self._apply_link))

        toolbar.append(
            self._make_button(
                "xapp-format-text-highlight-symbolic", None, _("Color de texto"), self._pick_color
            )
        )

        return toolbar

    def _make_button(self, icon_name: str | None, label: str | None, tooltip: str, action) -> Gtk.Button:
        button = Gtk.Button(icon_name=icon_name) if icon_name else Gtk.Button(label=label)
        button.add_css_class("flat")
        button.set_tooltip_text(tooltip)
        button.connect("clicked", lambda _btn: action())
        return button

    # --- Formato ------------------------------------------------------

    def _toggle_inline(self, tag_name: str) -> None:
        bounds = self.buffer.get_selection_bounds()
        if not bounds:
            return
        start, end = bounds
        tag = self.buffer.get_tag_table().lookup(tag_name)
        if start.has_tag(tag):
            self.buffer.remove_tag(tag, start, end)
        else:
            self.buffer.apply_tag(tag, start, end)
        self.text_view.grab_focus()

    def _line_bounds(self) -> tuple[Gtk.TextIter, Gtk.TextIter]:
        bounds = self.buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
        else:
            it = self.buffer.get_iter_at_mark(self.buffer.get_insert())
            start, end = it.copy(), it.copy()
        start = self.buffer.get_iter_at_offset(start.get_offset())
        start.set_line_offset(0)
        end = self.buffer.get_iter_at_offset(end.get_offset())
        if not end.ends_line():
            end.forward_to_line_end()
        return start, end

    def _toggle_block(self, tag_name: str) -> None:
        start, end = self._line_bounds()
        table = self.buffer.get_tag_table()
        tag = table.lookup(tag_name)
        already = start.has_tag(tag)
        for other in _BLOCK_TAGS:
            self.buffer.remove_tag(table.lookup(other), start, end)
        if not already:
            self.buffer.apply_tag(tag, start, end)
        self.text_view.grab_focus()

    def _cycle_heading(self) -> None:
        start, end = self._line_bounds()
        table = self.buffer.get_tag_table()
        h1, h2 = table.lookup(H1), table.lookup(H2)
        if start.has_tag(h1):
            self.buffer.remove_tag(h1, start, end)
            self.buffer.apply_tag(h2, start, end)
        elif start.has_tag(h2):
            self.buffer.remove_tag(h2, start, end)
        else:
            self.buffer.apply_tag(h1, start, end)
        self.text_view.grab_focus()

    def _toggle_bullet_list(self) -> None:
        self._toggle_list(BULLET, marker="• ")

    def _toggle_numbered_list(self) -> None:
        self._toggle_list(NUMBERED, marker=None)

    def _toggle_list(self, tag_name: str, marker: str | None) -> None:
        start, end = self._line_bounds()
        table = self.buffer.get_tag_table()
        tag = table.lookup(tag_name)

        if start.has_tag(tag):
            # Quitar: desetiqueta y borra los marcadores de cada línea
            text = self.buffer.get_text(start, end, True)
            lines = text.split("\n")
            new_lines = [_strip_list_marker(line) for line in lines]
            start_off = start.get_offset()
            self.buffer.begin_user_action()
            self.buffer.delete(start, end)
            self.buffer.insert(self.buffer.get_iter_at_offset(start_off), "\n".join(new_lines))
            self.buffer.end_user_action()
            self.text_view.grab_focus()
            return

        text = self.buffer.get_text(start, end, True)
        lines = text.split("\n")
        new_lines = []
        for i, line in enumerate(lines):
            plain = _strip_list_marker(line)
            prefix = marker if marker else f"{i + 1}. "
            new_lines.append(f"{prefix}{plain}" if plain else line)
        new_text = "\n".join(new_lines)

        start_off = start.get_offset()
        self.buffer.begin_user_action()
        self.buffer.delete(start, end)
        self.buffer.insert(self.buffer.get_iter_at_offset(start_off), new_text)
        new_end = self.buffer.get_iter_at_offset(start_off + len(new_text))
        self.buffer.apply_tag(tag, self.buffer.get_iter_at_offset(start_off), new_end)
        self.buffer.end_user_action()
        self.text_view.grab_focus()

    def _apply_link(self) -> None:
        bounds = self.buffer.get_selection_bounds()
        if not bounds:
            return
        start_off, end_off = bounds[0].get_offset(), bounds[1].get_offset()

        box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
            margin_top=8,
            margin_bottom=8,
            margin_start=8,
            margin_end=8,
        )
        entry = Gtk.Entry(placeholder_text="https://ejemplo.com", text="https://", width_chars=28)
        box.append(entry)
        insert_btn = Gtk.Button(label=_("Insertar"))
        box.append(insert_btn)

        popover = Gtk.Popover()
        popover.set_child(box)
        popover.set_parent(self.text_view)

        def on_insert(*_args) -> None:
            url = entry.get_text().strip()
            popover.popdown()
            if not url:
                return
            tag = _link_tag(self.buffer, url)
            self.buffer.apply_tag(
                tag, self.buffer.get_iter_at_offset(start_off), self.buffer.get_iter_at_offset(end_off)
            )
            self.text_view.grab_focus()

        insert_btn.connect("clicked", on_insert)
        entry.connect("activate", on_insert)
        popover.connect("closed", lambda _p: popover.unparent())

        popover.popup()
        entry.grab_focus()
        entry.select_region(8, -1)  # selecciona tras "https://" para escribir directamente

    def _pick_color(self) -> None:
        bounds = self.buffer.get_selection_bounds()
        if not bounds:
            return
        start_off, end_off = bounds[0].get_offset(), bounds[1].get_offset()
        dialog = Gtk.ColorDialog(with_alpha=False)
        dialog.choose_rgba(self.get_root(), None, None, self._on_color_chosen, start_off, end_off)

    def _on_color_chosen(self, dialog: Gtk.ColorDialog, result, start_off: int, end_off: int) -> None:
        try:
            rgba = dialog.choose_rgba_finish(result)
        except Exception:
            return
        tag = self.buffer.create_tag(None, foreground_rgba=rgba)
        self.buffer.apply_tag(
            tag, self.buffer.get_iter_at_offset(start_off), self.buffer.get_iter_at_offset(end_off)
        )
        self.text_view.grab_focus()

    # --- Contenido ------------------------------------------------------

    def get_html(self) -> str:
        return buffer_to_html(self.buffer)

    def set_html(self, html: str) -> None:
        html_to_buffer(self.buffer, html)

    def clear(self) -> None:
        self.buffer.set_text("")


def _strip_list_marker(line: str) -> str:
    if line.startswith("• "):
        return line[2:]
    stripped = line.lstrip("0123456789")
    if stripped.startswith(". ") and stripped != line:
        return stripped[2:]
    return line


# --- Serialización TextBuffer -> HTML --------------------------------------


def buffer_to_html(buffer: Gtk.TextBuffer) -> str:
    start, end = buffer.get_bounds()
    full_text = buffer.get_text(start, end, True)
    lines = full_text.split("\n")

    blocks: list[str] = []
    line_offset = 0
    open_list: str | None = None  # "ul" | "ol" | None

    table = buffer.get_tag_table()
    h1, h2, quote, bullet, numbered = (table.lookup(n) for n in (H1, H2, QUOTE, BULLET, NUMBERED))

    for line in lines:
        line_start = buffer.get_iter_at_offset(line_offset)
        line_end = buffer.get_iter_at_offset(line_offset + len(line))
        line_offset += len(line) + 1

        if not line.strip():
            if open_list:
                blocks.append(f"</{open_list}>")
                open_list = None
            continue

        inline_html = _inline_runs_to_html(buffer, line_start, line_end)

        if line_start.has_tag(h1):
            if open_list:
                blocks.append(f"</{open_list}>")
                open_list = None
            blocks.append(f"<h1>{inline_html}</h1>")
        elif line_start.has_tag(h2):
            if open_list:
                blocks.append(f"</{open_list}>")
                open_list = None
            blocks.append(f"<h2>{inline_html}</h2>")
        elif line_start.has_tag(quote):
            if open_list:
                blocks.append(f"</{open_list}>")
                open_list = None
            blocks.append(f"<blockquote>{inline_html}</blockquote>")
        elif line_start.has_tag(bullet):
            if open_list != "ul":
                if open_list:
                    blocks.append(f"</{open_list}>")
                blocks.append("<ul>")
                open_list = "ul"
            item_html = _inline_runs_to_html(buffer, line_start, line_end, skip_prefix="• ")
            blocks.append(f"<li>{item_html}</li>")
        elif line_start.has_tag(numbered):
            if open_list != "ol":
                if open_list:
                    blocks.append(f"</{open_list}>")
                blocks.append("<ol>")
                open_list = "ol"
            item_html = _inline_runs_to_html(buffer, line_start, line_end, strip_numbered=True)
            blocks.append(f"<li>{item_html}</li>")
        else:
            if open_list:
                blocks.append(f"</{open_list}>")
                open_list = None
            blocks.append(f"<p>{inline_html}</p>")

    if open_list:
        blocks.append(f"</{open_list}>")

    return "\n".join(blocks)


def _inline_runs_to_html(
    buffer: Gtk.TextBuffer,
    start: Gtk.TextIter,
    end: Gtk.TextIter,
    skip_prefix: str | None = None,
    strip_numbered: bool = False,
) -> str:
    it = start.copy()
    pieces: list[str] = []
    skip_chars = len(skip_prefix) if skip_prefix else 0

    while it.compare(end) < 0:
        run_end = it.copy()
        run_end.forward_to_tag_toggle(None)
        if run_end.compare(end) > 0:
            run_end = end.copy()

        text = buffer.get_text(it, run_end, True)

        if skip_chars:
            take = min(skip_chars, len(text))
            text = text[take:]
            skip_chars -= take
        if strip_numbered and text:
            stripped = text.lstrip("0123456789")
            if stripped.startswith(". ") and stripped != text:
                text = stripped[2:]
                strip_numbered = False

        if text:
            pieces.append(_wrap_inline(text, it.get_tags()))

        it = run_end

    return "".join(pieces)


def _wrap_inline(text: str, tags: list[Gtk.TextTag]) -> str:
    escaped = html_lib.escape(text)
    href = None
    color = None
    bold = italic = underline = strike = code = False

    for tag in tags:
        name = tag.get_property("name")
        if hasattr(tag, "href"):
            href = tag.href
        elif name == BOLD:
            bold = True
        elif name == ITALIC:
            italic = True
        elif name == UNDERLINE:
            underline = True
        elif name == STRIKETHROUGH:
            strike = True
        elif name == CODE:
            code = True
        elif name is None:
            rgba = tag.get_property("foreground-rgba")
            if rgba is not None:
                color = "#{:02x}{:02x}{:02x}".format(
                    round(rgba.red * 255), round(rgba.green * 255), round(rgba.blue * 255)
                )

    result = escaped
    if code:
        result = f"<code>{result}</code>"
    if strike:
        result = f"<s>{result}</s>"
    if underline:
        result = f"<u>{result}</u>"
    if italic:
        result = f"<em>{result}</em>"
    if bold:
        result = f"<strong>{result}</strong>"
    if color:
        result = f'<span style="color:{color}">{result}</span>'
    if href:
        result = f'<a href="{html_lib.escape(href, quote=True)}">{result}</a>'
    return result


# --- Parseo HTML -> TextBuffer ----------------------------------------------


class _HTMLToBuffer(HTMLParser):
    def __init__(self, buffer: Gtk.TextBuffer) -> None:
        super().__init__(convert_charrefs=True)
        self.buffer = buffer
        self.table = buffer.get_tag_table()
        self._inline_stack: list[str] = []
        self._href_stack: list[str] = []
        self._color_stack: list[str | None] = []
        self._block: str | None = None
        self._list_kind: str | None = None  # "ul" | "ol"
        self._list_index = 0
        self._pending_newline = False

    def _insert(self, text: str) -> None:
        if not text:
            return
        if self._pending_newline:
            self.buffer.insert(self.buffer.get_end_iter(), "\n")
            self._pending_newline = False

        tag_names = list(self._inline_stack)
        start_offset = self.buffer.get_end_iter().get_offset()
        self.buffer.insert(self.buffer.get_end_iter(), text)
        start_it = self.buffer.get_iter_at_offset(start_offset)
        end_it = self.buffer.get_end_iter()

        for name in tag_names:
            tag = self.table.lookup(name)
            if tag:
                self.buffer.apply_tag(tag, start_it, end_it)
        if self._href_stack:
            tag = _link_tag(self.buffer, self._href_stack[-1])
            self.buffer.apply_tag(tag, start_it, end_it)
        active_color = next((c for c in reversed(self._color_stack) if c), None)
        if active_color:
            rgba = Gdk.RGBA()
            if rgba.parse(active_color):
                color_tag = self.buffer.create_tag(None, foreground_rgba=rgba)
                self.buffer.apply_tag(color_tag, start_it, end_it)
        if self._block in (H1, H2, QUOTE, BULLET, NUMBERED):
            tag = self.table.lookup(self._block)
            self.buffer.apply_tag(tag, start_it, end_it)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("strong", "b"):
            self._inline_stack.append(BOLD)
        elif tag in ("em", "i"):
            self._inline_stack.append(ITALIC)
        elif tag == "u":
            self._inline_stack.append(UNDERLINE)
        elif tag in ("s", "strike", "del"):
            self._inline_stack.append(STRIKETHROUGH)
        elif tag == "code":
            self._inline_stack.append(CODE)
        elif tag == "a":
            href = dict(attrs).get("href", "")
            self._href_stack.append(href or "")
        elif tag == "span":
            style = dict(attrs).get("style", "") or ""
            color = None
            for part in style.split(";"):
                key, _, value = part.strip().partition(":")
                if key.strip() == "color":
                    color = value.strip()
            self._color_stack.append(color)
        elif tag == "h1":
            self._start_block(H1)
        elif tag == "h2":
            self._start_block(H2)
        elif tag == "blockquote":
            self._start_block(QUOTE)
        elif tag == "ul":
            self._list_kind = "ul"
        elif tag == "ol":
            self._list_kind = "ol"
            self._list_index = 0
        elif tag == "li":
            if self._list_kind == "ol":
                self._list_index += 1
                self._start_block(NUMBERED)
                self._insert(f"{self._list_index}. ")
            else:
                self._start_block(BULLET)
                self._insert("• ")
        elif tag == "p":
            self._start_block(None)
        elif tag == "br":
            self._pending_newline = True

    def _start_block(self, block: str | None) -> None:
        if self.buffer.get_end_iter().get_offset() > 0:
            self._pending_newline = True
        self._block = block

    def handle_endtag(self, tag: str) -> None:
        if tag in ("strong", "b") and BOLD in self._inline_stack:
            self._inline_stack.remove(BOLD)
        elif tag in ("em", "i") and ITALIC in self._inline_stack:
            self._inline_stack.remove(ITALIC)
        elif tag == "u" and UNDERLINE in self._inline_stack:
            self._inline_stack.remove(UNDERLINE)
        elif tag in ("s", "strike", "del") and STRIKETHROUGH in self._inline_stack:
            self._inline_stack.remove(STRIKETHROUGH)
        elif tag == "code" and CODE in self._inline_stack:
            self._inline_stack.remove(CODE)
        elif tag == "a" and self._href_stack:
            self._href_stack.pop()
        elif tag == "span" and self._color_stack:
            self._color_stack.pop()
        elif tag in ("ul", "ol"):
            self._list_kind = None
        elif tag in ("h1", "h2", "blockquote", "li", "p"):
            self._block = None

    def handle_data(self, data: str) -> None:
        if data.strip() == "" and "\n" in data:
            return  # sangría/formato entre etiquetas, no contenido real
        self._insert(data)


def html_to_buffer(buffer: Gtk.TextBuffer, html: str) -> None:
    _setup_tags(buffer)
    buffer.set_text("")
    parser = _HTMLToBuffer(buffer)
    parser.feed(html)
