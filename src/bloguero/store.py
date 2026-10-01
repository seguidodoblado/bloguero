from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from bloguero.models import Blog, Post

CACHE_DIR = Path.home() / ".cache" / "bloguero"
DB_PATH = CACHE_DIR / "bloguero.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS blogs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    blog_id TEXT NOT NULL,
    title TEXT NOT NULL,
    labels TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL,
    html TEXT NOT NULL DEFAULT '',
    updated TEXT,
    dirty INTEGER NOT NULL DEFAULT 0
);
"""


class Store:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)

    def close(self) -> None:
        self._conn.close()

    def save_blogs(self, blogs: list[Blog]) -> None:
        self._conn.executemany(
            "INSERT INTO blogs (id, name, url) VALUES (?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET name=excluded.name, url=excluded.url",
            [(b.id, b.name, b.url) for b in blogs],
        )
        self._conn.commit()

    def list_blogs(self) -> list[Blog]:
        rows = self._conn.execute("SELECT * FROM blogs").fetchall()
        return [Blog(id=r["id"], name=r["name"], url=r["url"]) for r in rows]

    def save_post(self, post: Post) -> None:
        self._conn.execute(
            """
            INSERT INTO posts (id, blog_id, title, labels, status, html, updated, dirty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                blog_id=excluded.blog_id, title=excluded.title, labels=excluded.labels,
                status=excluded.status, html=excluded.html,
                updated=excluded.updated, dirty=excluded.dirty
            """,
            (
                post.id,
                post.blog_id,
                post.title,
                ",".join(post.labels),
                post.status,
                post.html,
                post.updated.isoformat() if post.updated else None,
                int(post.dirty),
            ),
        )
        self._conn.commit()

    def list_posts(self, blog_id: str, status: str | None = None) -> list[Post]:
        if status:
            rows = self._conn.execute(
                "SELECT * FROM posts WHERE blog_id = ? AND status = ?", (blog_id, status)
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM posts WHERE blog_id = ?", (blog_id,)
            ).fetchall()
        return [_post_from_row(r) for r in rows]

    def get_post(self, post_id: str) -> Post | None:
        row = self._conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        return _post_from_row(row) if row else None

    def delete_post(self, post_id: str) -> None:
        self._conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        self._conn.commit()

    def mark_dirty(self, post_id: str, title: str, html: str, labels: list[str]) -> None:
        """Guarda cambios locales de un borrador sin tocar el estado conocido del servidor."""
        self._conn.execute(
            """
            UPDATE posts SET title = ?, html = ?, labels = ?, dirty = 1
            WHERE id = ?
            """,
            (title, html, ",".join(labels), post_id),
        )
        self._conn.commit()


def _post_from_row(row: sqlite3.Row) -> Post:
    updated = datetime.fromisoformat(row["updated"]) if row["updated"] else None
    return Post(
        id=row["id"],
        blog_id=row["blog_id"],
        title=row["title"],
        labels=[l for l in row["labels"].split(",") if l],
        status=row["status"],
        html=row["html"],
        updated=updated,
        dirty=bool(row["dirty"]),
    )
