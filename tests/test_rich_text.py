import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from bloguero.ui.rich_text import _setup_tags, buffer_to_html, html_to_buffer


def _roundtrip(html: str) -> str:
    buffer = Gtk.TextBuffer()
    _setup_tags(buffer)
    html_to_buffer(buffer, html)
    return buffer_to_html(buffer)


def test_bold_and_italic():
    assert _roundtrip("<p>Hola <strong>mundo</strong> y <em>cursiva</em></p>") == (
        "<p>Hola <strong>mundo</strong> y <em>cursiva</em></p>"
    )


def test_heading_and_quote():
    html = "<h1>Título</h1>\n<blockquote>cita</blockquote>"
    assert _roundtrip(html) == html


def test_lists():
    html = "<ul>\n<li>uno</li>\n<li>dos</li>\n</ul>\n<ol>\n<li>a</li>\n<li>b</li>\n</ol>"
    assert _roundtrip(html) == html


def test_link():
    html = '<p>Visita <a href="https://example.com">este sitio</a> ya</p>'
    assert _roundtrip(html) == html


def test_underline_strike_code():
    html = "<p><u>subrayado</u> <s>tachado</s> <code>código</code></p>"
    assert _roundtrip(html) == html


def test_color_span():
    html = '<p>Texto <span style="color:#ff0000">rojo</span> normal</p>'
    assert _roundtrip(html) == html


def test_empty():
    assert _roundtrip("") == ""
