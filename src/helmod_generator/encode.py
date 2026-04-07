"""Encode and decode Factorio blueprint strings."""

import base64
import json
import zlib

VERSION_BYTE = "0"


def encode_blueprint_string(blueprint_dict: dict) -> str:
    """Encode a blueprint dict into a Factorio blueprint string.

    Format: version_byte + base64(zlib_compress(json))
    """
    json_bytes = json.dumps(blueprint_dict, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(json_bytes, 9)
    encoded = base64.b64encode(compressed).decode("ascii")
    return VERSION_BYTE + encoded


def decode_blueprint_string(blueprint_string: str) -> dict:
    """Decode a Factorio blueprint string into a dict.

    Strips the version byte, base64-decodes, zlib-decompresses, and parses JSON.
    """
    if not blueprint_string:
        raise ValueError("Empty blueprint string")
    version = blueprint_string[0]
    if version != VERSION_BYTE:
        raise ValueError(f"Unexpected version byte: {version!r}")
    compressed = base64.b64decode(blueprint_string[1:])
    json_bytes = zlib.decompress(compressed)
    return json.loads(json_bytes)
