"""Utility functions for markdown rendering."""
from typing import Any


def escape_html(value: str) -> str:
    """Escape HTML special characters."""
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def format_address(address: Any) -> str:
    """Format address dictionary or string into a single line."""
    if not address:
        return ""
    if isinstance(address, str):
        return address
    parts = [
        address.get("street"),
        address.get("city"),
        address.get("state"),
        address.get("zip"),
        address.get("country"),
    ]
    return ", ".join([part for part in parts if part])


def split_description(description: str) -> list[str]:
    """Split description into clean lines."""
    if not description:
        return []
    lines = []
    for line in description.splitlines():
        clean = line.strip().lstrip("-*").strip()
        if clean:
            lines.append(clean)
    return lines


def yaml_escape(value: str) -> str:
    """Escape YAML string values."""
    return value.replace('"', "'").strip()
