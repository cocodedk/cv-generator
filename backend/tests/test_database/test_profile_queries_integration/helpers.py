"""Helper functions for profile integration tests."""
from backend.database.connection import Neo4jConnection
import pytest


def skip_if_no_neo4j():
    """Skip test if Neo4j is not available."""
    if not Neo4jConnection.verify_connectivity():
        pytest.skip("Neo4j is not available for integration tests.")


def is_test_profile(profile: dict) -> bool:
    """Check if a profile is a test profile by verifying it has 'test' prefix in multiple fields.

    This function checks multiple fields to ensure it's definitely a test profile:
    - Name must start with "test"
    - Email must start with "test" (if present)
    - At least one additional field (phone, summary, or linkedin) must start with "test"
    """
    if not profile or not profile.get("personal_info"):
        return False

    personal_info = profile["personal_info"]

    # Check if name starts with "test"
    name = personal_info.get("name", "")
    if not name.startswith("test"):
        return False

    # Additional safety check: verify email also starts with "test"
    email = personal_info.get("email", "")
    if email and not email.startswith("test"):
        return False

    # Check at least one more field to be extra sure
    phone = personal_info.get("phone", "")
    summary = personal_info.get("summary", "")
    linkedin = personal_info.get("linkedin", "")

    additional_test_fields = [
        phone.startswith("test") if phone else False,
        summary.startswith("test") if summary else False,
        linkedin.startswith("test") if linkedin else False,
    ]

    # At least one additional field must start with "test"
    if not any(additional_test_fields):
        return False

    return True
