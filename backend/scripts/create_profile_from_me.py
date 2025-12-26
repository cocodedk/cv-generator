"""Create profile automatically from docs/me.md data.

This script creates a profile in the Neo4j database using data extracted from docs/me.md.
It includes personal information, work experience, education, and skills.

Usage:
    docker-compose exec app python backend/scripts/create_profile_from_me.py

The script will:
    1. Create a Profile node in Neo4j
    2. Create Person node with personal information
    3. Create Experience nodes with projects
    4. Create Education nodes
    5. Create Skill nodes with categories and levels

If a profile already exists, it will be updated with the new data.
"""
import sys

# Add app directory to path (Docker container has /app as working directory)
sys.path.insert(0, '/app')

from backend.scripts.create_profile_from_me import get_profile_data, create_profile


def create_profile_from_me_data():
    """Create profile using data from docs/me.md."""
    profile_data = get_profile_data()
    return create_profile(profile_data)


if __name__ == "__main__":
    try:
        success = create_profile_from_me_data()
        sys.exit(0 if success else 1)
    finally:
        from backend.database.connection import Neo4jConnection
        Neo4jConnection.close()
