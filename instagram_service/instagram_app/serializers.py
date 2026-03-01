from rest_framework import serializers

from instagram_app.models import Comment, Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "instagram_id",
            "caption",
            "media_type",
            "media_url",
            "permalink",
            "timestamp",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "post", "instagram_id", "text", "created_at"]
        read_only_fields = ["id", "instagram_id", "created_at"]

class CommentCreateSerializer(serializers.Serializer):

    text = serializers.CharField(max_length=2200)
