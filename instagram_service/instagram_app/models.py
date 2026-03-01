from django.db import models

class Post(models.Model):

    instagram_id = models.CharField(
        max_length=255, unique=True, db_index=True,
        help_text="Media ID from Instagram Graph API.",
    )
    caption = models.TextField(blank=True, default="")
    media_type = models.CharField(
        max_length=50, blank=True, default="",
        help_text="Type of media: IMAGE, VIDEO, CAROUSEL_ALBUM.",
    )
    media_url = models.URLField(max_length=1024, blank=True, default="")
    permalink = models.URLField(max_length=1024, blank=True, default="")
    timestamp = models.DateTimeField(
        null=True, blank=True,
        help_text="Original publish timestamp from Instagram.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"Post {self.instagram_id}"

class Comment(models.Model):

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments",
    )
    instagram_id = models.CharField(
        max_length=255, unique=True, db_index=True,
        help_text="Comment ID returned by Instagram Graph API.",
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Comment {self.instagram_id} on {self.post}"
