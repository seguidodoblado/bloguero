from bloguero.convert import html_to_markdown


def test_html_to_markdown_basic():
    assert html_to_markdown("<h1>Título</h1>") == "# Título"


def test_html_to_markdown_bold():
    assert html_to_markdown("<p>Hola <strong>mundo</strong></p>") == "Hola **mundo**"
