"""Image processing utilities."""

import base64
import mimetypes
from pathlib import Path


def _maybe_inline_image(value: str) -> str:
    if value.startswith(("http://", "https://", "data:")):
        return value

    candidate = Path(value)
    if not candidate.is_file():
        return value

    mime, _ = mimetypes.guess_type(candidate.name)
    if mime is None:
        mime = "application/octet-stream"
    encoded = base64.b64encode(candidate.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"
