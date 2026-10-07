"""Render PlantUML source to SVG through a PlantUML render server.

The renderer makes an HTTP request to a PlantUML server. Set
``PLANTUML_SERVER_URL`` to choose the server, for example::

    PLANTUML_SERVER_URL=https://www.plantuml.com/plantuml

PlantUML's standard Deflate URL encoding is used rather than HEX encoding
so larger execution-path diagrams produce substantially shorter URLs.

A private/self-hosted server can still be used when student source code or
counterexample values must not leave your infrastructure.
"""

from __future__ import annotations

import os
import zlib

import httpx

from .exceptions import DiagramRenderError


DEFAULT_SERVER_URL = "https://www.plantuml.com/plantuml"

DEFAULT_TIMEOUT_SECONDS = 10.0
_MAX_ERROR_BODY_CHARS = 1000


_PLANTUML_ALPHABET = (
    "0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "-_"
)


def encode_plantuml(source: str) -> str:
    """Encode PlantUML source using the standard Deflate URL format.

    PlantUML's normal URL representation consists of:

    1. UTF-8 encoding;
    2. raw Deflate compression;
    3. PlantUML's custom base64-like encoding.

    Unlike HEX encoding, this keeps URLs much shorter for large diagrams.
    """

    compressor = zlib.compressobj(
        level=9,
        method=zlib.DEFLATED,
        wbits=-15,
    )

    compressed = (
        compressor.compress(source.encode("utf-8"))
        + compressor.flush()
    )

    return _encode_bytes(compressed)


def _encode_bytes(data: bytes) -> str:
    """Encode compressed bytes using PlantUML's URL alphabet."""

    encoded_parts = []

    for index in range(0, len(data), 3):
        encoded_parts.append(
            _encode_chunk(data[index:index + 3])
        )

    return "".join(encoded_parts)


def _encode_chunk(chunk: bytes) -> str:
    """Encode up to three bytes into PlantUML's four-character format."""

    b1 = chunk[0]
    b2 = chunk[1] if len(chunk) > 1 else 0
    b3 = chunk[2] if len(chunk) > 2 else 0

    c1 = b1 >> 2
    c2 = ((b1 & 0x03) << 4) | (b2 >> 4)
    c3 = ((b2 & 0x0F) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F

    result = (
        _PLANTUML_ALPHABET[c1]
        + _PLANTUML_ALPHABET[c2]
    )

    if len(chunk) > 1:
        result += _PLANTUML_ALPHABET[c3]

    if len(chunk) > 2:
        result += _PLANTUML_ALPHABET[c4]

    return result


def _raise_for_render_error(response: httpx.Response) -> None:
    """Raise DiagramRenderError with useful server diagnostics."""

    if not response.is_error:
        return

    detail = response.text.strip()

    if len(detail) > _MAX_ERROR_BODY_CHARS:
        detail = (
            detail[:_MAX_ERROR_BODY_CHARS].rstrip()
            + "..."
        )

    if detail:
        raise DiagramRenderError(
            "PlantUML server returned HTTP %d: %s"
            % (
                response.status_code,
                detail,
            )
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
    """Render PlantUML source to an SVG string synchronously."""

    encoded = encode_plantuml(plantuml_source)

    url = "%s/svg/%s" % (
        server_url.rstrip("/"),
        encoded,
    )

    try:
        response = httpx.get(
            url,
            timeout=timeout,
        )
    except httpx.HTTPError as error:
        raise DiagramRenderError(
            "PlantUML render request failed: %s"
            % error
        ) from error

    return _validate_svg(response)


async def render_svg_async(
    plantuml_source: str,
    server_url: str = DEFAULT_SERVER_URL,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> str:
    """Render PlantUML source to an SVG string asynchronously."""

    encoded = encode_plantuml(plantuml_source)

    url = "%s/svg/%s" % (
        server_url.rstrip("/"),
        encoded,
    )

    try:
        async with httpx.AsyncClient(
            timeout=timeout
        ) as client:
            response = await client.get(url)

    except httpx.HTTPError as error:
        raise DiagramRenderError(
            "PlantUML render request failed: %s"
            % error
        ) from error

    return _validate_svg(response)