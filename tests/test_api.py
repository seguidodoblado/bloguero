"""list_posts con más de una página: la librería de Google rechaza `list_next` cuando `status` va repetido."""
import json

from googleapiclient.discovery import build_from_document
from googleapiclient.http import HttpMockSequence

from bloguero.api import BloggerClient

# Descripción mínima de la API (la real se descarga de Google): solo posts.list con los parámetros que usa la app.
_DOCUMENT = {
    "kind": "discovery#restDescription", "name": "blogger", "version": "v3",
    "rootUrl": "https://blogger.test/", "servicePath": "",
    "resources": {"posts": {"methods": {"list": {
        "id": "blogger.posts.list", "path": "blogs/{blogId}/posts", "httpMethod": "GET",
        "parameters": {
            "blogId": {"type": "string", "required": True, "location": "path"},
            "status": {"type": "string", "repeated": True, "location": "query"},
            "fetchBodies": {"type": "boolean", "location": "query"},
            "pageToken": {"type": "string", "location": "query"},
        },
        "parameterOrder": ["blogId"], "response": {"$ref": "PostList"},
    }}}},
    "schemas": {"PostList": {"id": "PostList", "type": "object", "properties": {
        "items": {"type": "array", "items": {"type": "object"}}, "nextPageToken": {"type": "string"}}}},
}


def _page(ids: list[str], next_token: str | None = None) -> tuple[dict, bytes]:
    data = {"items": [{"id": i, "title": f"Entrada {i}", "status": "DRAFT", "content": ""} for i in ids]}
    if next_token:
        data["nextPageToken"] = next_token
    return {"status": "200"}, json.dumps(data).encode()


def _client(*pages) -> BloggerClient:
    client = BloggerClient.__new__(BloggerClient)   # sin credenciales ni red
    client._service = build_from_document(_DOCUMENT, http=HttpMockSequence(list(pages)))
    return client


def test_list_posts_follows_every_page_even_with_several_statuses():
    client = _client(_page(["1", "2"], next_token="p2"), _page(["3", "4"], next_token="p3"), _page(["5"]))

    posts = client.list_posts("blog")

    assert [post.id for post in posts] == ["1", "2", "3", "4", "5"]


def test_list_posts_with_a_single_page():
    assert [post.id for post in _client(_page(["1"])).list_posts("blog")] == ["1"]
