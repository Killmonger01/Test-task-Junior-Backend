from django.contrib import admin

from instagram_app.models import Comment, Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "instagram_id", "media_type", "timestamp")
    search_fields = ("instagram_id", "caption")

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "instagram_id", "post", "created_at")
    search_fields = ("instagram_id", "text")
