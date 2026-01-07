"""Address formatting and normalization utilities."""

import re


def _normalize_address(address: str) -> str:
    """
    Normalize address string by cleaning HTML breaks and newlines.

    Converts all line breaks (HTML <br> tags and newlines) to single <br> tags,
    and removes excessive breaks.
    """
    if not address:
        return ""

    # Replace HTML breaks (case-insensitive, with optional closing tag)
    # Replace <br>, <br/>, <br />, <BR>, etc. with newline
    address = re.sub(r"<br\s*/?>", "\n", address, flags=re.IGNORECASE)

    # Normalize multiple newlines to single newline
    address = re.sub(r"\n+", "\n", address)

    # Strip leading/trailing whitespace
    address = address.strip()

    # Convert single newlines to <br> tags
    address = address.replace("\n", "<br>")

    return address


def _strip_html_breaks(text: str) -> str:
    """Strip HTML break tags from text and convert to newlines."""
    if not text:
        return ""
    # Replace HTML breaks with newlines
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    # Normalize multiple newlines
    text = re.sub(r"\n+", "\n", text)
    return text.strip()
