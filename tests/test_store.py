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


def test_prune_posts_removes_what_the_server_no_longer_has(tmp_path: Path):
    store = Store(tmp_path / "test.db")
    for post_id in ("1", "2", "3"):
        store.save_post(Post(id=post_id, blog_id="1", title=post_id, html="", status="draft"))
    store.save_post(Post(id="9", blog_id="2", title="otro blog", html="", status="draft"))

    gone = store.prune_posts("1", {"1", "3"})

    assert gone == ["2"]
    assert store.get_post("2") is None
    assert {post.id for post in store.list_posts("1")} == {"1", "3"}
    assert store.get_post("9") is not None   # no toca otros blogs
    store.close()


def test_prune_posts_keeps_posts_with_unsaved_local_changes(tmp_path: Path):
    store = Store(tmp_path / "test.db")
    store.save_post(Post(id="1", blog_id="1", title="x", html="", status="draft"))
    store.mark_dirty("1", title="editado", html="<p>sin guardar</p>", labels=[])

    gone = store.prune_posts("1", set())

    assert gone == []
    assert store.get_post("1").title == "editado"
    store.close()
