"""Personal info scrambling utilities for public HTML output."""
from __future__ import annotations

import hashlib
import re
from typing import Any, Dict


SCRAMBLE_EXEMPT_FIELDS = {"linkedin", "github", "website"}


def _derive_offsets(key: str) -> tuple[int, int]:
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    offset = int.from_bytes(digest[:4], "big")
    return offset % 26, offset % 10


def _shift_alpha(char: str, offset: int) -> str:
    base = ord("A") if char.isupper() else ord("a")
    return chr((ord(char) - base + offset) % 26 + base)


def _shift_digit(char: str, offset: int) -> str:
    return chr((ord(char) - ord("0") + offset) % 10 + ord("0"))


def _transform_text(text: str, key: str, reverse: bool = False) -> str:
    alpha_offset, digit_offset = _derive_offsets(key)
    if reverse:
        alpha_offset = (-alpha_offset) % 26
        digit_offset = (-digit_offset) % 10
    output = []
    for char in text:
        if "a" <= char <= "z" or "A" <= char <= "Z":
            output.append(_shift_alpha(char, alpha_offset))
        elif "0" <= char <= "9":
            output.append(_shift_digit(char, digit_offset))
        else:
            output.append(char)
    return "".join(output)


def scramble_text(text: str, key: str) -> str:
    """Scramble plain text with deterministic rotation."""
    return _transform_text(text, key, reverse=False)


def scramble_html_text(text: str, key: str) -> str:
    """Scramble text while preserving HTML tags."""
    parts = re.split(r"(<[^>]+>)", text)
    scrambled = []
    for part in parts:
        if part.startswith("<") and part.endswith(">"):
            scrambled.append(part)
        else:
            scrambled.append(_transform_text(part, key, reverse=False))
    return "".join(scrambled)


def _scramble_address(value: Any, key: str) -> Any:
    """Scramble address field (dict or str)."""
    if isinstance(value, dict):
        return {
            part: scramble_text(str(part_value), key)
            for part, part_value in value.items()
            if part_value
        }
    if isinstance(value, str):
        return scramble_text(value, key)
    return value


def _scramble_field_value(field: str, value: Any, key: str) -> Any:
    """Scramble a single field value based on field type."""
    if field == "summary" and isinstance(value, str):
        return scramble_html_text(value, key)
    if field == "address":
        return _scramble_address(value, key)
    if field == "photo":
        return None
    if isinstance(value, str):
        return scramble_text(value, key)
    return value


def scramble_personal_info(personal_info: Dict[str, Any], key: str) -> Dict[str, Any]:
    """Scramble personal info fields except public links."""
    if not personal_info:
        return {}

    scrambled: Dict[str, Any] = {}
    for field, value in personal_info.items():
        if field in SCRAMBLE_EXEMPT_FIELDS:
            scrambled[field] = value
        elif value is None:
            scrambled[field] = None
        else:
            scrambled[field] = _scramble_field_value(field, value, key)

    return scrambled
