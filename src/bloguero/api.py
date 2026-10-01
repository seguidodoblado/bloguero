from __future__ import annotations

import time
from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError

from bloguero.models import Blog, Post

_MAX_RETRIES = 3
_RETRYABLE_STATUSES = {429, 500, 502, 503, 504}


class BloggerClient:
    def __init__(self, credentials: Credentials) -> None:
        self._service: Resource = build("blogger", "v3", credentials=credentials)

    def list_my_blogs(self) -> list[Blog]:
        data = self._call(self._service.blogs().listByUser(userId="self"))
        return [
            Blog(id=b["id"], name=b["name"], url=b["url"])
            for b in data.get("items", [])
        ]

    def list_posts(self, blog_id: str, statuses: list[str] | None = None) -> list[Post]:
        statuses = statuses or ["live", "draft", "scheduled"]
        posts: list[Post] = []
        request = self._service.posts().list(
            blogId=blog_id,
            status=[s.upper() for s in statuses],
            fetchBodies=True,
        )
        while request is not None:
            data = self._call(request)
            posts.extend(_post_from_api(p, blog_id) for p in data.get("items", []))
            request = self._service.posts().list_next(request, data)
        return posts

    def get_post(self, blog_id: str, post_id: str) -> Post:
        data = self._call(
            self._service.posts().get(blogId=blog_id, postId=post_id, view="AUTHOR")
        )
        return _post_from_api(data, blog_id)

    def create_post(
        self, blog_id: str, title: str, html: str, is_draft: bool, labels: list[str] | None = None
    ) -> Post:
        body = {"title": title, "content": html}
        if labels:
            body["labels"] = labels
        data = self._call(
            self._service.posts().insert(blogId=blog_id, body=body, isDraft=is_draft)
        )
        return _post_from_api(data, blog_id)

    def update_post(
        self, blog_id: str, post_id: str, title: str, html: str, labels: list[str] | None = None
    ) -> Post:
        body = {"title": title, "content": html}
        if labels:
            body["labels"] = labels
        data = self._call(
            self._service.posts().update(blogId=blog_id, postId=post_id, body=body)
        )
        return _post_from_api(data, blog_id)

    def publish_post(
        self, blog_id: str, post_id: str, publish_date: datetime | None = None
    ) -> Post:
        params = {"blogId": blog_id, "postId": post_id}
        if publish_date is not None:
            params["publishDate"] = publish_date.isoformat()
        data = self._call(self._service.posts().publish(**params))
        return _post_from_api(data, blog_id)

    def revert_post(self, blog_id: str, post_id: str) -> Post:
        data = self._call(self._service.posts().revert(blogId=blog_id, postId=post_id))
        return _post_from_api(data, blog_id)

    def delete_post(self, blog_id: str, post_id: str) -> None:
        self._call(self._service.posts().delete(blogId=blog_id, postId=post_id))

    @staticmethod
    def _call(request):
        for attempt in range(_MAX_RETRIES + 1):
            try:
                return request.execute()
            except HttpError as exc:
                if exc.resp.status not in _RETRYABLE_STATUSES or attempt == _MAX_RETRIES:
                    raise
                time.sleep(2**attempt)


def _post_from_api(data: dict, blog_id: str) -> Post:
    return Post(
        id=data["id"],
        blog_id=blog_id,
        title=data.get("title", ""),
        html=data.get("content", ""),
        status=data.get("status", "live").lower(),
        labels=data.get("labels", []),
        updated=_parse_timestamp(data.get("updated")),
        published=_parse_timestamp(data.get("published")),
    )


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None
