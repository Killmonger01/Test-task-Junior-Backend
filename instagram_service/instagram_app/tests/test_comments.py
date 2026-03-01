from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from instagram_app.models import Comment, Post
from instagram_app.services.instagram_client import InstagramAPIError

class CommentCreateViewTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.post_obj = Post.objects.create(
            instagram_id="17895695668004550",
            caption="Test post",
            media_type="IMAGE",
            media_url="https://example.com/image.jpg",
            permalink="https://www.instagram.com/p/test/",
        )
        self.url = reverse("post-comment", kwargs={"pk": self.post_obj.pk})

    @patch("instagram_app.services.sync_service.InstagramClient")
    def test_create_comment_success(self, MockClientClass: type) -> None:
        mock_client = MockClientClass.return_value
        mock_client.post_comment.return_value = {"id": "17858893269000001"}

        response = self.client.post(self.url, {"text": "Nice photo!"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data["text"], "Nice photo!")
        self.assertEqual(response.data["instagram_id"], "17858893269000001")
        self.assertEqual(response.data["post"], self.post_obj.pk)

        self.assertTrue(
            Comment.objects.filter(instagram_id="17858893269000001").exists()
        )
        comment = Comment.objects.get(instagram_id="17858893269000001")
        self.assertEqual(comment.text, "Nice photo!")
        self.assertEqual(comment.post_id, self.post_obj.pk)

    def test_comment_post_not_found(self) -> None:
        url = reverse("post-comment", kwargs={"pk": 99999})
        response = self.client.post(url, {"text": "Hello"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("not found", response.data["error"].lower())
        self.assertEqual(Comment.objects.count(), 0)

    @patch("instagram_app.services.sync_service.InstagramClient")
    def test_comment_instagram_api_error(self, MockClientClass: type) -> None:
        mock_client = MockClientClass.return_value
        mock_client.post_comment.side_effect = InstagramAPIError(
            "Media not found or not accessible.", status_code=400
        )

        response = self.client.post(self.url, {"text": "Hello"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("not found", response.data["error"].lower())
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_empty_text_rejected(self) -> None:
        response = self.client.post(self.url, {"text": ""}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
