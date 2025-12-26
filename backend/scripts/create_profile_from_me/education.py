"""Education data."""
from typing import List, Dict, Any


def get_education_data() -> List[Dict[str, Any]]:
    """Get education data.

    Returns:
        List of education dictionaries
    """
    return [
        {
            "degree": "Datamatiker",
            "institution": "Niels Brock Copenhagen Business College",
            "field": "Computer Science",
            "year": "2000"
        },
        {
            "degree": "Advanced Diploma / Continuing Education in Cybersecurity",
            "institution": "Erhvervsakademi / EK",
            "field": "Cybersecurity and Information Security Management",
            "year": "2020"
        }
    ]
