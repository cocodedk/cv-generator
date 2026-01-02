"""Utility functions for HTML rendering."""
import re
from typing import Any, List, Dict


def format_address(address: Any) -> str:
    """Format address dict or string into a single string."""
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


def is_list_item(line: str) -> bool:
    """Check if a line is a list item (bullet or numbered)."""
    stripped = line.strip()
    list_markers = ["-", "*", "•"]
    if any(stripped.startswith(marker) for marker in list_markers):
        return True
    if stripped and stripped[0].isdigit() and len(stripped) > 1:
        return stripped[1] in [".", ")"]
    return False


def count_list_items(lines: List[str]) -> int:
    """Count how many lines are list items."""
    return sum(1 for line in lines if is_list_item(line))


def clean_list_item(line: str) -> str:
    """Remove list markers and numbered prefixes from a line."""
    stripped = line.strip()
    list_markers = ["-", "*", "•"]
    for marker in list_markers:
        if stripped.startswith(marker):
            stripped = stripped[1:].strip()
            break
    if stripped and stripped[0].isdigit():
        stripped = re.sub(r"^\d+[.)]\s*", "", stripped)
    return stripped


def process_as_list(non_empty_lines: List[str]) -> List[str]:
    """Process lines as a list, cleaning markers."""
    items = []
    for line in non_empty_lines:
        cleaned = clean_list_item(line)
        if cleaned:
            items.append(cleaned)
    return items


def split_description(description: str) -> Dict[str, Any]:
    """
    Split description and detect format (list vs paragraph).
    Returns dict with 'format' and 'content' keys.
    """
    if not description:
        return {"format": "paragraph", "content": ""}

    lines = description.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]

    if not non_empty_lines:
        return {"format": "paragraph", "content": ""}

    # Check if it's a list: count lines starting with list markers
    list_count = count_list_items(non_empty_lines)
    is_list = list_count >= len(non_empty_lines) * 0.5 and len(non_empty_lines) > 1

    if is_list:
        items = process_as_list(non_empty_lines)
        return {"format": "list", "content": items}

    # Check for multiple paragraphs (double newlines)
    if "\n\n" in description:
        paragraphs = []
        for para in description.split("\n\n"):
            cleaned = para.strip().replace("\n", " ")
            if cleaned:
                paragraphs.append(cleaned)
        if len(paragraphs) > 1:
            return {"format": "paragraphs", "content": paragraphs}

    # Single paragraph: join all lines with spaces
    paragraph_text = " ".join(line.strip() for line in lines if line.strip())
    return {"format": "paragraph", "content": paragraph_text}
