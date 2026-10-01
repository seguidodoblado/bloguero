from pathlib import Path

from bloguero.models import Blog, Post
from bloguero.store import Store


def test_save_and_list_blogs(tmp_path: Path):
    store = Store(tmp_path / "test.db")
    store.save_blogs([Blog(id="1", name="Mi blog", url="https://example.com")])

    blogs = store.list_blogs()

    assert len(blogs) == 1
    assert blogs[0].name == "Mi blog"
    store.close()


def test_save_and_get_post(tmp_path: Path):
    store = Store(tmp_path / "test.db")
    post = Post(
        id="1",
        blog_id="1",
        title="Hola",
        html="<p>Hola</p>",
        status="draft",
        labels=["a", "b"],
    )
    store.save_post(post)

    saved = store.get_post("1")

    assert saved is not None
    assert saved.title == "Hola"
    assert saved.labels == ["a", "b"]
    store.close()


def test_delete_post(tmp_path: Path):
    store = Store(tmp_path / "test.db")
    store.save_post(Post(id="1", blog_id="1", title="x", html="", status="draft"))

    store.delete_post("1")

    assert store.get_post("1") is None
    store.close()
