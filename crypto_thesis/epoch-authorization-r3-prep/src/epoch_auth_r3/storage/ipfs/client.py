from __future__ import annotations

import json
import secrets
import urllib.error
import urllib.parse
import urllib.request

from .exceptions import KuboUnavailableError, ReplicaVerificationError


class KuboRpcClient:
    def __init__(self, api_url: str, *, timeout_seconds: float = 5.0,
                 max_response_bytes: int = 32 * 1024 * 1024):
        parsed = urllib.parse.urlsplit(api_url)
        if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"}:
            raise ValueError("Kubo RPC must be loopback HTTP")
        self.api_url = api_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_response_bytes = max_response_bytes

    def _request(self, path: str, *, data: bytes | None = None,
                 headers: dict[str, str] | None = None) -> bytes:
        request = urllib.request.Request(
            self.api_url + path, data=data, headers=headers or {}, method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                length = response.headers.get("Content-Length")
                if length and int(length) > self.max_response_bytes:
                    raise ReplicaVerificationError("RESPONSE_TOO_LARGE")
                body = response.read(self.max_response_bytes + 1)
        except (OSError, urllib.error.URLError) as exc:
            raise KuboUnavailableError("KUBO_UNAVAILABLE") from exc
        if len(body) > self.max_response_bytes:
            raise ReplicaVerificationError("RESPONSE_TOO_LARGE")
        return body

    def add_bytes(self, data: bytes) -> str:
        boundary = "r3i8" + secrets.token_hex(12)
        body = (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
            "filename=\"object.bin\"\r\nContent-Type: application/octet-stream\r\n\r\n"
        ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
        query = urllib.parse.urlencode({
            "cid-version": "1", "hash": "sha2-256", "raw-leaves": "true",
            "chunker": "size-262144", "wrap-with-directory": "false",
            "pin": "true", "hidden": "false", "nocopy": "false",
        })
        raw = self._request(
            "/api/v0/add?" + query, data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        return json.loads(raw.decode().strip().splitlines()[-1])["Hash"]

    def cat(self, cid: str) -> bytes:
        return self._request("/api/v0/cat?" + urllib.parse.urlencode({"arg": cid}))

    def pin_ls(self, cid: str) -> bool:
        try:
            raw = self._request(
                "/api/v0/pin/ls?" + urllib.parse.urlencode({"arg": cid, "type": "recursive"})
            )
            return cid in json.loads(raw)["Keys"]
        except (KeyError, json.JSONDecodeError):
            return False

    def identity(self) -> dict:
        return json.loads(self._request("/api/v0/id").decode())
