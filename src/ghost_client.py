import base64
import hashlib
import hmac
import json
import mimetypes
import os
import sys
import time
import urllib.request
import urllib.error

from ghost_api import CMSBackend


def _require_env(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        print(f"FATAL: {key} not set", file=sys.stderr)
        sys.exit(1)
    return val


class GhostClient(CMSBackend):
    def __init__(self):
        self.url = _require_env("GHOST_URL").rstrip("/")
        api_key = _require_env("GHOST_ADMIN_API_KEY")
        parts = api_key.split(":")
        if len(parts) != 2:
            print("FATAL: GHOST_ADMIN_API_KEY must be id:secret", file=sys.stderr)
            sys.exit(1)
        self._key_id = parts[0]
        self._key_secret = bytes.fromhex(parts[1])
        self._base = f"{self.url}/ghost/api/admin"

    def _token(self) -> str:
        def b64url(data: bytes) -> str:
            return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

        now = int(time.time())
        header = b64url(json.dumps({"alg": "HS256", "typ": "JWT", "kid": self._key_id}).encode())
        payload = b64url(json.dumps({"iat": now, "exp": now + 300, "aud": "/admin/"}).encode())
        sig = hmac.new(self._key_secret, f"{header}.{payload}".encode(), hashlib.sha256).digest()
        return f"{header}.{payload}.{b64url(sig)}"

    def _headers(self) -> dict:
        return {
            "Authorization": f"Ghost {self._token()}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, data: str | None = None) -> dict:
        url = f"{self._base}{path}"
        req = urllib.request.Request(url, method=method, headers=self._headers())
        if data:
            req.data = data.encode()
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            print(f"FATAL: {method} {path} → {e.code}: {e.read().decode()}", file=sys.stderr)
            sys.exit(1)

    def create_post(self, title: str, html: str, status: str = "draft",
                    author_email: str = "", tags: list[str] | None = None) -> dict:
        post: dict = {
            "title": title,
            "html": html,
            "status": status,
        }
        if author_email:
            post["authors"] = [{"email": author_email}]
        if tags:
            post["tags"] = [{"name": t} for t in tags]
        data = self._request("POST", "/posts/?source=html",
                             data=json.dumps({"posts": [post]}))
        return data["posts"][0]

    def update_post(self, post_id: str, **kwargs) -> dict:
        current = self.get_post(post_id)
        update = {k: v for k, v in kwargs.items() if v is not None}
        update["updated_at"] = current["updated_at"]
        if "tags" in update and isinstance(update["tags"], list):
            update["tags"] = [{"name": t} for t in update["tags"]]
        data = self._request("PUT", f"/posts/{post_id}/?source=html",
                             data=json.dumps({"posts": [update]}))
        return data["posts"][0]

    def get_post(self, post_id: str) -> dict:
        data = self._request("GET", f"/posts/{post_id}/")
        return data["posts"][0]

    def list_posts(self, status: str = "all", limit: int = 15) -> list[dict]:
        params = f"?status={status}&limit={limit}&order=updated_at%20desc"
        data = self._request("GET", f"/posts/{params}")
        return data["posts"]

    def publish_post(self, post_id: str) -> dict:
        return self.update_post(post_id, status="published")

    def upload_image(self, file_path: str, ref: str = "") -> str:
        url = f"{self._base}/images/upload/"
        boundary = f"----ghost{int(time.time())}"
        fname = os.path.basename(file_path)
        ctype = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

        parts = []
        if ref:
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"ref\"\r\n\r\n{ref}\r\n".encode())
        with open(file_path, "rb") as f:
            file_data = f.read()
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{fname}\"\r\nContent-Type: {ctype}\r\n\r\n".encode() + file_data + b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode())
        body = b"".join(parts)

        req = urllib.request.Request(url, method="POST", data=body, headers={
            "Authorization": f"Ghost {self._token()}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        })
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())["images"][0]["url"]
        except urllib.error.HTTPError as e:
            print(f"FATAL: image upload → {e.code}: {e.read().decode()}", file=sys.stderr)
            sys.exit(1)


def _cli():
    if len(sys.argv) < 2:
        print("Usage: ghost_client.py <command> [args]")
        print("Commands: create-draft, create-post, publish, list, get, upload-image")
        sys.exit(1)

    client = GhostClient()
    cmd = sys.argv[1]

    if cmd == "create-draft":
        if len(sys.argv) < 4:
            print("Usage: ghost_client.py create-draft <title> <html> [author_email] [tags]")
            sys.exit(1)
        title, html = sys.argv[2], sys.argv[3]
        author = sys.argv[4] if len(sys.argv) > 4 else ""
        tags = sys.argv[5].split(",") if len(sys.argv) > 5 else None
        post = client.create_post(title, html, status="draft",
                                  author_email=author, tags=tags)
        print(json.dumps({"id": post["id"], "title": post["title"],
                          "status": post["status"], "url": post["url"]}, indent=2))

    elif cmd == "create-post":
        if len(sys.argv) < 4:
            print("Usage: ghost_client.py create-post <title> <html> [author_email] [tags]")
            sys.exit(1)
        title, html = sys.argv[2], sys.argv[3]
        author = sys.argv[4] if len(sys.argv) > 4 else ""
        tags = sys.argv[5].split(",") if len(sys.argv) > 5 else None
        post = client.create_post(title, html, status="published",
                                  author_email=author, tags=tags)
        print(json.dumps({"id": post["id"], "title": post["title"],
                          "status": post["status"], "url": post["url"]}, indent=2))

    elif cmd == "publish":
        if len(sys.argv) < 3:
            print("Usage: ghost_client.py publish <post_id>")
            sys.exit(1)
        post = client.publish_post(sys.argv[2])
        print(json.dumps({"id": post["id"], "status": post["status"],
                          "url": post["url"]}, indent=2))

    elif cmd == "list":
        status = sys.argv[2] if len(sys.argv) > 2 else "all"
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 15
        posts = client.list_posts(status=status, limit=limit)
        for p in posts:
            print(f"{p['id']}  {p['status']:10s}  {p['title']}")

    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: ghost_client.py get <post_id>")
            sys.exit(1)
        post = client.get_post(sys.argv[2])
        print(json.dumps(post, indent=2, default=str))

    elif cmd == "upload-image":
        if len(sys.argv) < 3:
            print("Usage: ghost_client.py upload-image <file_path> [ref]")
            sys.exit(1)
        ref = sys.argv[3] if len(sys.argv) > 3 else ""
        url = client.upload_image(sys.argv[2], ref=ref)
        print(url)

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    _cli()
