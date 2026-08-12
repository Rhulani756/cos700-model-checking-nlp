"""Render PlantUML source to SVG through a PlantUML render server.

The renderer makes an HTTP request to a PlantUML server. Set
``PLANTUML_SERVER_URL`` to choose the server, for example::

    PLANTUML_SERVER_URL=https://www.plantuml.com/plantuml

A private/self-hosted server can still be used when student source code or
counterexample values must not leave your infrastructure.
"""

from __future__ import annotations

import os

import httpx

from .exceptions import DiagramRenderError


DEFAULT_SERVER_URL = "https://www.plantuml.com/plantuml"
DEFAULT_TIMEOUT_SECONDS = 10.0
_MAX_ERROR_BODY_CHARS = 1000

_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
}


def encode_plantuml(source: str) -> str:
    """Encode PlantUML source using PlantUML's supported HEX URL format.

    PlantUML recognises hexadecimal URL data when it is prefixed with ``~h``.
    This avoids maintaining a custom Deflate/base64 implementation in this
    module. The trade-off is a longer URL, which is acceptable for the small
    execution-path diagrams produced by the NLP pipeline.
    """

    return "~h" + source.encode("utf-8").hex()


def _raise_for_render_error(response: httpx.Response) -> None:
    """Raise DiagramRenderError with useful server diagnostics."""

    if not response.is_error:
        return

    detail = response.text.strip()
    if len(detail) > _MAX_ERROR_BODY_CHARS:
        detail = detail[:_MAX_ERROR_BODY_CHARS].rstrip() + "..."

    if detail:
        raise DiagramRenderError(
            "PlantUML server returned HTTP %d: %s"
            % (response.status_code, detail)
        )

    raise DiagramRenderError(
        "PlantUML server returned HTTP %d with no response body."
        % response.status_code
    )


def _validate_svg(response: httpx.Response) -> str:
    """Return SVG text when the response contains valid SVG output."""

    _raise_for_render_error(response)

    svg = response.text
    if "<svg" not in svg.lower():
        raise DiagramRenderError(
            "PlantUML server did not return valid SVG output."
        )

    return svg


def render_svg_sync(
    plantuml_source: str,
    server_url: str = DEFAULT_SERVER_URL,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> str:
    encoded = encode_plantuml(plantuml_source)
    url = "%s/svg/%s" % (server_url.rstrip("/"), encoded)

    try:
        response = httpx.get(url, timeout=timeout, headers=_REQUEST_HEADERS)
    except httpx.HTTPError as error:
        raise DiagramRenderError(
            "PlantUML render request failed: %s" % error
        ) from error

    return _validate_svg(response)


async def render_svg_async(
    plantuml_source: str,
    server_url: str = DEFAULT_SERVER_URL,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> str:
    encoded = encode_plantuml(plantuml_source)
    url = "%s/svg/%s" % (server_url.rstrip("/"), encoded)

    try:
        async with httpx.AsyncClient(timeout=timeout, headers=_REQUEST_HEADERS) as client:
            response = await client.get(url)
    except httpx.HTTPError as error:
        raise DiagramRenderError(
            "PlantUML render request failed: %s" % error
        ) from error

    return _validate_svg(response)