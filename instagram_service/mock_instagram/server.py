from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

HOST = "0.0.0.0"
PORT = 8888

POSTS_PER_PAGE = 5

FAKE_POSTS: list[dict[str, Any]] = []
for i in range(1, 16):
    ts = datetime.now(timezone.utc) - timedelta(days=15 - i)
    FAKE_POSTS.append(
        {
            "id": f"1789500000000{i:04d}",
            "caption": f"Mock post #{i} — testing Instagram sync service 📸",
            "media_type": "IMAGE" if i % 3 != 0 else "CAROUSEL_ALBUM",
            "media_url": f"https://picsum.photos/seed/post{i}/1080/1080",
            "permalink": f"https://www.instagram.com/p/mock_post_{i}/",
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S+0000"),
        }
    )

COMMENTS: list[dict[str, Any]] = []

VALID_MEDIA_IDS = {p["id"] for p in FAKE_POSTS}

class InstagramMockHandler(BaseHTTPRequestHandler):

    def _send_json(self, data: dict[str, Any], status_code: int = 200) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_error(self, message: str, code: int = 400) -> None:
        self._send_json(
            {
                "error": {
                    "message": message,
                    "type": "OAuthException",
                    "code": code,
                }
            },
            status_code=code,
        )

    def _parse_path(self) -> tuple[str, dict[str, list[str]]]:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        return parsed.path, params

    def do_GET(self) -> None:
        path, params = self._parse_path()

        if path == "/me/media":
            self._handle_user_media(params)
        else:
            self._send_error("Endpoint not found", 404)

    def _handle_user_media(self, params: dict[str, list[str]]) -> None:
        after = int(params.get("after", ["0"])[0])
        page = FAKE_POSTS[after : after + POSTS_PER_PAGE]

        response: dict[str, Any] = {"data": page}

        next_cursor = after + POSTS_PER_PAGE
        if next_cursor < len(FAKE_POSTS):
            response["paging"] = {
                "cursors": {"after": str(next_cursor)},
                "next": (
                    f"http://{self.headers.get('Host', f'{HOST}:{PORT}')}"
                    f"/me/media?after={next_cursor}"
                    f"&access_token={params.get('access_token', [''])[0]}"
                ),
            }

        self._send_json(response)

    def do_POST(self) -> None:
        path, params = self._parse_path()

        parts = path.strip("/").split("/")
        if len(parts) == 2 and parts[1] == "comments":
            media_id = parts[0]
            self._handle_create_comment(media_id, params)
        else:
            self._send_error("Endpoint not found", 404)

    def _handle_create_comment(
        self, media_id: str, params: dict[str, list[str]]
    ) -> None:
        
        if media_id not in VALID_MEDIA_IDS:
            self._send_error(
                f"Media not found or not accessible: {media_id}", 400
            )
            return

        message = params.get("message", [None])[0]
        if not message:
            self._send_error("A 'message' parameter is required.", 400)
            return

        comment_id = f"1785889326{uuid.uuid4().hex[:7]}"
        comment = {
            "id": comment_id,
            "media_id": media_id,
            "text": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        COMMENTS.append(comment)

        self._send_json({"id": comment_id})

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[MockInstagram] {args[0] if args else ''}")

def run_server() -> None:
    server = HTTPServer((HOST, PORT), InstagramMockHandler)
    print(f"🟢 Mock Instagram API running at http://{HOST}:{PORT}")
    print(f"   → {len(FAKE_POSTS)} fake posts available")
    print(f"   → Pagination: {POSTS_PER_PAGE} posts per page")
    print()
    server.serve_forever()

if __name__ == "__main__":
    run_server()
