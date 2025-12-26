"""Personal information data."""
from typing import Dict, Any


def get_personal_info() -> Dict[str, Any]:
    """Get personal information data.

    Returns:
        Dictionary containing personal information
    """
    # Parse address from: "Magistervej 54 3. th, 2400 Copenhagen NV"
    # Street: "Magistervej 54 3. th"
    # City: "Copenhagen NV"
    # Zip: "2400"
    # Country: "Denmark"

    return {
        "name": "Babak Bandpey",
        "title": "Senior Freelance Software Engineer / Security & GRC Specialist",
        "email": "babak@cocode.dk",
        "phone": "+45 27 82 30 77",
        "address": {
            "street": "Magistervej 54 3. th",
            "city": "Copenhagen NV",
            "zip": "2400",
            "country": "Denmark"
        },
        "linkedin": "https://www.linkedin.com/in/babakbandpey/",
        "github": "https://github.com/cocodedk",
        "website": "https://cocode.dk",
        "summary": (
            "Senior systems architect who operationalizes security, compliance, and AI "
            "into measurable business outcomes. Conceived, architected, and built FITS, "
            "a production-grade AI-driven GRC platform used by real organizations. "
            "Expert in Python, Django, PostgreSQL, Neo4j, React, and AI/LLM integration. "
            "Hands-on experience with ISO 27001, CIS Controls, ISMS implementation, "
            "and large-scale compliance automation."
        )
    }
