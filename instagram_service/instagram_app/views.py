from __future__ import annotations

from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from instagram_app.models import Post
from instagram_app.pagination import PostCursorPagination
from instagram_app.serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    PostSerializer,
)
from instagram_app.services.instagram_client import InstagramAPIError
from instagram_app.services.sync_service import CommentService, SyncService

class SyncView(APIView):

    def post(self, request: Request) -> Response:
        try:
            service = SyncService()
            posts = service.sync_posts()
        except InstagramAPIError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        serializer = PostSerializer(posts, many=True)
        return Response(
            {"synced": len(posts), "posts": serializer.data},
            status=status.HTTP_200_OK,
        )

class PostListView(generics.ListAPIView):

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostCursorPagination

class CommentCreateView(APIView):

    def post(self, request: Request, pk: int) -> Response:
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(
                {"error": f"Post with id={pk} not found in the database."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text: str = serializer.validated_data["text"]

        try:
            service = CommentService()
            comment = service.create_comment(post, text)
        except InstagramAPIError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )
