from __future__ import annotations

from typing import Any

import requests
from django.conf import settings


class InstagramAPIError(Exception):
    """Ошибка при взаимодействии с Instagram Graph API."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)


class InstagramClient:
    """HTTP-клиент для Instagram Graph API."""

    def __init__(
        self,
        access_token: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.access_token = access_token or settings.INSTAGRAM_ACCESS_TOKEN
        self.base_url = base_url or settings.INSTAGRAM_GRAPH_API_URL

    def _get(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """GET-запрос к API. Возвращает распарсенный JSON."""
        params = params or {}
        params["access_token"] = self.access_token
        response = requests.get(url, params=params, timeout=30)
        data: dict[str, Any] = response.json()

        if "error" in data:
            error_msg = data["error"].get("message", "Unknown Instagram API error")
            raise InstagramAPIError(error_msg, status_code=response.status_code)

        if not response.ok:
            raise InstagramAPIError(
                f"Instagram API returned status {response.status_code}",
                status_code=response.status_code,
            )
        return data

    def _post(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """POST-запрос к API. Возвращает распарсенный JSON."""
        params = params or {}
        params["access_token"] = self.access_token
        response = requests.post(url, params=params, timeout=30)
        data: dict[str, Any] = response.json()

        if "error" in data:
            error_msg = data["error"].get("message", "Unknown Instagram API error")
            raise InstagramAPIError(error_msg, status_code=response.status_code)

        if not response.ok:
            raise InstagramAPIError(
                f"Instagram API returned status {response.status_code}",
                status_code=response.status_code,
            )
        return data

    def fetch_user_media(self) -> list[dict[str, Any]]:
        """Получить все медиа пользователя. Автоматически обходит пагинацию через поле next."""
        url = f"{self.base_url}/me/media"
        params: dict[str, Any] | None = {
            "fields": "id,caption,media_type,media_url,permalink,timestamp",
        }
        all_media: list[dict[str, Any]] = []

        while url:
            data = self._get(url, params)
            all_media.extend(data.get("data", []))
            url = data.get("paging", {}).get("next")
            params = None

        return all_media

    def post_comment(self, media_instagram_id: str, text: str) -> dict[str, Any]:
        """Отправить комментарий к посту. Возвращает dict с id созданного комментария."""
        url = f"{self.base_url}/{media_instagram_id}/comments"
        return self._post(url, params={"message": text})