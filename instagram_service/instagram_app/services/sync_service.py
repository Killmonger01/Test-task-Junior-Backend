from __future__ import annotations

from typing import Any

from django.utils.dateparse import parse_datetime

from instagram_app.models import Comment, Post
from instagram_app.services.instagram_client import InstagramClient

class SyncService:

    def __init__(self, client: InstagramClient | None = None) -> None:
        self.client = client or InstagramClient()

    def sync_posts(self) -> list[Post]:
        media_items: list[dict[str, Any]] = self.client.fetch_user_media()
        posts: list[Post] = []

        for item in media_items:
            post, _created = Post.objects.update_or_create(
                instagram_id=item["id"],
                defaults={
                    "caption": item.get("caption", ""),
                    "media_type": item.get("media_type", ""),
                    "media_url": item.get("media_url", ""),
                    "permalink": item.get("permalink", ""),
                    "timestamp": (
                        parse_datetime(item["timestamp"])
                        if item.get("timestamp")
                        else None
                    ),
                },
            )
            posts.append(post)

        return posts

class CommentService:

    def __init__(self, client: InstagramClient | None = None) -> None:
        self.client = client or InstagramClient()

    def create_comment(self, post: Post, text: str) -> Comment:
        result = self.client.post_comment(post.instagram_id, text)
        comment = Comment.objects.create(
            post=post,
            instagram_id=result["id"],
            text=text,
        )
        return comment
