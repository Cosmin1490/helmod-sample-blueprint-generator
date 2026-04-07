"""Decode Helmod export strings into Python dicts."""

import base64
import re
import zlib

from slpp import slpp as lua

VERSION_BYTE = "0"


def _strip_serpent_wrapper(lua_str: str) -> str:
    """Strip the `do return ... end` wrapper that serpent.dump adds in block mode."""
    stripped = lua_str.strip()
    # serpent.dump block mode: "do return { ... } end"
    match = re.match(r"^do\s+return\s+(.*)\s+end$", stripped, re.DOTALL)
    if match:
        return match.group(1).strip()
    return stripped


def _preprocess_lua(lua_str: str) -> str:
    """Preprocess Lua table string for slpp compatibility."""
    lua_str = _strip_serpent_wrapper(lua_str)
    # serpent.dump may use `nil` which slpp doesn't handle — remove nil assignments
    # e.g. ["key"] = nil, or key = nil,
    lua_str = re.sub(r'\[?"?\w+"?\]?\s*=\s*nil\s*,?', "", lua_str)
    return lua_str


def decode_helmod_string(export_string: str) -> dict:
    """Decode a Helmod export string into a Python dict.

    Helmod format: version_byte + base64(zlib(serpent.dump(lua_table)))
    """
    if not export_string:
        raise ValueError("Empty export string")

    # Strip version byte
    version = export_string[0]
    if version != VERSION_BYTE:
        raise ValueError(f"Unexpected version byte: {version!r}")

    # base64 decode -> zlib decompress -> Lua table string
    compressed = base64.b64decode(export_string[1:])
    lua_bytes = zlib.decompress(compressed)
    lua_str = lua_bytes.decode("utf-8")

    # Preprocess and parse the Lua table
    lua_str = _preprocess_lua(lua_str)
    result = lua.decode(lua_str)

    if result is None:
        raise ValueError("Failed to parse Lua table from Helmod export")

    return result
