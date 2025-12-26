"""Field path building utilities for frontend mapping."""


def build_field_path(loc: tuple) -> str:
    """Build react-hook-form compatible field path (e.g., 'experience.0.description')."""
    if not loc:
        return ""

    path_parts = []
    for part in loc:
        if isinstance(part, int):
            if path_parts:
                path_parts.append(f".{part}")
            else:
                path_parts.append(str(part))
        elif path_parts:
            path_parts.append(f".{part}")
        else:
            path_parts.append(str(part))

    return "".join(path_parts)
