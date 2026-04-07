"""Tests for blueprint string encoding/decoding."""

from helmod_generator.encode import decode_blueprint_string, encode_blueprint_string


def test_roundtrip():
    """Encoding then decoding should return the original dict."""
    original = {
        "blueprint": {
            "entities": [
                {
                    "entity_number": 1,
                    "name": "assembling-machine-3",
                    "position": {"x": 3, "y": 3},
                    "recipe": "iron-gear-wheel",
                }
            ],
            "item": "blueprint",
            "version": 562949953945600,
        }
    }
    encoded = encode_blueprint_string(original)
    assert encoded.startswith("0")
    decoded = decode_blueprint_string(encoded)
    assert decoded == original


def test_version_byte():
    """Encoded string should start with version byte '0'."""
    bp = {"blueprint": {"entities": [], "item": "blueprint", "version": 0}}
    encoded = encode_blueprint_string(bp)
    assert encoded[0] == "0"


def test_decode_invalid_version():
    """Should raise on unexpected version byte."""
    import pytest
    with pytest.raises(ValueError, match="version byte"):
        decode_blueprint_string("1" + "eJwDAAAAAAE=")


def test_decode_empty():
    """Should raise on empty string."""
    import pytest
    with pytest.raises(ValueError, match="Empty"):
        decode_blueprint_string("")
