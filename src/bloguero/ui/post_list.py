from __future__ import annotations

from collections.abc import Callable

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from bloguero.i18n import _
from bloguero.models import Blog, Post

STATUS_FILTERS = ["live", "draft", "scheduled"]


def _status_label(status: str) -> str:
    # Diccionario construido en cada llamada (no a nivel de módulo) para que _()
    # se evalúe con el idioma activo, no con el que hubiera al importar el módulo.
    return {
        "live": _("Publicadas"),
        "draft": _("Borradores"),
        "scheduled": _("Programadas"),
    }[status]


class PostListView(Gtk.Box):
    """Selector de blog, filtros de estado y lista de entradas."""

    def __init__(
        self,
        on_select: Callable[[Post], None],
        on_blog_changed: Callable[[Blog], None],
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self._on_select = on_select
        self._on_blog_changed = on_blog_changed
        self._blogs: list[Blog] = []
        self._all_posts: list[Post] = []
        self._posts_by_id: dict[str, Post] = {}

        self._blog_dropdown = Gtk.DropDown(margin_top=6, margin_start=6, margin_end=6)
        self._blog_dropdown.connect("notify::selected", self._on_blog_selected)
        self.append(self._blog_dropdown)

        filter_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
            margin_start=6,
            margin_end=6,
            homogeneous=True,
        )
        self._filter_buttons: dict[str, Gtk.ToggleButton] = {}
        for status in STATUS_FILTERS:
            button = Gtk.ToggleButton(label=_status_label(status), active=True)
            button.connect("toggled", lambda _btn: self._apply_filter())
            filter_box.append(button)
            self._filter_buttons[status] = button
        self.append(filter_box)

        self._store = Gtk.ListStore(str, str, str)  # id, title, status
        self._view = Gtk.TreeView(model=self._store)
        self._view.append_column(
            Gtk.TreeViewColumn(_("Título"), Gtk.CellRendererText(), text=1)
        )
        self._view.get_selection().connect("changed", self._on_row_selected)

        scroller = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        scroller.set_child(self._view)
        self.append(scroller)

    def set_blogs(self, blogs: list[Blog]) -> None:
        self._blogs = blogs
        self._blog_dropdown.set_model(Gtk.StringList.new([b.name for b in blogs]))
        if blogs:
            self._blog_dropdown.set_selected(0)

    def set_posts(self, posts: list[Post]) -> None:
        self._all_posts = posts
        self._apply_filter()

    def _apply_filter(self) -> None:
        active = {status for status, btn in self._filter_buttons.items() if btn.get_active()}
        filtered = [p for p in self._all_posts if p.status in active]
        self._store.clear()
        self._posts_by_id = {p.id: p for p in filtered}
        for post in filtered:
            self._store.append([post.id, post.title, post.status])

    def _on_blog_selected(self, dropdown: Gtk.DropDown, _pspec) -> None:
        index = dropdown.get_selected()
        if 0 <= index < len(self._blogs):
            self._on_blog_changed(self._blogs[index])

    def _on_row_selected(self, selection: Gtk.TreeSelection) -> None:
        model, treeiter = selection.get_selected()
        if treeiter is None:
            return
        post_id = model[treeiter][0]
        post = self._posts_by_id.get(post_id)
        if post is not None:
            self._on_select(post)
