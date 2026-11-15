"""Minimal HTTP application exposing a health-check endpoint."""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


def healthz() -> dict[str, str]:
    """Return the service health payload."""

    return {"status": "ok"}


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Handle requests for the application's health endpoint."""

    def do_GET(self) -> None:
        if self.path == "/":
            self._redirect_to_github()
            return

        if self.path != "/healthz":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        self._send_json(HTTPStatus.OK, healthz())

    def do_HEAD(self) -> None:
        if self.path == "/":
            self._redirect_to_github()
            return

        if self.path != "/healthz":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        self._send_json(HTTPStatus.OK, healthz(), include_body=False)

    def _redirect_to_github(self) -> None:
        self.send_response(HTTPStatus.FOUND)
        self.send_header(
            "Location",
            "https://github.com/jcmanlutac-com/jcmanlutac-com",
        )
        self.end_headers()

    def _send_json(
        self,
        status: HTTPStatus,
        payload: dict[str, Any],
        *,
        include_body: bool = True,
    ) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        """Keep the default access logging while satisfying type checkers."""

        super().log_message(format, *args)


def create_server() -> ThreadingHTTPServer:
    """Create the server using the configured host and port."""

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    return ThreadingHTTPServer((host, port), HealthCheckHandler)


if __name__ == "__main__":
    with create_server() as server:
        print(f"Listening on http://{server.server_address[0]}:{server.server_address[1]}")
        server.serve_forever()
