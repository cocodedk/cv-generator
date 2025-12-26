"""Field name building utilities for error messages."""


def build_friendly_field_name(loc: tuple) -> str:  # noqa: C901
    """Convert field location to user-friendly name."""
    if not loc:
        return "Unknown field"

    field_labels = {
        "personal_info": {
            "name": "Full Name",
            "title": "Professional Title",
            "email": "Email",
            "phone": "Phone",
            "address": "Address",
            "linkedin": "LinkedIn",
            "github": "GitHub",
            "website": "Website",
            "summary": "Professional Summary",
        },
        "experience": {
            "title": "Job Title",
            "company": "Company",
            "start_date": "Start Date",
            "end_date": "End Date",
            "description": "Role Summary",
            "location": "Location",
        },
        "education": {
            "degree": "Degree",
            "institution": "Institution",
            "year": "Year",
            "field": "Field",
            "gpa": "GPA",
        },
        "skills": {
            "name": "Skill Name",
            "category": "Category",
            "level": "Level",
        },
    }

    parts = list(loc)
    if not parts:
        return "Unknown field"

    # Handle array indices
    result_parts = []
    i = 0
    while i < len(parts):
        part = parts[i]

        if isinstance(part, int):
            # Array index - get the previous part to know what array
            if i > 0 and isinstance(parts[i - 1], str):
                array_name = parts[i - 1]
                index_num = part + 1  # 1-based for user display

                if array_name == "experience":
                    result_parts.append(f"Experience {index_num}")
                elif array_name == "education":
                    result_parts.append(f"Education {index_num}")
                elif array_name == "skills":
                    result_parts.append(f"Skill {index_num}")
                else:
                    result_parts.append(f"{array_name}[{part}]")
            i += 1
        elif isinstance(part, str):
            # Field name
            if part in field_labels:
                # This is a section, not a field yet
                i += 1
                continue
            else:
                # This is a field name
                section = parts[i - 2] if i >= 2 and isinstance(parts[i - 2], str) else None
                if section and section in field_labels and part in field_labels[section]:
                    field_label = field_labels[section][part]
                    if result_parts:
                        result_parts.append(f" - {field_label}")
                    else:
                        result_parts.append(field_label)
                else:
                    result_parts.append(part.replace("_", " ").title())
                i += 1
        else:
            i += 1

    return "".join(result_parts) if result_parts else "Unknown field"
