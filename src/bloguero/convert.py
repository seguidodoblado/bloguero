from __future__ import annotations

import html2text as _html2text


def html_to_markdown(html: str) -> str:
    """Convierte HTML a Markdown legible, solo para mostrar diffs (p. ej. en conflictos)."""
    converter = _html2text.HTML2Text()
    converter.body_width = 0
    return converter.handle(html).strip()
