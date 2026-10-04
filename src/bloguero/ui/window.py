from __future__ import annotations

import threading

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GLib, Gtk

from bloguero import __version__, session
from bloguero.api import BloggerClient
from bloguero.convert import html_to_markdown
from bloguero.i18n import _
from bloguero.models import Blog, Post
from bloguero.store import Store
from bloguero.ui.editor import EditorView
from bloguero.ui.login import LoginView
from bloguero.ui.post_list import PostListView


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application, title="Bloguero", default_width=900, default_height=600)

        header = Gtk.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Bloguero"))
        header.pack_end(self._build_menu_button())
        self.set_titlebar(header)

        self._store = Store()
        self._client: BloggerClient | None = None
        self._blogs: list[Blog] = []
        self._current_blog: Blog | None = None
        self._current_post: Post | None = None

        self._stack = Gtk.Stack()
        self.set_child(self._stack)

        self._login_view = LoginView(on_login=self._login)
        self._stack.add_named(self._login_view, "login")

        self._loading_view = self._build_loading_view()
        self._stack.add_named(self._loading_view, "loading")

        self._main_view = self._build_main_view()
        self._stack.add_named(self._main_view, "main")

        self._load_from_cache()

        from bloguero import auth

        state = session.startup_state(auth.has_stored_credentials(), bool(self._blogs))
        if state == session.CONNECT:
            if self._blogs:
                self._stack.set_visible_child_name("main")
            else:
                self._stack.set_visible_child_name("loading")
            self._login()
        elif state == session.OFFLINE_LOGIN:
            self._stack.set_visible_child_name("main")
            self._set_offline(
                True, _("No has iniciado sesión: mostrando datos guardados localmente."), can_login=True
            )
        else:
            self._stack.set_visible_child_name("login")

    def _build_menu_button(self) -> Gtk.Widget:
        # Menú de la cabecera: botones con icono del sistema (simbólico, con el normal como
        # alternativa si el tema no lo tiene) y etiqueta, como en Telegraph Writer y
        # Joseflix Request.
        popover = Gtk.Popover()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_margin_start(6)
        box.set_margin_end(6)
        box.set_margin_top(6)
        box.set_margin_bottom(6)

        entries = (
            (
                _("Preferencias"),
                ("preferences-system-symbolic", "preferences-system"),
                self._open_preferences,
            ),
            (
                _("Acerca de Bloguero"),
                ("help-about-symbolic", "help-about"),
                self._open_about,
            ),
        )
        for label, icon_names, callback in entries:
            item = Gtk.Button()
            content = Gtk.Box(spacing=8)
            icon = Gio.ThemedIcon.new_from_names(list(icon_names))
            content.append(Gtk.Image.new_from_gicon(icon))
            content.append(Gtk.Label(label=label, xalign=0))
            item.set_child(content)
            item.set_halign(Gtk.Align.FILL)
            item.connect("clicked", lambda _btn, fn=callback: (popover.popdown(), fn()))
            box.append(item)
        popover.set_child(box)

        menu_button = Gtk.MenuButton(
            icon_name="open-menu-symbolic", tooltip_text=_("Menú principal")
        )
        menu_button.set_popover(popover)
        return menu_button

    def _open_preferences(self) -> None:
        from bloguero.ui.preferences import PreferencesWindow

        PreferencesWindow(self.get_application()).present()

    def _open_about(self) -> None:
        about = Gtk.AboutDialog(
            transient_for=self,
            modal=True,
            program_name="Bloguero",
            version=__version__,
            logo_icon_name="bloguero",
            comments=_("Cliente de escritorio para Blogger"),
            website="https://github.com/seguidodoblado/bloguero",
            website_label=_("github.com/seguidodoblado/bloguero"),
            authors=["José Antonio Seguido Doblado <jose.antonio.seguido@gmail.com>"],
            copyright="© 2026 José Antonio Seguido Doblado",
            license_type=Gtk.License.GPL_3_0,
            translator_credits=_("translator-credits"),
        )
        about.present()

    def _build_loading_view(self) -> Gtk.Widget:
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
        )
        spinner = Gtk.Spinner(spinning=True, width_request=32, height_request=32)
        box.append(spinner)
        return box

    def _build_main_view(self) -> Gtk.Widget:
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self._offline_bar = Gtk.Box(spacing=12, margin_top=6, margin_bottom=6, margin_start=12, margin_end=12)
        self._offline_banner = Gtk.Label(xalign=0, hexpand=True)
        self._offline_banner.add_css_class("warning")
        self._connect_button = Gtk.Button(label=_("Conectar con Google"))
        self._connect_button.connect("clicked", self._on_connect_clicked)
        self._offline_bar.append(self._offline_banner)
        self._offline_bar.append(self._connect_button)
        self._offline_bar.set_visible(False)
        container.append(self._offline_bar)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL, vexpand=True)

        self._post_list = PostListView(on_select=self._open_post, on_blog_changed=self._on_blog_changed)
        paned.set_start_child(self._post_list)

        self._editor = EditorView(
            on_new=self._new_post,
            on_save_draft=self._save_draft,
            on_publish=self._publish,
            on_revert=self._revert_to_draft,
            on_delete=self._delete_post,
            on_dirty=self._on_editor_dirty,
        )
        paned.set_end_child(self._editor)
        # El panel izquierdo se queda en su ancho fijo (position) al redimensionar la
        # ventana (p. ej. al maximizar); todo el espacio extra va al editor.
        paned.set_resize_start_child(False)
        paned.set_resize_end_child(True)
        paned.set_shrink_start_child(False)
        paned.set_position(280)

        container.append(paned)
        return container

    def _set_offline(self, offline: bool, message: str = "", can_login: bool = False) -> None:
        if offline:
            self._offline_banner.set_text(
                message or _("Sin conexión: mostrando datos guardados localmente.")
            )
        # El botón solo aparece cuando falta la sesión (no cuando solo falla la red)
        self._connect_button.set_visible(offline and can_login)
        self._connect_button.set_sensitive(True)
        self._offline_bar.set_visible(offline)

    def _on_connect_clicked(self, _button: Gtk.Button) -> None:
        self._connect_button.set_sensitive(False)
        self._login()

    def _show_message(self, title: str, detail: str) -> None:
        dialog = Gtk.AlertDialog()
        dialog.set_message(title)
        dialog.set_detail(detail)
        dialog.show(self)

    def _load_from_cache(self) -> None:
        blogs = self._store.list_blogs()
        if not blogs:
            return
        self._blogs = blogs
        self._current_blog = blogs[0]
        self._post_list.set_blogs(blogs)
        self._post_list.set_posts(self._store.list_posts(blogs[0].id))

    def _login(self) -> None:
        threading.Thread(target=self._login_worker, daemon=True).start()

    def _login_worker(self) -> None:
        from bloguero import auth

        try:
            credentials = auth.get_credentials()
            client = BloggerClient(credentials)
            blogs = client.list_my_blogs()
            posts = client.list_posts(blogs[0].id) if blogs else []
        except auth.AuthError as exc:
            GLib.idle_add(self._on_login_error, str(exc))
            return
        except Exception:  # noqa: BLE001 - un fallo de red o de la API se muestra al usuario, no debe cerrar la app
            GLib.idle_add(self._on_login_offline)
            return

        GLib.idle_add(self._on_login_success, client, blogs, posts)

    def _on_login_error(self, message: str) -> bool:
        self._connect_button.set_sensitive(True)
        self._login_view.show_error(message)
        self._stack.set_visible_child_name("login")
        return False

    def _on_login_offline(self) -> bool:
        from bloguero import auth

        if self._blogs:
            # Sin token guardado el botón de conectar se mantiene, para reintentarlo
            self._set_offline(True, can_login=not auth.has_stored_credentials())
            self._stack.set_visible_child_name("main")
        else:
            self._login_view.show_error(_("Sin conexión y sin datos locales guardados."))
            self._stack.set_visible_child_name("login")
        return False

    def _on_login_success(self, client: BloggerClient, blogs: list[Blog], posts: list[Post]) -> bool:
        self._client = client
        self._blogs = blogs
        self._store.save_blogs(blogs)
        if blogs:
            self._current_blog = blogs[0]
            self._apply_fetched_posts(posts)
        self._post_list.set_blogs(blogs)
        self._set_offline(False)
        self._stack.set_visible_child_name("main")
        return False

    def _on_blog_changed(self, blog: Blog) -> None:
        if self._current_blog and blog.id == self._current_blog.id:
            return
        self._current_blog = blog
        self._current_post = None
        self._editor.clear()
        self._post_list.set_posts(self._store.list_posts(blog.id))
        if not self._client:
            return
        threading.Thread(target=self._refresh_posts_worker, daemon=True).start()

    def _refresh_posts_worker(self) -> None:
        if not self._current_blog or not self._client:
            return
        try:
            posts = self._client.list_posts(self._current_blog.id)
        except Exception:  # noqa: BLE001 - un fallo de red o de la API se muestra al usuario, no debe cerrar la app
            GLib.idle_add(self._set_offline, True, "")
            return
        GLib.idle_add(self._apply_fetched_posts, posts)

    def _apply_fetched_posts(self, posts: list[Post]) -> None:
        self._set_offline(False)
        for post in posts:
            cached = self._store.get_post(post.id)
            if cached and cached.dirty:
                # Hay cambios locales sin guardar: no se pisan con lo que diga el servidor.
                post.title = cached.title
                post.labels = cached.labels
                post.html = cached.html
                post.dirty = True
            self._store.save_post(post)
        self._post_list.set_posts(posts)

    def _refresh_posts(self) -> None:
        if not self._current_blog or not self._client:
            return
        try:
            posts = self._client.list_posts(self._current_blog.id)
        except Exception:  # noqa: BLE001 - un fallo de red o de la API se muestra al usuario, no debe cerrar la app
            self._set_offline(True)
            return
        self._apply_fetched_posts(posts)

    def _open_post(self, post: Post) -> None:
        self._current_post = post
        self._editor.load_post(post)

    def _new_post(self) -> None:
        self._current_post = None
        self._editor.clear()

    def _on_editor_dirty(self) -> None:
        if not self._current_post:
            return
        self._store.mark_dirty(
            self._current_post.id,
            title=self._editor.title(),
            html=self._editor.body_html(),
            labels=self._editor.labels(),
        )

    def _save_draft(self) -> Post | None:
        if not self._client or not self._current_blog:
            self._show_message(
                _("Sin conexión"),
                _(
                    "No se puede guardar en Blogger ahora mismo. "
                    "Tus cambios siguen a salvo en este equipo; vuelve a intentarlo cuando tengas conexión."
                ),
            )
            return None

        title = self._editor.title()
        html = self._editor.body_html()
        labels = self._editor.labels()

        if self._current_post is not None and self._has_remote_conflict(self._current_post):
            return None

        return self._do_save(title, html, labels)

    def _has_remote_conflict(self, local_post: Post) -> bool:
        try:
            server_post = self._client.get_post(self._current_blog.id, local_post.id)
        except Exception:  # noqa: BLE001 - un fallo de red o de la API se muestra al usuario, no debe cerrar la app
            return False

        if not local_post.updated or not server_post.updated:
            return False
        if server_post.updated == local_post.updated:
            return False

        self._show_conflict_dialog(server_post)
        return True

    def _show_conflict_dialog(self, server_post: Post) -> None:
        # Se convierte a Markdown solo para que el diff sea legible en el diálogo.
        server_preview = html_to_markdown(server_post.html)
        local_preview = html_to_markdown(self._editor.body_html())
        intro = _("Se editó en otro sitio después de que la abrieras aquí.")
        mine_label = _("Tu versión")
        server_label = _("Versión en Blogger")

        dialog = Gtk.AlertDialog()
        dialog.set_message(_("Esta entrada cambió en Blogger"))
        dialog.set_detail(
            f"{intro}\n\n— {mine_label} —\n{local_preview[:300]}\n\n"
            f"— {server_label} —\n{server_preview[:300]}"
        )
        dialog.set_buttons([_("Cancelar"), _("Usar la de Blogger"), _("Mantener la mía")])
        dialog.set_cancel_button(0)
        dialog.set_default_button(0)
        dialog.choose(self, None, self._on_conflict_resolved, server_post)

    def _on_conflict_resolved(self, dialog: Gtk.AlertDialog, result, server_post: Post) -> None:
        try:
            choice = dialog.choose_finish(result)
        except Exception:  # noqa: BLE001 - un fallo de red o de la API se muestra al usuario, no debe cerrar la app
            return

        if choice == 1:
            server_post.dirty = False
            self._current_post = server_post
            self._store.save_post(server_post)
            self._editor.load_post(server_post)
        elif choice == 2:
            self._do_save(self._editor.title(), self._editor.body_html(), self._editor.labels())

    def _do_save(self, title: str, html: str, labels: list[str]) -> Post | None:
        try:
            if self._current_post is None:
                post = self._client.create_post(
                    self._current_blog.id, title, html, is_draft=True, labels=labels
                )
            else:
                post = self._client.update_post(
                    self._current_blog.id, self._current_post.id, title, html, labels=labels
                )
        except Exception as exc:  # noqa: BLE001 - un fallo de red o de la API se muestra al usuario, no debe cerrar la app
            self._show_message(_("No se pudo guardar"), str(exc))
            return None

        self._current_post = post
        self._store.save_post(post)
        self._refresh_posts()
        return post

    def _publish(self) -> None:
        scheduled_at = self._editor.scheduled_at()
        post = self._save_draft()
        if not post or not self._client or not self._current_blog:
            return

        try:
            published = self._client.publish_post(
                self._current_blog.id, post.id, publish_date=scheduled_at
            )
        except Exception as exc:  # noqa: BLE001 - un fallo de red o de la API se muestra al usuario, no debe cerrar la app
            self._show_message(_("No se pudo publicar"), str(exc))
            return

        published.html = post.html
        self._current_post = published
        self._store.save_post(published)
        self._editor.load_post(published)
        self._refresh_posts()

    def _revert_to_draft(self) -> None:
        if not self._client or not self._current_blog or not self._current_post:
            return

        try:
            reverted = self._client.revert_post(self._current_blog.id, self._current_post.id)
        except Exception as exc:  # noqa: BLE001 - un fallo de red o de la API se muestra al usuario, no debe cerrar la app
            self._show_message(_("No se pudo volver a borrador"), str(exc))
            return

        reverted.html = self._current_post.html
        self._current_post = reverted
        self._store.save_post(reverted)
        self._editor.load_post(reverted)
        self._refresh_posts()

    def _delete_post(self) -> None:
        if not self._current_post:
            return

        dialog = Gtk.AlertDialog()
        dialog.set_message(_("Borrar entrada"))
        dialog.set_detail(
            _("¿Seguro que quieres borrar «{title}»? Esta acción no se puede deshacer.").format(
                title=self._current_post.title
            )
        )
        dialog.set_buttons([_("Cancelar"), _("Borrar")])
        dialog.set_cancel_button(0)
        dialog.set_default_button(0)
        dialog.choose(self, None, self._on_delete_confirmed)

    def _on_delete_confirmed(self, dialog: Gtk.AlertDialog, result) -> None:
        try:
            choice = dialog.choose_finish(result)
        except Exception:  # noqa: BLE001 - un fallo de red o de la API se muestra al usuario, no debe cerrar la app
            return
        if choice != 1 or not self._client or not self._current_blog or not self._current_post:
            return

        try:
            self._client.delete_post(self._current_blog.id, self._current_post.id)
        except Exception as exc:  # noqa: BLE001 - un fallo de red o de la API se muestra al usuario, no debe cerrar la app
            self._show_message(_("No se pudo borrar"), str(exc))
            return

        self._store.delete_post(self._current_post.id)
        self._current_post = None
        self._editor.clear()
        self._refresh_posts()
